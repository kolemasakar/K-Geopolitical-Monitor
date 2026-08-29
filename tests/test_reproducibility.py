from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.reproducibility import (
    ARTIFACT_HASH_BASIS,
    ReproducibilityInstrumentedCollector,
    ReproducibilityStore,
)


NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)
QUERY = 'Ukraine security "air defence" українська'


class GoodAdapter:
    source_id = "good-official"
    source_name = "Good Official"
    source_class = "Official sources"
    adapter_version = "test-adapter-1.2.3"

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id="repro-item-1",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Ukraine security air defence update",
                summary="Persisted parsed source payload.",
                original_url="https://official.example/repro-item-1",
                collected_at=collected_at,
                metadata={"message_id": "official-123", "language": "uk"},
                reliability="official",
            )
        ]


class FailingAdapter:
    source_id = "failed-source"
    source_name = "Failed Source"
    source_class = "Structured data"

    def fetch(self, watch, collected_at):
        raise RuntimeError("source unavailable")


class PhantomAdapter:
    source_id = "phantom-source"
    source_name = "Phantom Source"
    source_class = "Regional media"

    def fetch(self, watch, collected_at):
        return []


def _runtime(tmp_path, *, watch_id="watch-repro", query=QUERY):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Reproducibility watch",
        query,
        60,
        watch_id=watch_id,
        created_at=NOW,
    )
    return runtime


def _instrumented(runtime, adapters):
    return ReproducibilityInstrumentedCollector(
        LiveSourceCollector(runtime, list(adapters))
    )


def test_instrumented_collection_captures_exact_query_cutoff_adapter_and_hash(tmp_path):
    runtime = _runtime(tmp_path)
    collector = _instrumented(runtime, [GoodAdapter()])

    report = collector.collect("watch-repro", NOW)
    bundle = ReproducibilityStore(runtime.database_path).bundle_for_collection(
        report.collection_id
    )

    assert report.status == "COMPLETED"
    assert bundle is not None
    run = bundle["research_run"]
    assert run["status"] == "COMPLETED"
    assert run["collection_status"] == "COMPLETED"
    assert run["collection_id"] == report.collection_id
    assert run["exact_query_snapshot"] == QUERY
    assert run["research_cutoff"] == NOW.isoformat()
    assert run["instrumentation_version"] == "E6-1.0"

    assert len(bundle["query_executions"]) == 1
    query = bundle["query_executions"][0]
    assert query["source_id"] == GoodAdapter.source_id
    assert query["adapter_identity"].endswith(".GoodAdapter")
    assert query["adapter_version"] == "test-adapter-1.2.3"
    assert query["exact_query"] == QUERY
    assert query["request_locator"] is None
    assert query["request_locator_capture_state"] == "NOT_INSTRUMENTED"
    assert query["attempt_status"] == "SUCCESS"
    assert query["attempted_at"] == NOW.isoformat()

    assert len(bundle["artifacts"]) == 1
    artifact = bundle["artifacts"][0]
    assert artifact["raw_item_id"] == "repro-item-1"
    assert artifact["original_url"] == "https://official.example/repro-item-1"
    assert artifact["collected_at"] == NOW.isoformat()
    assert artifact["hash_algorithm"] == "SHA256"
    assert len(artifact["content_hash"]) == 64
    assert artifact["hash_basis"] == ARTIFACT_HASH_BASIS
    assert artifact["origin_id"] is None
    assert artifact["relation_class"] is None
    assert "remain null unless explicitly classified" in bundle["classification_note"]

    with sqlite3.connect(runtime.database_path) as connection:
        annotation_count = connection.execute(
            "SELECT COUNT(*) FROM research_provenance_annotations"
        ).fetchone()[0]
    assert annotation_count == 0


def test_repeated_persisted_artifact_produces_same_hash(tmp_path):
    runtime = _runtime(tmp_path)
    collector = _instrumented(runtime, [GoodAdapter()])
    store = ReproducibilityStore(runtime.database_path)

    first = collector.collect("watch-repro", NOW)
    second = collector.collect("watch-repro", NOW)

    first_hash = store.bundle_for_collection(first.collection_id)["artifacts"][0][
        "content_hash"
    ]
    second_hash = store.bundle_for_collection(second.collection_id)["artifacts"][0][
        "content_hash"
    ]
    assert first.collection_id != second.collection_id
    assert first_hash == second_hash


def test_source_collection_failure_is_distinct_from_successful_audit_capture(tmp_path):
    runtime = _runtime(tmp_path)
    collector = _instrumented(runtime, [FailingAdapter()])

    report = collector.collect("watch-repro", NOW)
    bundle = ReproducibilityStore(runtime.database_path).bundle_for_collection(
        report.collection_id
    )

    assert report.status == "FAILED"
    assert bundle is not None
    assert bundle["research_run"]["status"] == "COMPLETED"
    assert bundle["research_run"]["collection_status"] == "FAILED"
    assert bundle["research_run"]["error"] is None
    assert bundle["artifacts"] == []
    assert bundle["query_executions"][0]["attempt_status"] == "FAILED"
    assert bundle["query_executions"][0]["attempt_error"] == "source unavailable"


def test_uninstrumented_collector_does_not_fabricate_research_history(tmp_path):
    runtime = _runtime(tmp_path)
    base = LiveSourceCollector(runtime, [GoodAdapter()])

    report = base.collect("watch-repro", NOW)

    assert report.status == "COMPLETED"
    assert ReproducibilityStore(runtime.database_path).bundle_for_collection(
        report.collection_id
    ) is None
    with sqlite3.connect(runtime.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM research_audit_runs"
        ).fetchone()[0] == 0


def test_explicit_provenance_annotation_does_not_change_claim_verification(tmp_path):
    runtime = _runtime(tmp_path)
    collector = _instrumented(runtime, [GoodAdapter()])
    report = collector.collect("watch-repro", NOW)
    analysis = LiveEndToEndProcessor(runtime).process_collection(
        report.collection_id,
        processed_at=NOW,
    )
    assert len(analysis.claims) == 1

    with sqlite3.connect(runtime.database_path) as connection:
        before = connection.execute(
            """
            SELECT verification_status, independent_origin_count, origins_json
            FROM live_analysis_claims
            WHERE claim_id = ?
            """,
            (analysis.claims[0].claim_id,),
        ).fetchone()

    store = ReproducibilityStore(runtime.database_path)
    bundle = store.bundle_for_collection(report.collection_id)
    research_run_id = bundle["research_run"]["research_run_id"]
    store.annotate_provenance(
        research_run_id,
        "repro-item-1",
        origin_id="origin:official-statement-123",
        relation_class="CITATION",
        classification_basis="Explicit analyst classification from source text.",
        classified_at=NOW,
    )

    annotated = store.bundle_for_collection(report.collection_id)["artifacts"][0]
    assert annotated["origin_id"] == "origin:official-statement-123"
    assert annotated["relation_class"] == "CITATION"

    with sqlite3.connect(runtime.database_path) as connection:
        after = connection.execute(
            """
            SELECT verification_status, independent_origin_count, origins_json
            FROM live_analysis_claims
            WHERE claim_id = ?
            """,
            (analysis.claims[0].claim_id,),
        ).fetchone()
    assert after == before


def test_provenance_annotation_rejects_unsupported_relation_and_foreign_item(tmp_path):
    runtime = _runtime(tmp_path)
    collector = _instrumented(runtime, [GoodAdapter()])
    report = collector.collect("watch-repro", NOW)
    store = ReproducibilityStore(runtime.database_path)
    research_run_id = store.bundle_for_collection(report.collection_id)["research_run"][
        "research_run_id"
    ]

    with pytest.raises(ValueError, match="unsupported provenance"):
        store.annotate_provenance(
            research_run_id,
            "repro-item-1",
            origin_id="origin:test",
            relation_class="INDEPENDENT_CONFIRMATION",
            classification_basis="unsupported classification",
            classified_at=NOW,
        )

    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            ("foreign-source", "Foreign", "Official sources", "official"),
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES (?, ?, ?, ?, ?)",
            (
                "foreign-item",
                "foreign-source",
                "Foreign item",
                "Not part of audited collection",
                NOW.isoformat(),
            ),
        )

    with pytest.raises(ValueError, match="does not belong"):
        store.annotate_provenance(
            research_run_id,
            "foreign-item",
            origin_id="origin:foreign",
            relation_class="PRIMARY_ORIGIN",
            classification_basis="foreign item test",
            classified_at=NOW,
        )


def test_reproducibility_finalization_mismatch_fails_closed(tmp_path):
    runtime = _runtime(tmp_path)
    collector = _instrumented(runtime, [GoodAdapter()])
    collector.adapters.append(PhantomAdapter())

    with pytest.raises(RuntimeError, match="reproducibility finalization failed"):
        collector.collect("watch-repro", NOW)

    with sqlite3.connect(runtime.database_path) as connection:
        audit = connection.execute(
            """
            SELECT status, collection_status, collection_id, error
            FROM research_audit_runs
            """
        ).fetchone()
        query_count = connection.execute(
            "SELECT COUNT(*) FROM research_query_executions"
        ).fetchone()[0]
        hash_count = connection.execute(
            "SELECT COUNT(*) FROM research_artifact_hashes"
        ).fetchone()[0]

    assert audit[0] == "FAILED"
    assert audit[1] == "COMPLETED"
    assert audit[2] is not None
    assert "source collection attempts do not match" in audit[3]
    assert query_count == 0
    assert hash_count == 0


def test_research_cutoff_must_be_timezone_aware(tmp_path):
    runtime = _runtime(tmp_path)
    store = ReproducibilityStore(runtime.database_path)

    with pytest.raises(ValueError):
        store.start_live_collection(
            watch_id="watch-repro",
            exact_query=QUERY,
            research_cutoff=datetime(2026, 8, 29, 12, 0),
            started_at=NOW,
        )
