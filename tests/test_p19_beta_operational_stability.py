from datetime import datetime, timedelta, timezone
import json
import sqlite3

import pytest

from kgeopolitical_monitor.monitoring_cycle import CycleExecution
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.operational_stability import (
    CRITICAL,
    DEGRADED,
    HEALTHY,
    REPEATED_FAILURE,
    RETRY_RECURRENCE,
    RUN_STALLED,
    SOURCE_NEVER_OBSERVED,
    SOURCE_STALE,
    SUPERVISOR_HEALTH_MISSING,
    SUPERVISOR_STALE,
    WATCH_LATE,
    BetaOperationalSLO,
    OperationalStabilityEvaluator,
    check_sqlite_integrity,
    classify_operational_error,
    evaluate_soak_window,
)
from kgeopolitical_monitor.runtime_health import RuntimeHealthStore


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _record_success(runtime, watch_id, at, *, run_id="run-ok"):
    run = runtime.start_run(watch_id, run_id=run_id, started_at=at)
    runtime.complete_run(run.run_id, result_count=1, completed_at=at)
    RuntimeHealthStore(runtime.database_path).record_tick(
        checked_at=at,
        recovered_runs=0,
        executions=(
            CycleExecution(
                watch_id=watch_id,
                run_id=run.run_id,
                status="COMPLETED",
                result_count=1,
                retry_count=run.retry_count,
            ),
        ),
    )
    return run


def test_operational_stability_healthy_with_fresh_tick_and_schedule(tmp_path):
    runtime = _runtime(tmp_path)
    watch = runtime.create_watch(
        "healthy",
        "healthy",
        60,
        watch_id="watch-healthy",
        created_at=NOW - timedelta(hours=1),
    )
    _record_success(runtime, watch.watch_id, NOW, run_id="run-healthy")

    report = OperationalStabilityEvaluator(runtime.database_path).evaluate(NOW)

    assert report.status == HEALTHY
    assert report.findings == ()
    assert report.integrity.ok is True
    assert report.metrics["enabled_watch_count"] == 1
    assert report.metrics["running_run_count"] == 0
    json.dumps(report.as_dict())


def test_missing_and_stale_supervisor_health_are_classified(tmp_path):
    runtime = _runtime(tmp_path)
    report = OperationalStabilityEvaluator(runtime.database_path).evaluate(NOW)

    assert report.status == DEGRADED
    assert {item.code for item in report.findings} == {SUPERVISOR_HEALTH_MISSING}

    RuntimeHealthStore(runtime.database_path).record_tick(
        checked_at=NOW - timedelta(minutes=10),
        recovered_runs=0,
        executions=(),
    )
    stale = OperationalStabilityEvaluator(runtime.database_path).evaluate(NOW)
    assert stale.status == CRITICAL
    assert SUPERVISOR_STALE in {item.code for item in stale.findings}


def test_late_watch_stalled_run_and_failure_recurrence_are_visible(tmp_path):
    runtime = _runtime(tmp_path)
    failing = runtime.create_watch(
        "failing",
        "failing",
        60,
        watch_id="watch-failing",
        created_at=NOW - timedelta(hours=6),
    )
    stalled = runtime.create_watch(
        "stalled",
        "stalled",
        60,
        watch_id="watch-stalled",
        created_at=NOW - timedelta(hours=6),
    )

    for offset in (5, 4, 3, 2):
        at = NOW - timedelta(hours=offset)
        run = runtime.start_run(
            failing.watch_id,
            run_id=f"run-failed-{offset}",
            started_at=at,
        )
        runtime.fail_run(run.run_id, "synthetic failure", completed_at=at)

    runtime.start_run(
        stalled.watch_id,
        run_id="run-stalled",
        started_at=NOW - timedelta(hours=1),
    )
    RuntimeHealthStore(runtime.database_path).record_tick(
        checked_at=NOW,
        recovered_runs=0,
        executions=(),
    )

    report = OperationalStabilityEvaluator(runtime.database_path).evaluate(NOW)
    codes = {item.code for item in report.findings}

    assert report.status == CRITICAL
    assert WATCH_LATE in codes
    assert RUN_STALLED in codes
    assert REPEATED_FAILURE in codes
    assert RETRY_RECURRENCE in codes


def test_expected_sources_are_classified_as_missing_or_stale(tmp_path):
    runtime = _runtime(tmp_path)
    watch = runtime.create_watch(
        "source watch",
        "source watch",
        60,
        watch_id="watch-source",
        created_at=NOW,
    )
    _record_success(runtime, watch.watch_id, NOW, run_id="run-source")

    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            """
            INSERT INTO source_collection_runs(
                collection_id, watch_id, status, started_at, completed_at,
                item_count, source_success_count, source_failure_count, failures
            ) VALUES (?, ?, 'COMPLETED', ?, ?, 0, 1, 0, '[]')
            """,
            (
                "collection-old",
                watch.watch_id,
                (NOW - timedelta(hours=4)).isoformat(),
                (NOW - timedelta(hours=4)).isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO source_collection_attempts(
                collection_id, source_id, source_name, source_class,
                status, item_count, error, attempted_at
            ) VALUES (?, ?, ?, ?, 'SUCCESS', 0, NULL, ?)
            """,
            (
                "collection-old",
                "old-source",
                "Old Source",
                "Official sources",
                (NOW - timedelta(hours=4)).isoformat(),
            ),
        )

    report = OperationalStabilityEvaluator(
        runtime.database_path,
        expected_source_ids=("old-source", "missing-source"),
    ).evaluate(NOW)
    codes = {item.code for item in report.findings}

    assert report.status == DEGRADED
    assert SOURCE_STALE in codes
    assert SOURCE_NEVER_OBSERVED in codes
    assert report.metrics["expected_source_count"] == 2
    assert report.metrics["observed_source_count"] == 1


def test_sqlite_integrity_checker_reports_clean_runtime(tmp_path):
    runtime = _runtime(tmp_path)

    result = check_sqlite_integrity(runtime.database_path)

    assert result.integrity_check == "ok"
    assert result.foreign_key_violation_count == 0
    assert result.ok is True


def test_beta_slo_fails_closed_on_non_positive_thresholds():
    with pytest.raises(ValueError, match="supervisor_stale_after_seconds"):
        BetaOperationalSLO(supervisor_stale_after_seconds=0)


def test_soak_window_detects_historical_gap_and_failure_distribution(tmp_path):
    runtime = _runtime(tmp_path)
    watch = runtime.create_watch(
        "window",
        "window",
        60,
        watch_id="watch-window",
        created_at=NOW - timedelta(hours=4),
    )
    first = runtime.start_run(
        watch.watch_id,
        run_id="run-window-1",
        started_at=NOW - timedelta(hours=4),
    )
    runtime.complete_run(first.run_id, completed_at=NOW - timedelta(hours=4))

    failed = runtime.start_run(
        watch.watch_id,
        run_id="run-window-2",
        started_at=NOW - timedelta(hours=2),
    )
    runtime.fail_run(
        failed.run_id,
        "source network timeout",
        completed_at=NOW - timedelta(hours=2),
    )

    report = evaluate_soak_window(
        runtime.database_path,
        started_at=NOW - timedelta(hours=4),
        ended_at=NOW - timedelta(hours=1, minutes=30),
    )

    assert report.clean is False
    assert report.missed_cycle_count >= 1
    assert report.failed_run_count == 1
    assert report.error_class_distribution == {"TIMEOUT": 1}


def test_error_classification_is_deterministic():
    assert classify_operational_error("interrupted runtime recovered") == "RECOVERED_INTERRUPTION"
    assert classify_operational_error("source request timed out") == "TIMEOUT"
    assert classify_operational_error("HTTP error 503") == "HTTP"
    assert classify_operational_error("connection reset") == "NETWORK"
    assert classify_operational_error("permission denied") == "PERMISSION"
    assert classify_operational_error("sqlite database locked") == "DATABASE"
    assert classify_operational_error("live source item identity mismatch") == "SOURCE_IDENTITY"
    assert classify_operational_error("source unavailable") == "SOURCE"
    assert classify_operational_error("unexpected") == "OTHER"
