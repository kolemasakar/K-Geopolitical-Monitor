"""O1 on-demand request path: strictly disposable offline integration acceptance.

A synthetic enabled watch exists *only inside the disposable test database* and
is not a proposal to activate either disabled production watch.
"""
from datetime import datetime, timezone
import sqlite3

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_operational_cycle import LiveOperationalCycle

CLOCK = datetime(2026, 10, 25, 20, 0, tzinfo=timezone.utc)


class FixedSource:
    def __init__(self, source_id, host, *, failed=False):
        self.source_id = source_id
        self.source_name = source_id
        self.source_class = "Official sources"
        self.host = host
        self.failed = failed
        self.calls = 0

    def fetch(self, watch, collected_at):
        self.calls += 1
        if self.failed:
            raise RuntimeError("synthetic unavailable source")
        return [LiveSourceItem(
            item_id="fixture-" + self.source_id,
            source_id=self.source_id,
            source_name=self.source_name,
            source_class=self.source_class,
            title="Synthetic verified event",
            summary="Offline synthetic evidence, not a real event.",
            original_url="https://" + self.host + "/fixture",
            collected_at=collected_at,
            reliability="official",
        )]


def isolated_cycle(tmp_path, *, fail_second=False, fail_both=False):
    root = tmp_path / "isolated-o1"
    root.mkdir()
    runtime = OperationalMonitoringRuntime(root)
    # This watch is in disposable SQLite only; never open production.
    runtime.create_watch(
        "Synthetic one-shot request", "synthetic",
        cadence_minutes=1440,
        enabled=True, created_at=CLOCK,
        watch_id="isolated-owner-request",
    )
    sources = [
        FixedSource("official-a", "agency-a.example", failed=fail_both),
        FixedSource("official-b", "agency-b.example", failed=fail_second or fail_both),
    ]
    cycle = LiveOperationalCycle(runtime, LiveSourceCollector(runtime, sources),
                                 LiveEndToEndProcessor(runtime))
    return runtime, cycle, sources


def db_count(runtime, table):
    with sqlite3.connect(runtime.database_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]


def test_on_demand_two_independent_fixture_sources(tmp_path):
    runtime, cycle, sources = isolated_cycle(tmp_path)
    assert db_count(runtime, "monitoring_runs") == 0
    executions = cycle.execute_due(CLOCK)
    assert len(executions) == 1
    assert executions[0].status == "COMPLETED"
    assert db_count(runtime, "source_collection_runs") == 1
    assert db_count(runtime, "source_collection_attempts") == 2
    assert db_count(runtime, "live_analysis_runs") == 1
    assert db_count(runtime, "live_source_provenance") == 2
    assert db_count(runtime, "monitoring_runs") == 1
    assert all(s.calls == 1 for s in sources)
    # No continuous/unrequested repeats: cadence blocks an immediate second call.
    assert cycle.execute_due(CLOCK) == []
    assert all(s.calls == 1 for s in sources)


def test_on_demand_one_fixture_source_unavailable(tmp_path):
    runtime, cycle, sources = isolated_cycle(tmp_path, fail_second=True)
    executions = cycle.execute_due(CLOCK)
    assert len(executions) == 1
    assert executions[0].status == "COMPLETED"
    with sqlite3.connect(runtime.database_path) as conn:
        status, failures = conn.execute(
            "SELECT status, source_failure_count FROM source_collection_runs"
        ).fetchone()
        assert (status, failures) == ("PARTIAL", 1)
    assert db_count(runtime, "live_source_provenance") == 1


def test_on_demand_all_sources_unavailable_fail_closed(tmp_path):
    runtime, cycle, sources = isolated_cycle(tmp_path, fail_both=True)
    executions = cycle.execute_due(CLOCK)
    assert len(executions) == 1
    assert executions[0].status == "FAILED"
    assert db_count(runtime, "live_analysis_runs") == 0
    assert db_count(runtime, "source_collection_attempts") == 2
    assert db_count(runtime, "live_source_provenance") == 0
