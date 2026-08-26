from datetime import datetime, timezone
import sqlite3

from kgeopolitical_monitor.live_sources import (
    LiveSourceCollector,
    LiveSourceItem,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


NOW = datetime(2026, 8, 26, 14, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-live",
        created_at=NOW,
    )
    return runtime


def test_live_source_item_identity_mismatch_fails_closed_before_ingestion(tmp_path):
    runtime = _runtime(tmp_path)

    class MismatchAdapter:
        source_id = "declared-source"
        source_name = "Declared Source"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return [
                LiveSourceItem(
                    item_id="mismatch-item",
                    source_id="other-source",
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title="Ukraine security update",
                    summary="Identity mismatch payload.",
                    original_url="https://example.org/mismatch",
                    collected_at=collected_at,
                )
            ]

    collector = LiveSourceCollector(runtime, [MismatchAdapter()])
    report = collector.collect("watch-live", NOW)

    assert report.status == "FAILED"
    assert report.item_count == 0
    assert report.source_success_count == 0
    assert report.source_failure_count == 1
    assert "live source item identity mismatch" in report.failures[0]["error"]
    assert "source_id expected='declared-source'" in report.failures[0]["error"]

    attempts = collector.audit.attempts(report.collection_id)
    assert len(attempts) == 1
    assert attempts[0].source_id == "declared-source"
    assert attempts[0].status == "FAILED"
    assert attempts[0].item_count == 0
    assert "identity mismatch" in attempts[0].error

    with sqlite3.connect(runtime.database_path) as connection:
        assert connection.execute(
            "SELECT 1 FROM raw_items WHERE id = 'mismatch-item'"
        ).fetchone() is None


def test_zero_item_success_is_persisted_as_successful_source_attempt(tmp_path):
    runtime = _runtime(tmp_path)

    class EmptySuccessAdapter:
        source_id = "empty-source"
        source_name = "Empty Source"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return []

    collector = LiveSourceCollector(runtime, [EmptySuccessAdapter()])
    report = collector.collect("watch-live", NOW)

    assert report.status == "COMPLETED"
    assert report.item_count == 0
    assert report.source_success_count == 1
    assert report.source_failure_count == 0

    attempts = collector.audit.attempts(report.collection_id)
    assert len(attempts) == 1
    attempt = attempts[0]
    assert attempt.source_id == "empty-source"
    assert attempt.status == "SUCCESS"
    assert attempt.item_count == 0
    assert attempt.error is None
    assert attempt.attempted_at == NOW
