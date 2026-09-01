"""Persisted owner-only unattended runtime health instrumentation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .database import runtime_database_connection
from .monitoring_cycle import CycleExecution
from .operational_monitoring import COMPLETED, FAILED, _normalize_time


RUNTIME_HEALTH_INSTRUMENTATION_VERSION = "KGM_OWNER_RUNTIME_HEALTH_V1"
IDLE = "IDLE"
HEALTHY = "HEALTHY"
DEGRADED = "DEGRADED"


@dataclass(frozen=True)
class RuntimeHealthSnapshot:
    instrumentation_version: str
    last_supervisor_tick_at: datetime
    last_completed_tick_at: datetime
    last_successful_execution_at: datetime | None
    recovered_runs: int
    execution_count: int
    completed_execution_count: int
    failed_execution_count: int
    tick_status: str
    last_error: str | None


class RuntimeHealthStore:
    """Persist only directly instrumented supervisor-tick facts.

    This store intentionally does not infer process uptime, global source health,
    coverage completeness or service availability from unrelated timestamps.
    """

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path).resolve()

    def record_tick(
        self,
        *,
        checked_at: datetime,
        recovered_runs: int,
        executions: tuple[CycleExecution, ...],
    ) -> RuntimeHealthSnapshot:
        current = _normalize_time(checked_at)
        if recovered_runs < 0:
            raise ValueError("recovered_runs must not be negative")

        completed = [item for item in executions if item.status == COMPLETED]
        failed = [item for item in executions if item.status == FAILED]
        unknown = [
            item for item in executions if item.status not in {COMPLETED, FAILED}
        ]
        if unknown:
            raise ValueError("runtime health received an unsupported execution status")

        if failed:
            status = DEGRADED
        elif completed:
            status = HEALTHY
        else:
            status = IDLE

        last_error = next(
            (item.error for item in reversed(failed) if item.error),
            None,
        )

        with runtime_database_connection(self.database_path) as connection:
            prior = connection.execute(
                """
                SELECT last_successful_execution_at
                FROM owner_runtime_health
                WHERE singleton_id = 1
                """
            ).fetchone()
            last_successful = (
                current
                if completed
                else (
                    datetime.fromisoformat(prior[0])
                    if prior is not None and prior[0]
                    else None
                )
            )
            connection.execute(
                """
                INSERT INTO owner_runtime_health(
                    singleton_id,
                    instrumentation_version,
                    last_supervisor_tick_at,
                    last_completed_tick_at,
                    last_successful_execution_at,
                    recovered_runs,
                    execution_count,
                    completed_execution_count,
                    failed_execution_count,
                    tick_status,
                    last_error
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(singleton_id) DO UPDATE SET
                    instrumentation_version = excluded.instrumentation_version,
                    last_supervisor_tick_at = excluded.last_supervisor_tick_at,
                    last_completed_tick_at = excluded.last_completed_tick_at,
                    last_successful_execution_at = excluded.last_successful_execution_at,
                    recovered_runs = excluded.recovered_runs,
                    execution_count = excluded.execution_count,
                    completed_execution_count = excluded.completed_execution_count,
                    failed_execution_count = excluded.failed_execution_count,
                    tick_status = excluded.tick_status,
                    last_error = excluded.last_error
                """,
                (
                    RUNTIME_HEALTH_INSTRUMENTATION_VERSION,
                    current.isoformat(),
                    current.isoformat(),
                    last_successful.isoformat() if last_successful is not None else None,
                    recovered_runs,
                    len(executions),
                    len(completed),
                    len(failed),
                    status,
                    last_error,
                ),
            )

        return RuntimeHealthSnapshot(
            instrumentation_version=RUNTIME_HEALTH_INSTRUMENTATION_VERSION,
            last_supervisor_tick_at=current,
            last_completed_tick_at=current,
            last_successful_execution_at=last_successful,
            recovered_runs=recovered_runs,
            execution_count=len(executions),
            completed_execution_count=len(completed),
            failed_execution_count=len(failed),
            tick_status=status,
            last_error=last_error,
        )

    def latest(self) -> RuntimeHealthSnapshot | None:
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT
                    instrumentation_version,
                    last_supervisor_tick_at,
                    last_completed_tick_at,
                    last_successful_execution_at,
                    recovered_runs,
                    execution_count,
                    completed_execution_count,
                    failed_execution_count,
                    tick_status,
                    last_error
                FROM owner_runtime_health
                WHERE singleton_id = 1
                """
            ).fetchone()

        if row is None:
            return None
        return RuntimeHealthSnapshot(
            instrumentation_version=str(row[0]),
            last_supervisor_tick_at=datetime.fromisoformat(row[1]),
            last_completed_tick_at=datetime.fromisoformat(row[2]),
            last_successful_execution_at=(
                datetime.fromisoformat(row[3]) if row[3] else None
            ),
            recovered_runs=int(row[4]),
            execution_count=int(row[5]),
            completed_execution_count=int(row[6]),
            failed_execution_count=int(row[7]),
            tick_status=str(row[8]),
            last_error=row[9],
        )
