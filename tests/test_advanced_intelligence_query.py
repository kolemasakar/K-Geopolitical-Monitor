from datetime import datetime, timedelta, timezone

from kgeopolitical_monitor.advanced_graph import (
    INVALIDATED,
    SUPPORTS,
    GraphEdge,
    GraphEdgeEvidence,
    GraphNode,
    SQLiteAdvancedGraphRepository,
)
from kgeopolitical_monitor.intelligence_query import IntelligenceQuery
from kgeopolitical_monitor.relationship_lifecycle import RelationshipLifecycleManager


T0 = datetime(2026, 8, 26, 14, 0, tzinfo=timezone.utc)


def _node(repo, ref_type, ref_id, kind, label):
    node = GraphNode.from_canonical(
        ref_type,
        ref_id,
        kind,
        label,
        created_at=T0,
    )
    repo.save_node(node)
    return node


def _edge(repo, source, target, relation_type, relation_class, confidence=0.7):
    edge = GraphEdge.between(
        source.node_id,
        target.node_id,
        relation_type,
        relation_class,
        confidence,
        f"{relation_type} explanation.",
        observed_at=T0,
        valid_from=T0,
    )
    RelationshipLifecycleManager(repo).save_relationship(
        edge,
        evidence=(
            GraphEdgeEvidence(
                edge.edge_id,
                f"finding:{relation_type}",
                SUPPORTS,
                T0,
            ),
        ),
    )
    return edge


def test_direct_neighborhood_is_explainable_with_canonical_and_evidence_refs(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    ukraine = _node(repo, "ACTOR", "ukraine", "ACTOR", "Ukraine")
    eu = _node(repo, "ACTOR", "eu", "ACTOR", "European Union")
    edge = _edge(repo, ukraine, eu, "cooperates_with", "POLITICAL")

    query = IntelligenceQuery(advanced_repository=repo)
    result = query.direct_neighborhood(ukraine.node_id, as_of=T0 + timedelta(minutes=1))
    explanation = result.explanation()

    assert result.query_type == "DIRECT_NEIGHBORHOOD"
    assert {item["canonical_ref_id"] for item in result.nodes} == {"ukraine", "eu"}
    assert [item["edge_id"] for item in result.edges] == [edge.edge_id]
    assert explanation["canonical_refs"] == ["ACTOR:eu", "ACTOR:ukraine"]
    assert explanation["evidence_refs"] == ["finding:cooperates_with"]
    assert edge.edge_id in explanation["graph_ids"]


def test_multi_hop_paths_are_bounded_and_exclude_invalidated_edges(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    manager = RelationshipLifecycleManager(repo)
    a = _node(repo, "ACTOR", "a", "ACTOR", "A")
    b = _node(repo, "ACTOR", "b", "ACTOR", "B")
    c = _node(repo, "ACTOR", "c", "ACTOR", "C")
    d = _node(repo, "ACTOR", "d", "ACTOR", "D")
    ab = _edge(repo, a, b, "supports", "POLITICAL")
    bc = _edge(repo, b, c, "coordinates", "POLITICAL")
    cd = _edge(repo, c, d, "supports", "POLITICAL")
    ad = _edge(repo, a, d, "temporary_link", "POLITICAL")
    manager.transition(
        ad.edge_id,
        status=INVALIDATED,
        observed_at=T0 + timedelta(minutes=10),
        explanation="Invalidated direct shortcut.",
    )

    query = IntelligenceQuery(advanced_repository=repo)
    result = query.multi_hop_paths(
        a.node_id,
        d.node_id,
        max_depth=3,
        as_of=T0 + timedelta(minutes=20),
    )

    assert result.paths == (
        {
            "node_ids": (a.node_id, b.node_id, c.node_id, d.node_id),
            "edge_ids": (ab.edge_id, bc.edge_id, cd.edge_id),
            "depth": 3,
        },
    )
    assert {item["edge_id"] for item in result.edges} == {ab.edge_id, bc.edge_id, cd.edge_id}
    assert ad.edge_id not in result.explanation()["graph_ids"]


def test_actor_relationships_support_current_and_historical_state(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    manager = RelationshipLifecycleManager(repo)
    a = _node(repo, "ACTOR", "a", "ACTOR", "A")
    b = _node(repo, "ACTOR", "b", "ACTOR", "B")
    edge = _edge(repo, a, b, "alliance", "POLITICAL")
    manager.transition(
        edge.edge_id,
        status=INVALIDATED,
        observed_at=T0 + timedelta(hours=1),
        explanation="Alliance no longer valid.",
    )

    query = IntelligenceQuery(advanced_repository=repo)
    current = query.actor_relationships(
        "a",
        "b",
        as_of=T0 + timedelta(hours=2),
    )
    historical = query.actor_relationships(
        "a",
        "b",
        as_of=T0 + timedelta(hours=2),
        include_historical=True,
    )
    before = query.relation_state(edge.edge_id, at=T0 + timedelta(minutes=30))
    after = query.relation_state(edge.edge_id, at=T0 + timedelta(hours=2))

    assert current.edges == ()
    assert historical.edges[0]["status"] == INVALIDATED
    assert before.edges[0]["status"] == "ACTIVE"
    assert after.edges[0]["status"] == INVALIDATED


def test_actor_events_returns_only_participation_edges_to_event_nodes(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    actor = _node(repo, "ACTOR", "actor-a", "ACTOR", "Actor A")
    event = _node(repo, "EVENT", "event-1", "EVENT", "Summit")
    other_actor = _node(repo, "ACTOR", "actor-b", "ACTOR", "Actor B")
    participation = _edge(repo, actor, event, "participates_in", "PARTICIPATION")
    _edge(repo, actor, other_actor, "supports", "POLITICAL")

    query = IntelligenceQuery(advanced_repository=repo)
    result = query.actor_events("actor-a", as_of=T0 + timedelta(minutes=1))

    assert {item["canonical_ref_id"] for item in result.nodes} == {"actor-a", "event-1"}
    assert [item["edge_id"] for item in result.edges] == [participation.edge_id]
    assert result.edges[0]["relation_class"] == "PARTICIPATION"


def test_advanced_causal_paths_are_cycle_safe_and_explainable(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    a = _node(repo, "ACTOR", "a", "ACTOR", "A")
    b = _node(repo, "EVENT", "b", "EVENT", "B")
    c = _node(repo, "EVENT", "c", "EVENT", "C")
    ab = _edge(repo, a, b, "causes", "CAUSAL")
    bc = _edge(repo, b, c, "influences", "INFLUENCE")
    _edge(repo, c, a, "feeds_back", "CAUSAL")

    query = IntelligenceQuery(advanced_repository=repo)
    result = query.advanced_causal_paths(
        a.node_id,
        max_depth=3,
        as_of=T0 + timedelta(minutes=1),
    )

    assert [item["depth"] for item in result.paths] == [1, 2]
    assert result.paths[0]["edge_ids"] == (ab.edge_id,)
    assert result.paths[1]["edge_ids"] == (ab.edge_id, bc.edge_id)
    assert all(a.node_id not in item["node_ids"][1:] for item in result.paths)
    assert set(result.explanation()["evidence_refs"]) == {
        "finding:causes",
        "finding:influences",
    }


def test_advanced_methods_require_explicit_durable_backend():
    query = IntelligenceQuery()
    try:
        query.direct_neighborhood("missing", as_of=T0)
    except ValueError as exc:
        assert "advanced graph backend" in str(exc)
    else:
        raise AssertionError("advanced query must require an explicit durable backend")
