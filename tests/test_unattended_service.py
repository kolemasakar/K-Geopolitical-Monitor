from datetime import datetime, timezone

import pytest

from kgeopolitical_monitor.monitoring_cycle import CycleExecution
from kgeopolitical_monitor.unattended_service import UnattendedMonitoringService


NOW = datetime(2026, 8, 26, 20, 0, tzinfo=timezone.utc)


class FakeRuntime:
    def __init__(self, recovered_runs: int = 0):
        self.recovered_runs = recovered_runs
        self.recovery_calls = []

    def recover_interrupted_runs(self, recovered_at):
        self.recovery_calls.append(recovered_at)
        return self.recovered_runs


class FakeCycle:
    def __init__(self):
        self.calls = []

    def execute_due(self, now):
        self.calls.append(now)
        return [
            CycleExecution(
                watch_id="watch-1",
                run_id=f"run-{len(self.calls)}",
                status="COMPLETED",
                result_count=1,
                retry_count=0,
            )
        ]


def test_run_once_recovers_interrupted_runs_only_on_startup():
    runtime = FakeRuntime(recovered_runs=2)
    cycle = FakeCycle()
    service = UnattendedMonitoringService(runtime, cycle, poll_seconds=30)

    first = service.run_once(NOW)
    second = service.run_once(NOW)

    assert first.recovered_runs == 2
    assert second.recovered_runs == 0
    assert runtime.recovery_calls == [NOW]
    assert len(first.executions) == 1
    assert len(second.executions) == 1
    assert cycle.calls == [NOW, NOW]


def test_serve_forever_uses_bounded_poll_loop_for_testability():
    runtime = FakeRuntime()
    cycle = FakeCycle()
    service = UnattendedMonitoringService(runtime, cycle, poll_seconds=15)
    sleeps = []

    iterations = service.serve_forever(
        clock=lambda: NOW,
        sleeper=sleeps.append,
        max_iterations=3,
    )

    assert iterations == 3
    assert len(cycle.calls) == 3
    assert runtime.recovery_calls == [NOW]
    assert sleeps == [15.0, 15.0]


def test_serve_forever_respects_stop_before_first_iteration():
    runtime = FakeRuntime()
    cycle = FakeCycle()
    service = UnattendedMonitoringService(runtime, cycle)

    iterations = service.serve_forever(stop_requested=lambda: True)

    assert iterations == 0
    assert cycle.calls == []
    assert runtime.recovery_calls == []


def test_poll_interval_and_iteration_limit_fail_closed():
    runtime = FakeRuntime()
    cycle = FakeCycle()

    with pytest.raises(ValueError, match="poll_seconds"):
        UnattendedMonitoringService(runtime, cycle, poll_seconds=0)

    service = UnattendedMonitoringService(runtime, cycle)
    with pytest.raises(ValueError, match="max_iterations"):
        service.serve_forever(max_iterations=0)
