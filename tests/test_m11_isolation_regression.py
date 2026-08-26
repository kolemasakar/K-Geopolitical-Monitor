import sqlite3
from datetime import datetime, timezone

from kgeopolitical_monitor.advanced_graph import (
    SUPPORTS,
    GraphEdge,
    GraphEdgeEvidence,
    SQLiteAdvancedGraphRepository,
)
from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.graph_projection import (
    CanonicalActorReference,
    project_actor_references,
    project_live_analysis_claim_references,
)
from kgeopolitical_monitor.intelligence_query import IntelligenceQuery
from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor, PARTLY_VERIFIED
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.region_language_coverage import RegionLanguageCoverageService
from kgeopolitical_monitor.relationship_lifecycle import RelationshipLifecycleManager
from kgeopolitical_monitor.runtime_storage import RuntimeStoragePolicy


NOW = datetime(2026, 8, 26, 15, 0, tzinfo=timezone.utc)


class StaticAdapter:
    def __init__(self, source_id, source_name, source_class, reliability, items):
        self.source_id = source_id
        self.source_name = source_name
        self.source_class = source_class
        self.reliability = reliability
        self._items = items

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=item["item_id"],
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title=item["title"],
                summary=item.get("summary", item["title"]),
                original_url=item["url"],
                collected_at=collected_at,
                metadata=item.get("metadata", {}),
                reliability=self.reliability,
            )
            for item in self._items
        ]


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Ukraine strategic monitor",
        "Ukraine security agreement",
        60,
        watch_id="watch-m11",
        created_at=NOW,
    )
    return runtime


def _collect_two_origins(runtime):
    adapters = [
        StaticAdapter(
            "official-m11",
            "Official M11",
            "Official sources",
            "official",
            [
                {
                    "item_id": "raw-official-m11",
                    "title": "Ukraine security agreement",
                    "url": "https://official.example/security-agreement",
                }
            ],
        ),
        StaticAdapter(
            "media-m11",
            "Media M11",
            "International media",
            "medium",
            [
                {
                    "item_id": "raw-media-m11",
                    "title": "Ukraine: security agreement",
                    "url": "https://media.example/security-agreement",
                }
            ],
        ),
    ]
    return LiveSourceCollector(runtime, adapters).collect("watch-m11", NOW)


def _claim_row(database_path, claim_id):
    with sqlite3.connect(database_path) as connection:
        return connection.execute(
            """
            SELECT claim_id, verification_status, confidence,
                   independent_origin_count, source_class_count, origins_json
            FROM live_analysis_claims
            WHERE claim_id = ?
            """,
            (claim_id,),
        ).fetchone()


def test_m8_m10_m11_cross_layer_processing_does_not_mutate_upstream_claim_truth(tmp_path):
    runtime = _runtime(tmp_path)
    collection = _collect_two_origins(runtime)
    processor = LiveEndToEndProcessor(runtime)
    analysis = processor.process_collection(collection.collection_id, processed_at=NOW)

    assert len(analysis.claims) == 1
    claim = analysis.claims[0]
    assert claim.verification_status == PARTLY_VERIFIED
    before = _claim_row(runtime.database_path, claim.claim_id)

    coverage = RegionLanguageCoverageService(runtime)
    coverage.register_region("UA", "Ukraine", region_group="Europe", created_at=NOW)
    coverage.register_language("uk", "Ukrainian", created_at=NOW)
    coverage.register_language("en", "English", created_at=NOW)
    coverage.configure_watch_scope(
        "watch-m11",
        [("UA", "uk"), ("UA", "en")],
        configured_at=NOW,
    )
    coverage.tag_observation(
        "watch-m11",
        "raw-official-m11",
        "UA",
        "uk",
        attribution_type="DECLARED",
        confidence=1.0,
        original_language=True,
        tagged_at=NOW,
    )
    coverage.tag_observation(
        "watch-m11",
        "raw-official-m11",
        "UA",
        "en",
        attribution_type="TRANSLATION",
        confidence=1.0,
        original_language=False,
        tagged_at=NOW,
    )

    graph = SQLiteAdvancedGraphRepository(runtime.database_path)
    claim_nodes = project_live_analysis_claim_references(
        runtime.database_path,
        graph,
        analysis_run_id=analysis.analysis_run_id,
        observed_at=NOW,
    )
    actor = project_actor_references(
        (
            CanonicalActorReference(
                actor_id="actor-ukraine",
                name="Ukraine",
                actor_type="COUNTRY",
            ),
        ),
        graph,
        observed_at=NOW,
    )[0]
    relationship = GraphEdge.between(
        actor.node_id,
        claim_nodes[0].node_id,
        "influences",
        "INFLUENCE",
        0.99,
        "Graph-layer analytical relationship only.",
        observed_at=NOW,
    )
    RelationshipLifecycleManager(graph).save_relationship(
        relationship,
        evidence=(
            GraphEdgeEvidence(
                relationship.edge_id,
                f"claim:{claim.claim_id}",
                SUPPORTS,
                NOW,
            ),
        ),
    )

    query = IntelligenceQuery(advanced_repository=graph)
    result = query.direct_neighborhood(actor.node_id, as_of=NOW)
    assert relationship.edge_id in result.explanation()["graph_ids"]
    assert f"claim:{claim.claim_id}" in result.explanation()["evidence_refs"]

    repeated = processor.process_collection(collection.collection_id, processed_at=NOW)
    after = _claim_row(runtime.database_path, claim.claim_id)

    assert repeated.claims[0].claim_id == claim.claim_id
    assert before == after
    assert repeated.claims[0].confidence == claim.confidence
    assert repeated.claims[0].independent_origins == claim.independent_origins
    assert repeated.claims[0].verification_status == claim.verification_status


def test_m11_runtime_storage_remains_inside_project_local_data_directory(tmp_path):
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    policy = RuntimeStoragePolicy(project_root)

    assert runtime.database_path == policy.resolve_database()
    assert runtime.database_path.parent == policy.data_root

    graph = SQLiteAdvancedGraphRepository(runtime.database_path)
    assert graph.database_path.resolve() == runtime.database_path.resolve()

    try:
        policy.resolve_database(tmp_path / "shared-runtime.db")
    except ValueError as exc:
        assert "project-local data directory" in str(exc)
    else:
        raise AssertionError("runtime storage outside project-local data must fail")


def test_m11_migration_restart_and_repeated_projection_are_idempotent(tmp_path):
    runtime = _runtime(tmp_path)
    initialize_database(str(runtime.database_path))
    initialize_database(str(runtime.database_path))

    graph = SQLiteAdvancedGraphRepository(runtime.database_path)
    actors = (
        CanonicalActorReference("actor-a", "Actor A", "COUNTRY"),
        CanonicalActorReference("actor-b", "Actor B", "ORGANIZATION"),
    )
    first = project_actor_references(actors, graph, observed_at=NOW)
    second = project_actor_references(actors, graph, observed_at=NOW)

    restarted = SQLiteAdvancedGraphRepository(runtime.database_path)
    loaded = restarted.get_node_by_canonical("ACTOR", "actor-a")

    with sqlite3.connect(runtime.database_path) as connection:
        migration_count = connection.execute(
            """
            SELECT COUNT(*) FROM schema_migrations
            WHERE version = '010_advanced_geopolitical_graph.sql'
            """
        ).fetchone()[0]
        actor_count = connection.execute(
            "SELECT COUNT(*) FROM graph_nodes WHERE canonical_ref_type = 'ACTOR'"
        ).fetchone()[0]

    assert tuple(item.node_id for item in first) == tuple(item.node_id for item in second)
    assert loaded is not None
    assert loaded.node_id == first[0].node_id
    assert migration_count == 1
    assert actor_count == 2


def test_m11_graph_stack_requires_no_external_graph_provider(tmp_path):
    runtime = _runtime(tmp_path)
    graph = SQLiteAdvancedGraphRepository(runtime.database_path)
    actor = project_actor_references(
        (CanonicalActorReference("actor-local", "Local Actor", "COUNTRY"),),
        graph,
        observed_at=NOW,
    )[0]

    restarted = SQLiteAdvancedGraphRepository(runtime.database_path)
    query = IntelligenceQuery(advanced_repository=restarted)
    result = query.direct_neighborhood(actor.node_id, as_of=NOW)

    assert result.nodes[0]["canonical_ref_id"] == "actor-local"
    assert result.edges == ()
    assert restarted.database_path.resolve() == runtime.database_path.resolve()
