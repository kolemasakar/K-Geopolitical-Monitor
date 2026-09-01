from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.monitoring_cycle import CycleExecution
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.runtime_health import (
    DEGRADED,
    HEALTHY,
    IDLE,
    RUNTIME_HEALTH_INSTRUMENTATION_VERSION,
    RuntimeHealthStore,
)


NOW = datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc)


def _store(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path)
    return RuntimeHealthStore(runtime.database_path)


def test_idle_tick_is_instrumented_without_inferred_success(tmp_path):
    store = _store(tmp_path)

    snapshot = store.record_tick(
        checked_at=NOW,
        recovered_runs=0,
        executions=(),
    )

    assert snapshot.instrumentation_version == RUNTIME_HEALTH_INSTRUMENTATION_VERSION
    assert snapshot.last_supervisor_tick_at == NOW
    assert snapshot.last_completed_tick_at == NOW
    assert snapshot.last_successful_execution_at is None
    assert snapshot.execution_count == 0
    assert snapshot.tick_status == IDLE
    assert snapshot.last_error is None
    assert store.latest() == snapshot


def test_successful_execution_records_traceable_success_timestamp(tmp_path):
    store = _store(tmp_path)
    execution = CycleExecution(
        watch_id="watch-1",
        run_id="run-1",
        status="COMPLETED",
        result_count=2,
        retry_count=0,
    )

    snapshot = store.record_tick(
        checked_at=NOW,
        recovered_runs=1,
        executions=(execution,),
    )

    assert snapshot.last_successful_execution_at == NOW
    assert snapshot.recovered_runs == 1
    assert snapshot.execution_count == 1
    assert snapshot.completed_execution_count == 1
    assert snapshot.failed_execution_count == 0
    assert snapshot.tick_status == HEALTHY


def test_failed_tick_is_degraded_and_preserves_prior_success_timestamp(tmp_path):
    store = _store(tmp_path)
    store.record_tick(
        checked_at=NOW,
        recovered_runs=0,
        executions=(
            CycleExecution(
                watch_id="watch-ok",
                run_id="run-ok",
                status="COMPLETED",
                result_count=1,
                retry_count=0,
            ),
        ),
    )
    failed_at = NOW + timedelta(minutes=1)

    snapshot = store.record_tick(
        checked_at=failed_at,
        recovered_runs=0,
        executions=(
            CycleExecution(
                watch_id="watch-failed",
                run_id="run-failed",
                status="FAILED",
                result_count=0,
                retry_count=1,
                error="source unavailable",
            ),
        ),
    )

    assert snapshot.last_supervisor_tick_at == failed_at
    assert snapshot.last_successful_execution_at == NOW
    assert snapshot.completed_execution_count == 0
    assert snapshot.failed_execution_count == 1
    assert snapshot.tick_status == DEGRADED
    assert snapshot.last_error == "source unavailable"


def test_mixed_tick_is_degraded_but_records_successful_execution_timestamp(tmp_path):
    store = _store(tmp_path)

    snapshot = store.record_tick(
        checked_at=NOW,
        recovered_runs=0,
        executions=(
            CycleExecution("watch-a", "run-a", "COMPLETED", 1, 0),
            CycleExecution("watch-b", "run-b", "FAILED", 0, 0, "timeout"),
        ),
    )

    assert snapshot.last_successful_execution_at == NOW
    assert snapshot.completed_execution_count == 1
    assert snapshot.failed_execution_count == 1
    assert snapshot.tick_status == DEGRADED
    assert snapshot.last_error == "timeout"


def test_runtime_health_rejects_naive_time_and_unknown_execution_status(tmp_path):
    store = _store(tmp_path)

    with pytest.raises(ValueError, match="timezone-aware"):
        store.record_tick(
            checked_at=datetime(2026, 9, 1, 8, 0),
            recovered_runs=0,
            executions=(),
        )

    with pytest.raises(ValueError, match="unsupported execution status"):
        store.record_tick(
            checked_at=NOW,
            recovered_runs=0,
            executions=(CycleExecution("watch", "run", "UNKNOWN", 0, 0),),
        )
