#!/usr/bin/env python3
"""Deterministic Phase 19 accelerated operational-stability proof.

This script exercises restart/retry/idempotency/integrity/diagnostic behavior
without pretending that simulated timestamps are real elapsed soak evidence.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
import tempfile

from kgeopolitical_monitor.live_sources import (
    LiveSourceCollector,
    LiveSourceItem,
    SourceCollectionAuditStore,
)
from kgeopolitical_monitor.monitoring_cycle import CycleExecution
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.operational_stability import (
    CRITICAL,
    HEALTHY,
    REPEATED_FAILURE,
    RETRY_RECURRENCE,
    RUN_STALLED,
    SOURCE_NEVER_OBSERVED,
    SOURCE_STALE,
    SUPERVISOR_STALE,
    WATCH_LATE,
    OperationalStabilityEvaluator,
    check_sqlite_integrity,
    evaluate_soak_window,
)
from kgeopolitical_monitor.runtime_health import RuntimeHealthStore


START = datetime(2026, 9, 9, 0, 0, tzinfo=timezone.utc)


class StaticAdapter:
    source_id = "synthetic-official"
    source_name = "Synthetic Official Source"
    source_class = "Official sources"

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id="synthetic-stable-item",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Synthetic beta stability event",
                summary="Non-sensitive deterministic Phase 19 fixture.",
                original_url="https://example.org/p19-synthetic",
                collected_at=collected_at,
                reliability="official",
            )
        ]


class AuditAdapter:
    source_id = "stale-source"
    source_name = "Stale Synthetic Source"
    source_class = "Official sources"


def _healthy_accelerated_window(root: Path) -> dict[str, object]:
    runtime = OperationalMonitoringRuntime(root / "healthy")
    watch = runtime.create_watch(
        "P19 synthetic soak",
        "synthetic stability",
        60,
        watch_id="watch-soak",
        created_at=START,
    )
    health = RuntimeHealthStore(runtime.database_path)

    # 25 hourly logical executions span 24 simulated hours. No wall-clock soak is claimed.
    for hour in range(25):
        at = START + timedelta(hours=hour)
        run = runtime.start_run(watch.watch_id, run_id=f"run-soak-{hour:02d}", started_at=at)
        runtime.complete_run(run.run_id, result_count=1, completed_at=at)
        health.record_tick(
            checked_at=at,
            recovered_runs=0,
            executions=(
                CycleExecution(
                    watch_id=watch.watch_id,
                    run_id=run.run_id,
                    status="COMPLETED",
                    result_count=1,
                    retry_count=run.retry_count,
                ),
            ),
        )

    collector = LiveSourceCollector(runtime, [StaticAdapter()])
    collector.collect(watch.watch_id, START + timedelta(hours=24))

    report = OperationalStabilityEvaluator(
        runtime.database_path,
        expected_source_ids=(StaticAdapter.source_id,),
    ).evaluate(START + timedelta(hours=24))

    if report.status != HEALTHY:
        raise RuntimeError(f"accelerated healthy window was not healthy: {report.as_dict()}")

    window = evaluate_soak_window(
        runtime.database_path,
        started_at=START,
        ended_at=START + timedelta(hours=24),
    )
    if not window.clean:
        raise RuntimeError(f"accelerated soak-window evaluator was not clean: {window.as_dict()}")

    return {
        "logical_window_hours": 24,
        "logical_execution_count": 25,
        "status": report.status,
        "soak_window": window.as_dict(),
        "integrity": report.integrity.as_dict(),
    }


def _restart_retry_and_idempotency(root: Path) -> dict[str, object]:
    project = root / "restart"
    runtime = OperationalMonitoringRuntime(project)
    watch = runtime.create_watch(
        "P19 restart",
        "restart stability",
        60,
        watch_id="watch-restart",
        created_at=START,
    )
    interrupted = runtime.start_run(
        watch.watch_id,
        run_id="run-interrupted",
        started_at=START,
    )

    restarted = OperationalMonitoringRuntime(project)
    recovered = restarted.recover_interrupted_runs(START + timedelta(minutes=10))
    recovered_run = restarted.repository.latest_run(watch.watch_id)
    if recovered != 1 or recovered_run is None:
        raise RuntimeError("restart recovery did not recover exactly one interrupted run")
    if recovered_run.status != "FAILED" or not recovered_run.recovered:
        raise RuntimeError("interrupted run was not marked recovered/FAILED")
    if recovered_run.run_id != interrupted.run_id:
        raise RuntimeError("restart recovery changed run identity")

    retry = restarted.start_run(
        watch.watch_id,
        run_id="run-retry",
        started_at=START + timedelta(minutes=11),
    )
    if retry.retry_count != 1:
        raise RuntimeError(f"retry_count expected 1, got {retry.retry_count}")
    restarted.complete_run(
        retry.run_id,
        result_count=1,
        completed_at=START + timedelta(minutes=11),
    )

    collector = LiveSourceCollector(restarted, [StaticAdapter()])
    at = START + timedelta(minutes=12)
    collector.collect(watch.watch_id, at)
    collector.collect(watch.watch_id, at + timedelta(minutes=1))
    with sqlite3.connect(restarted.database_path) as connection:
        raw_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM raw_items WHERE id = ?",
                ("synthetic-stable-item",),
            ).fetchone()[0]
        )
    if raw_count != 1:
        raise RuntimeError(f"idempotent raw item count expected 1, got {raw_count}")

    integrity = check_sqlite_integrity(restarted.database_path)
    if not integrity.ok:
        raise RuntimeError(f"restart database integrity failed: {integrity.as_dict()}")

    return {
        "recovered_runs": recovered,
        "retry_count": retry.retry_count,
        "raw_item_count_after_duplicate_collection": raw_count,
        "integrity": integrity.as_dict(),
    }


def _fault_classification(root: Path) -> dict[str, object]:
    runtime = OperationalMonitoringRuntime(root / "faults")
    failing = runtime.create_watch(
        "P19 failing watch",
        "failure stability",
        60,
        watch_id="watch-failing",
        created_at=START,
    )
    stalled = runtime.create_watch(
        "P19 stalled watch",
        "stall stability",
        60,
        watch_id="watch-stalled",
        created_at=START,
    )

    for hour in range(4):
        at = START + timedelta(hours=hour)
        run = runtime.start_run(
            failing.watch_id,
            run_id=f"run-failed-{hour}",
            started_at=at,
        )
        runtime.fail_run(
            run.run_id,
            "synthetic injected source failure",
            completed_at=at,
        )

    runtime.start_run(
        stalled.watch_id,
        run_id="run-stalled",
        started_at=START + timedelta(hours=4),
    )

    RuntimeHealthStore(runtime.database_path).record_tick(
        checked_at=START,
        recovered_runs=0,
        executions=(),
    )

    audit = SourceCollectionAuditStore(runtime.database_path)
    audit.start("collection-stale", failing.watch_id, START)
    audit.record_source_attempt(
        "collection-stale",
        AuditAdapter(),
        status="SUCCESS",
        item_count=0,
        attempted_at=START,
    )

    evaluated_at = START + timedelta(hours=5)
    report = OperationalStabilityEvaluator(
        runtime.database_path,
        expected_source_ids=("stale-source", "never-source"),
    ).evaluate(evaluated_at)

    codes = {finding.code for finding in report.findings}
    required = {
        SUPERVISOR_STALE,
        WATCH_LATE,
        RUN_STALLED,
        SOURCE_STALE,
        SOURCE_NEVER_OBSERVED,
        REPEATED_FAILURE,
        RETRY_RECURRENCE,
    }
    missing = required - codes
    if missing:
        raise RuntimeError(f"fault classifier missed: {sorted(missing)}")
    if report.status != CRITICAL:
        raise RuntimeError(f"fault scenario expected CRITICAL, got {report.status}")
    if not report.integrity.ok:
        raise RuntimeError("injected operational failures corrupted canonical SQLite")

    return {
        "status": report.status,
        "finding_codes": sorted(codes),
        "critical_finding_count": report.metrics["critical_finding_count"],
        "degraded_finding_count": report.metrics["degraded_finding_count"],
        "integrity": report.integrity.as_dict(),
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kgm-p19-") as temp_dir:
        root = Path(temp_dir)
        accelerated = _healthy_accelerated_window(root)
        restart = _restart_retry_and_idempotency(root)
        faults = _fault_classification(root)

    result = {
        "gate_target": "PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED",
        "proof_scope": "ACCELERATED_DETERMINISTIC_HARNESS",
        "simulated_time": True,
        "accelerated_24h": accelerated,
        "restart_retry_idempotency": restart,
        "fault_classification": faults,
        "real_elapsed_soak": {
            "24h": "NOT_EVIDENCED",
            "72h": "NOT_EVIDENCED",
            "7d": "NOT_EVIDENCED",
        },
        "phase19_full_gate": "NOT_CLOSED",
        "owner_local_canonical": True,
        "shared_runtime_active": False,
        "migration_033_created": False,
        "paid_resources_authorized": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("P19_ACCELERATED_STABILITY_PROOF=PASS")
    print("P19_RESTART_RECOVERY=PASS")
    print("P19_RETRY_IDEMPOTENCY=PASS")
    print("P19_SQLITE_INTEGRITY=PASS")
    print("P19_OPERATOR_DIAGNOSTICS=PASS")
    print("P19_REAL_24H_SOAK=NOT_EVIDENCED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
