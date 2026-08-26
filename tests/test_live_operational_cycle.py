from datetime import datetime, timedelta, timezone
import sqlite3

from kgeopolitical_monitor.live_end_to_end import LiveAnalysisResult
from kgeopolitical_monitor.live_operational_cycle import LiveOperationalCycle
from kgeopolitical_monitor.live_sources import SourceCollectionReport
from kgeopolitical_monitor.operational_monitoring import (
    COMPLETED,
    FAILED,
    OperationalMonitoringRuntime,
)


NOW = datetime(2026, 8, 26, 21, 0, tzinfo=timezone.utc)


def _runtime_with_watch(tmp_path, cadence_minutes=60):
    runtime = OperationalMonitoringRuntime(tmp_path)
    runtime.create_watch(
        "Live watch",
        "Ukraine",
        cadence_minutes,
        watch_id="watch-live",
        created_at=NOW - timedelta(hours=1),
    )
    return runtime


def _collection(*, status, item_count, failures=(), success_count=1, failure_count=0):
    return SourceCollectionReport(
        collection_id="collection-1",
        watch_id="watch-live",
        status=status,
        item_count=item_count,
        source_success_count=success_count,
        source_failure_count=failure_count,
        failures=tuple(failures),
        started_at=NOW,
        completed_at=NOW,
    )


class StaticCollector:
    def __init__(self, report=None, error=None):
        self.report = report
        self.error = error
        self.calls = []

    def collect(self, watch_id, now):
        self.calls.append((watch_id, now))
        if self.error is not None:
            raise self.error
        return self.report


class RuntimeProcessor:
    def __init__(self, runtime, mode="success", result_count=2):
        self.runtime = runtime
        self.mode = mode
        self.result_count = result_count
        self.calls = []

    def process_collection(self, collection_id, *, processed_at):
        self.calls.append((collection_id, processed_at))
        if self.mode == "fail-before-run":
            raise RuntimeError("processor failed before run")

        run = self.runtime.start_run("watch-live", started_at=processed_at)
        if self.mode == "fail-after-run":
            self.runtime.fail_run(run.run_id, "processor failed", completed_at=processed_at)
            raise RuntimeError("processor failed after run")

        self.runtime.complete_run(
            run.run_id,
            result_count=self.result_count,
            completed_at=processed_at,
        )
        return LiveAnalysisResult(
            analysis_run_id="analysis-1",
            collection_id=collection_id,
            watch_id="watch-live",
            monitoring_run_id=run.run_id,
            claims=(),
            findings=(),
        )


def test_all_source_failure_creates_failed_monitoring_run_and_respects_cadence(tmp_path):
    runtime = _runtime_with_watch(tmp_path)
    collector = StaticCollector(
        _collection(
            status="FAILED",
            item_count=0,
            success_count=0,
            failure_count=2,
            failures=(
                {"source_id": "source-a", "error": "network"},
                {"source_id": "source-b", "error": "timeout"},
            ),
        )
    )
    processor = RuntimeProcessor(runtime)

    executions = LiveOperationalCycle(runtime, collector, processor).execute_due(NOW)

    assert len(executions) == 1
    assert executions[0].status == FAILED
    assert "source-a: network" in executions[0].error
    assert processor.calls == []
    assert runtime.due_watches(NOW + timedelta(minutes=59)) == []
    assert [watch.watch_id for watch in runtime.due_watches(NOW + timedelta(minutes=60))] == [
        "watch-live"
    ]


def test_successful_zero_item_collection_is_completed_not_failed(tmp_path):
    runtime = _runtime_with_watch(tmp_path)
    collector = StaticCollector(_collection(status="COMPLETED", item_count=0))
    processor = RuntimeProcessor(runtime)

    executions = LiveOperationalCycle(runtime, collector, processor).execute_due(NOW)

    assert len(executions) == 1
    assert executions[0].status == COMPLETED
    assert executions[0].result_count == 0
    assert executions[0].error is None
    assert processor.calls == []
    assert runtime.due_watches(NOW + timedelta(minutes=1)) == []


def test_usable_collection_reuses_m8_owned_monitoring_run(tmp_path):
    runtime = _runtime_with_watch(tmp_path)
    collector = StaticCollector(_collection(status="PARTIAL", item_count=3, failure_count=1))
    processor = RuntimeProcessor(runtime, result_count=2)

    executions = LiveOperationalCycle(runtime, collector, processor).execute_due(NOW)

    assert len(executions) == 1
    assert executions[0].status == COMPLETED
    assert executions[0].result_count == 2
    assert processor.calls == [("collection-1", NOW)]
    latest = runtime.repository.latest_run("watch-live")
    assert latest is not None
    assert executions[0].run_id == latest.run_id


def test_processing_failure_before_m8_run_gets_fallback_failed_run(tmp_path):
    runtime = _runtime_with_watch(tmp_path)
    collector = StaticCollector(_collection(status="COMPLETED", item_count=1))
    processor = RuntimeProcessor(runtime, mode="fail-before-run")

    executions = LiveOperationalCycle(runtime, collector, processor).execute_due(NOW)

    assert len(executions) == 1
    assert executions[0].status == FAILED
    assert "processor failed before run" in executions[0].error
    assert runtime.due_watches(NOW + timedelta(minutes=1)) == []


def test_processing_failure_after_m8_failed_run_does_not_duplicate_run(tmp_path):
    runtime = _runtime_with_watch(tmp_path)
    collector = StaticCollector(_collection(status="COMPLETED", item_count=1))
    processor = RuntimeProcessor(runtime, mode="fail-after-run")

    executions = LiveOperationalCycle(runtime, collector, processor).execute_due(NOW)

    assert len(executions) == 1
    assert executions[0].status == FAILED
    with sqlite3.connect(runtime.database_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM monitoring_runs WHERE watch_id = ?",
            ("watch-live",),
        ).fetchone()[0]
    assert count == 1


def test_collector_exception_is_persisted_as_failed_watch_attempt(tmp_path):
    runtime = _runtime_with_watch(tmp_path)
    collector = StaticCollector(error=RuntimeError("transport exploded"))
    processor = RuntimeProcessor(runtime)

    executions = LiveOperationalCycle(runtime, collector, processor).execute_due(NOW)

    assert len(executions) == 1
    assert executions[0].status == FAILED
    assert executions[0].error == "live collection exception: transport exploded"
    assert runtime.repository.latest_run("watch-live").status == FAILED
