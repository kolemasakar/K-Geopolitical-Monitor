"""Owner operating mode: disabled watch inventory never dispatches background research."""
from datetime import datetime, timezone

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.unattended_service import UnattendedMonitoringService


class NoCollectionExecutor:
    def __init__(self):
        self.calls = 0

    def execute_due(self, now):
        self.calls += 1
        return []


def test_on_demand_disabled_watches_do_not_create_background_runs(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    runtime = OperationalMonitoringRuntime(root)
    runtime.create_watch("legacy a", "topic a", 60, enabled=False)
    runtime.create_watch("legacy b", "topic b", 120, enabled=False)
    now = datetime(2026, 10, 25, 20, 0, tzinfo=timezone.utc)

    assert len(runtime.repository.list_watches()) == 2
    assert runtime.repository.list_watches(enabled_only=True) == []
    assert runtime.due_watches(now) == []

    executor = NoCollectionExecutor()
    service = UnattendedMonitoringService(runtime, executor, poll_seconds=60)
    tick = service.run_once(now)
    assert tick.executions == ()
    assert executor.calls == 1
    assert runtime.repository.list_watches(enabled_only=True) == []
    assert all(runtime.repository.latest_run(w.watch_id) is None for w in runtime.repository.list_watches())
