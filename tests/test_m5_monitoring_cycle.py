from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.monitoring_cycle import MonitoringCycle
from kgeopolitical_monitor.operational_monitoring import FAILED, OperationalMonitoringRuntime
from kgeopolitical_monitor.operational_output import FindingDraft


class SelectiveProcessor:
    def __init__(self, failing_watch_ids=None):
        self.failing_watch_ids = set(failing_watch_ids or [])

    def process(self, watch):
        if watch.watch_id in self.failing_watch_ids:
            raise RuntimeError(f"processing failed for {watch.watch_id}")
        return [
            FindingDraft(
                title=f"High priority {watch.watch_id}",
                summary="Primary monitored development",
                importance=0.9,
                confidence=0.8,
                evidence_refs=(f"evidence:{watch.watch_id}:1",),
                explanation="Supported by the stored project-local evidence reference.",
            ),
            FindingDraft(
                title=f"Secondary {watch.watch_id}",
                summary="Secondary monitored development",
                importance=0.5,
                confidence=0.95,
                evidence_refs=(f"evidence:{watch.watch_id}:2",),
                explanation="Lower importance but independently traceable.",
            ),
        ]


class FailOnceProcessor:
    def __init__(self):
        self.calls = 0

    def process(self, watch):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary processing failure")
        return [
            FindingDraft(
                title="Recovered finding",
                summary="Monitoring succeeded after a previous failed run.",
                importance=0.7,
                confidence=0.7,
                evidence_refs=("evidence:recovered",),
                explanation="The retry produced a traceable project-local result.",
            )
        ]


def _create_runtime_with_watches(tmp_path, t0):
    project_root = tmp_path / "project"
    project_root.mkdir()
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "A watch",
        "actor A",
        60,
        watch_id="watch-a",
        created_at=t0,
    )
    runtime.create_watch(
        "B watch",
        "actor B",
        60,
        watch_id="watch-b",
        created_at=t0,
    )
    return runtime


def test_monitoring_cycle_isolates_watch_failure_and_persists_ranked_findings(tmp_path):
    t0 = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    runtime = _create_runtime_with_watches(tmp_path, t0)
    cycle = MonitoringCycle(runtime, SelectiveProcessor({"watch-a"}))

    executions = cycle.execute_due(t0)

    assert len(executions) == 2
    by_watch = {execution.watch_id: execution for execution in executions}
    assert by_watch["watch-a"].status == FAILED
    assert by_watch["watch-a"].error == "processing failed for watch-a"
    assert by_watch["watch-b"].status == "COMPLETED"
    assert by_watch["watch-b"].result_count == 2

    findings = cycle.ranked_findings(watch_id="watch-b")
    assert [finding.importance for finding in findings] == [0.9, 0.5]
    assert findings[0].run_id == by_watch["watch-b"].run_id
    assert findings[0].evidence_refs == ("evidence:watch-b:1",)
    assert findings[0].explanation


def test_monitoring_cycle_is_deterministic_within_cadence_window(tmp_path):
    t0 = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    runtime = _create_runtime_with_watches(tmp_path, t0)
    cycle = MonitoringCycle(runtime, SelectiveProcessor())

    first = cycle.execute_due(t0)
    repeated = cycle.execute_due(t0)
    before_due = cycle.execute_due(t0 + timedelta(minutes=59))

    assert len(first) == 2
    assert repeated == []
    assert before_due == []


def test_monitoring_cycle_tracks_retry_after_failure(tmp_path):
    t0 = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    project_root = tmp_path / "project"
    project_root.mkdir()
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Retry watch",
        "retry subject",
        15,
        watch_id="watch-retry",
        created_at=t0,
    )
    processor = FailOnceProcessor()
    cycle = MonitoringCycle(runtime, processor)

    first = cycle.execute_due(t0)
    second = cycle.execute_due(t0 + timedelta(minutes=15))

    assert first[0].status == FAILED
    assert first[0].retry_count == 0
    assert second[0].status == "COMPLETED"
    assert second[0].retry_count == 1
    assert second[0].result_count == 1


def test_runtime_restart_recovers_interrupted_run_without_external_storage(tmp_path):
    t0 = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    project_root = tmp_path / "project"
    project_root.mkdir()
    runtime = OperationalMonitoringRuntime(project_root)
    watch = runtime.create_watch(
        "Recovery watch",
        "recovery subject",
        30,
        watch_id="watch-recovery",
        created_at=t0,
    )
    runtime.start_run(watch.watch_id, run_id="run-interrupted", started_at=t0)

    restarted = OperationalMonitoringRuntime(project_root)
    recovered_count = restarted.recover_interrupted_runs(t0 + timedelta(minutes=2))
    recovered = restarted.repository.latest_run(watch.watch_id)

    assert recovered_count == 1
    assert recovered is not None
    assert recovered.status == FAILED
    assert recovered.recovered is True
    assert recovered.error == "interrupted runtime recovered"
    assert restarted.due_watches(t0 + timedelta(minutes=29)) == []
    assert [item.watch_id for item in restarted.due_watches(t0 + timedelta(minutes=30))] == [
        watch.watch_id
    ]


def test_operational_finding_requires_traceability_and_explanation():
    with pytest.raises(ValueError, match="traceable evidence"):
        FindingDraft(
            title="No evidence",
            summary="Invalid operational finding",
            importance=0.5,
            confidence=0.5,
            evidence_refs=(),
            explanation="Explanation exists.",
        )

    with pytest.raises(ValueError, match="requires an explanation"):
        FindingDraft(
            title="No explanation",
            summary="Invalid operational finding",
            importance=0.5,
            confidence=0.5,
            evidence_refs=("evidence:1",),
            explanation=" ",
        )
