"""Phase 19 owner-local beta operational-stability evaluation.

The evaluator is deliberately read-only with respect to the canonical SQLite
database. It classifies observable operational facts into bounded, deterministic
findings so an operator does not need to inspect raw database internals.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import Counter
import sqlite3
from typing import Iterable

from .runtime_health import RuntimeHealthStore


HEALTHY = "HEALTHY"
DEGRADED = "DEGRADED"
CRITICAL = "CRITICAL"

SEVERITY_DEGRADED = "DEGRADED"
SEVERITY_CRITICAL = "CRITICAL"

SUPERVISOR_HEALTH_MISSING = "SUPERVISOR_HEALTH_MISSING"
SUPERVISOR_STALE = "SUPERVISOR_STALE"
WATCH_LATE = "WATCH_LATE"
RUN_STALLED = "RUN_STALLED"
SOURCE_NEVER_OBSERVED = "SOURCE_NEVER_OBSERVED"
SOURCE_STALE = "SOURCE_STALE"
REPEATED_FAILURE = "REPEATED_FAILURE"
RETRY_RECURRENCE = "RETRY_RECURRENCE"
SQLITE_INTEGRITY_FAILURE = "SQLITE_INTEGRITY_FAILURE"
SQLITE_FOREIGN_KEY_FAILURE = "SQLITE_FOREIGN_KEY_FAILURE"
SOAK_MISSED_CYCLE = "SOAK_MISSED_CYCLE"
SOAK_FAILED_EXECUTIONS = "SOAK_FAILED_EXECUTIONS"
SOAK_RUNNING_EXECUTIONS = "SOAK_RUNNING_EXECUTIONS"

ERROR_RECOVERED_INTERRUPTION = "RECOVERED_INTERRUPTION"
ERROR_TIMEOUT = "TIMEOUT"
ERROR_HTTP = "HTTP"
ERROR_NETWORK = "NETWORK"
ERROR_PERMISSION = "PERMISSION"
ERROR_DATABASE = "DATABASE"
ERROR_SOURCE_IDENTITY = "SOURCE_IDENTITY"
ERROR_SOURCE = "SOURCE"
ERROR_OTHER = "OTHER"


def classify_operational_error(error: str | None) -> str:
    """Map free-form persisted errors into deterministic operator classes."""

    text = str(error or "").strip().lower()
    if "interrupted runtime recovered" in text:
        return ERROR_RECOVERED_INTERRUPTION
    if "timeout" in text or "timed out" in text:
        return ERROR_TIMEOUT
    if "http" in text:
        return ERROR_HTTP
    if "network" in text or "connection" in text or "dns" in text:
        return ERROR_NETWORK
    if "permission" in text or "denied" in text:
        return ERROR_PERMISSION
    if "sqlite" in text or "database" in text:
        return ERROR_DATABASE
    if "identity mismatch" in text:
        return ERROR_SOURCE_IDENTITY
    if "source" in text:
        return ERROR_SOURCE
    return ERROR_OTHER


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("operational stability timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _parse(value: str) -> datetime:
    return _utc(datetime.fromisoformat(value))


@dataclass(frozen=True)
class BetaOperationalSLO:
    """Bounded beta health thresholds.

    These are operational detection thresholds, not uptime/SLA claims.
    """

    supervisor_stale_after_seconds: int = 180
    watch_lateness_grace_minutes: int = 15
    stalled_run_after_minutes: int = 30
    source_stale_after_minutes: int = 180
    repeated_failure_threshold: int = 3
    retry_recurrence_threshold: int = 3

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if int(value) <= 0:
                raise ValueError(f"{name} must be positive")


@dataclass(frozen=True)
class OperationalFinding:
    code: str
    severity: str
    subject: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class IntegrityResult:
    integrity_check: str
    foreign_key_violation_count: int

    @property
    def ok(self) -> bool:
        return self.integrity_check.lower() == "ok" and self.foreign_key_violation_count == 0

    def as_dict(self) -> dict[str, object]:
        return {
            "integrity_check": self.integrity_check,
            "foreign_key_violation_count": self.foreign_key_violation_count,
            "ok": self.ok,
        }


@dataclass(frozen=True)
class OperationalStabilityReport:
    evaluated_at: datetime
    status: str
    slo: BetaOperationalSLO
    findings: tuple[OperationalFinding, ...]
    metrics: dict[str, object]
    integrity: IntegrityResult

    def as_dict(self) -> dict[str, object]:
        return {
            "evaluated_at": self.evaluated_at.isoformat(),
            "status": self.status,
            "slo": asdict(self.slo),
            "findings": [finding.as_dict() for finding in self.findings],
            "metrics": dict(self.metrics),
            "integrity": self.integrity.as_dict(),
        }


@dataclass(frozen=True)
class SoakWindowReport:
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    clean: bool
    run_count: int
    completed_run_count: int
    failed_run_count: int
    running_run_count: int
    recovered_run_count: int
    missed_cycle_count: int
    error_class_distribution: dict[str, int]
    violations: tuple[OperationalFinding, ...]
    integrity: IntegrityResult

    def as_dict(self) -> dict[str, object]:
        return {
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "clean": self.clean,
            "run_count": self.run_count,
            "completed_run_count": self.completed_run_count,
            "failed_run_count": self.failed_run_count,
            "running_run_count": self.running_run_count,
            "recovered_run_count": self.recovered_run_count,
            "missed_cycle_count": self.missed_cycle_count,
            "error_class_distribution": dict(self.error_class_distribution),
            "violations": [item.as_dict() for item in self.violations],
            "integrity": self.integrity.as_dict(),
        }


def check_sqlite_integrity(database_path: str | Path) -> IntegrityResult:
    """Run SQLite integrity and FK checks without mutating application data."""

    path = Path(database_path).resolve()
    with sqlite3.connect(path) as connection:
        integrity_rows = connection.execute("PRAGMA integrity_check").fetchall()
        integrity = "; ".join(str(row[0]) for row in integrity_rows) if integrity_rows else "missing"
        fk_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    return IntegrityResult(
        integrity_check=integrity,
        foreign_key_violation_count=len(fk_rows),
    )


class OperationalStabilityEvaluator:
    """Read-only evaluator over existing owner-local operational facts."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        slo: BetaOperationalSLO | None = None,
        expected_source_ids: Iterable[str] = (),
    ) -> None:
        self.database_path = Path(database_path).resolve()
        self.slo = slo or BetaOperationalSLO()
        normalized = tuple(sorted({str(item).strip() for item in expected_source_ids if str(item).strip()}))
        self.expected_source_ids = normalized

    def evaluate(self, evaluated_at: datetime) -> OperationalStabilityReport:
        now = _utc(evaluated_at)
        findings: list[OperationalFinding] = []

        health = RuntimeHealthStore(self.database_path).latest()
        if health is None:
            findings.append(
                OperationalFinding(
                    SUPERVISOR_HEALTH_MISSING,
                    SEVERITY_DEGRADED,
                    "owner-runtime",
                    "No instrumented supervisor tick has been persisted.",
                )
            )
        else:
            age = now - _utc(health.last_supervisor_tick_at)
            if age > timedelta(seconds=self.slo.supervisor_stale_after_seconds):
                findings.append(
                    OperationalFinding(
                        SUPERVISOR_STALE,
                        SEVERITY_CRITICAL,
                        "owner-runtime",
                        (
                            f"Last supervisor tick is {int(age.total_seconds())}s old; "
                            f"limit={self.slo.supervisor_stale_after_seconds}s."
                        ),
                    )
                )

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            watches = connection.execute(
                """
                SELECT watch_id, cadence_minutes, created_at
                FROM monitoring_watches
                WHERE enabled = 1
                ORDER BY watch_id
                """
            ).fetchall()

            running_rows = connection.execute(
                """
                SELECT run_id, watch_id, started_at
                FROM monitoring_runs
                WHERE status = 'RUNNING'
                ORDER BY watch_id, started_at
                """
            ).fetchall()

            latest_rows = connection.execute(
                """
                SELECT r.run_id, r.watch_id, r.status, r.started_at,
                       r.completed_at, r.retry_count, r.error
                FROM monitoring_runs AS r
                JOIN (
                    SELECT watch_id, MAX(started_at) AS latest_started_at
                    FROM monitoring_runs
                    GROUP BY watch_id
                ) AS latest
                  ON latest.watch_id = r.watch_id
                 AND latest.latest_started_at = r.started_at
                ORDER BY r.watch_id, r.run_id DESC
                """
            ).fetchall()

            latest_by_watch: dict[str, sqlite3.Row] = {}
            for row in latest_rows:
                latest_by_watch.setdefault(str(row["watch_id"]), row)

            for watch in watches:
                watch_id = str(watch["watch_id"])
                cadence = int(watch["cadence_minutes"])
                latest = latest_by_watch.get(watch_id)
                anchor = _parse(str(watch["created_at"])) if latest is None else _parse(str(latest["started_at"]))
                due_at = anchor + timedelta(minutes=cadence + self.slo.watch_lateness_grace_minutes)
                if now > due_at and (latest is None or str(latest["status"]) != "RUNNING"):
                    findings.append(
                        OperationalFinding(
                            WATCH_LATE,
                            SEVERITY_DEGRADED,
                            watch_id,
                            (
                                f"Watch is late by {int((now - due_at).total_seconds())}s "
                                "beyond cadence plus grace."
                            ),
                        )
                    )

            for row in running_rows:
                started = _parse(str(row["started_at"]))
                age = now - started
                if age > timedelta(minutes=self.slo.stalled_run_after_minutes):
                    findings.append(
                        OperationalFinding(
                            RUN_STALLED,
                            SEVERITY_CRITICAL,
                            str(row["watch_id"]),
                            (
                                f"RUNNING execution {row['run_id']} is "
                                f"{int(age.total_seconds())}s old; "
                                f"limit={self.slo.stalled_run_after_minutes * 60}s."
                            ),
                        )
                    )

            for watch in watches:
                watch_id = str(watch["watch_id"])
                recent = connection.execute(
                    """
                    SELECT status, retry_count
                    FROM monitoring_runs
                    WHERE watch_id = ?
                    ORDER BY started_at DESC, run_id DESC
                    LIMIT ?
                    """,
                    (watch_id, self.slo.repeated_failure_threshold),
                ).fetchall()
                if (
                    len(recent) >= self.slo.repeated_failure_threshold
                    and all(str(row["status"]) == "FAILED" for row in recent)
                ):
                    findings.append(
                        OperationalFinding(
                            REPEATED_FAILURE,
                            SEVERITY_CRITICAL,
                            watch_id,
                            (
                                f"Last {self.slo.repeated_failure_threshold} executions "
                                "all failed."
                            ),
                        )
                    )

                latest = latest_by_watch.get(watch_id)
                if latest is not None and int(latest["retry_count"]) >= self.slo.retry_recurrence_threshold:
                    findings.append(
                        OperationalFinding(
                            RETRY_RECURRENCE,
                            SEVERITY_DEGRADED,
                            watch_id,
                            (
                                f"Latest retry_count={int(latest['retry_count'])}; "
                                f"limit={self.slo.retry_recurrence_threshold}."
                            ),
                        )
                    )

            observed_source_count = 0
            for source_id in self.expected_source_ids:
                row = connection.execute(
                    """
                    SELECT attempted_at, status
                    FROM source_collection_attempts
                    WHERE source_id = ?
                    ORDER BY attempted_at DESC
                    LIMIT 1
                    """,
                    (source_id,),
                ).fetchone()
                if row is None:
                    findings.append(
                        OperationalFinding(
                            SOURCE_NEVER_OBSERVED,
                            SEVERITY_DEGRADED,
                            source_id,
                            "Expected source has no persisted collection attempt.",
                        )
                    )
                    continue
                observed_source_count += 1
                attempted_at = _parse(str(row["attempted_at"]))
                age = now - attempted_at
                if age > timedelta(minutes=self.slo.source_stale_after_minutes):
                    findings.append(
                        OperationalFinding(
                            SOURCE_STALE,
                            SEVERITY_DEGRADED,
                            source_id,
                            (
                                f"Latest source attempt is {int(age.total_seconds())}s old; "
                                f"limit={self.slo.source_stale_after_minutes * 60}s."
                            ),
                        )
                    )

        with sqlite3.connect(self.database_path) as connection:
            failed_error_rows = connection.execute(
                """
                SELECT error
                FROM monitoring_runs
                WHERE status = 'FAILED'
                """
            ).fetchall()
        error_distribution = Counter(
            classify_operational_error(row[0]) for row in failed_error_rows
        )

        integrity = check_sqlite_integrity(self.database_path)
        if integrity.integrity_check.lower() != "ok":
            findings.append(
                OperationalFinding(
                    SQLITE_INTEGRITY_FAILURE,
                    SEVERITY_CRITICAL,
                    "canonical-sqlite",
                    f"PRAGMA integrity_check returned: {integrity.integrity_check}",
                )
            )
        if integrity.foreign_key_violation_count:
            findings.append(
                OperationalFinding(
                    SQLITE_FOREIGN_KEY_FAILURE,
                    SEVERITY_CRITICAL,
                    "canonical-sqlite",
                    (
                        f"PRAGMA foreign_key_check reported "
                        f"{integrity.foreign_key_violation_count} violation(s)."
                    ),
                )
            )

        findings = sorted(findings, key=lambda item: (item.severity, item.code, item.subject))
        if any(item.severity == SEVERITY_CRITICAL for item in findings):
            status = CRITICAL
        elif findings:
            status = DEGRADED
        else:
            status = HEALTHY

        metrics: dict[str, object] = {
            "enabled_watch_count": len(watches),
            "running_run_count": len(running_rows),
            "expected_source_count": len(self.expected_source_ids),
            "observed_source_count": observed_source_count,
            "critical_finding_count": sum(item.severity == SEVERITY_CRITICAL for item in findings),
            "degraded_finding_count": sum(item.severity == SEVERITY_DEGRADED for item in findings),
            "runtime_health_status": health.tick_status if health is not None else None,
            "error_class_distribution": dict(sorted(error_distribution.items())),
        }

        return OperationalStabilityReport(
            evaluated_at=now,
            status=status,
            slo=self.slo,
            findings=tuple(findings),
            metrics=metrics,
            integrity=integrity,
        )


def evaluate_soak_window(
    database_path: str | Path,
    *,
    started_at: datetime,
    ended_at: datetime,
    watch_lateness_grace_minutes: int = 15,
) -> SoakWindowReport:
    """Evaluate persisted execution history across a real or simulated time window.

    The function never decides whether timestamps represent real elapsed time.
    Callers must label simulated evidence honestly.
    """

    start = _utc(started_at)
    end = _utc(ended_at)
    if end <= start:
        raise ValueError("soak window ended_at must be after started_at")
    if watch_lateness_grace_minutes <= 0:
        raise ValueError("watch_lateness_grace_minutes must be positive")

    path = Path(database_path).resolve()
    violations: list[OperationalFinding] = []
    missed_cycle_count = 0

    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        watches = connection.execute(
            """
            SELECT watch_id, cadence_minutes, created_at
            FROM monitoring_watches
            WHERE enabled = 1
            ORDER BY watch_id
            """
        ).fetchall()

        window_runs = connection.execute(
            """
            SELECT run_id, watch_id, status, started_at, completed_at,
                   error, retry_count, recovered
            FROM monitoring_runs
            WHERE started_at >= ? AND started_at <= ?
            ORDER BY watch_id, started_at, run_id
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()

        runs_by_watch: dict[str, list[sqlite3.Row]] = {}
        for row in window_runs:
            runs_by_watch.setdefault(str(row["watch_id"]), []).append(row)

        for watch in watches:
            watch_id = str(watch["watch_id"])
            created_at = _parse(str(watch["created_at"]))
            if created_at > end:
                continue
            cadence = timedelta(minutes=int(watch["cadence_minutes"]))
            grace = timedelta(minutes=watch_lateness_grace_minutes)

            previous = connection.execute(
                """
                SELECT started_at
                FROM monitoring_runs
                WHERE watch_id = ? AND started_at < ?
                ORDER BY started_at DESC, run_id DESC
                LIMIT 1
                """,
                (watch_id, start.isoformat()),
            ).fetchone()

            rows = runs_by_watch.get(watch_id, [])
            if previous is not None:
                anchor = _parse(str(previous["started_at"]))
                first_deadline = anchor + cadence + grace
            else:
                anchor = created_at
                first_deadline = created_at + grace

            for index, row in enumerate(rows):
                current = _parse(str(row["started_at"]))
                deadline = first_deadline if index == 0 else anchor + cadence + grace
                if current > deadline:
                    missed_cycle_count += 1
                    violations.append(
                        OperationalFinding(
                            SOAK_MISSED_CYCLE,
                            SEVERITY_CRITICAL,
                            watch_id,
                            (
                                f"Historical run gap exceeded cadence+grace; "
                                f"deadline={deadline.isoformat()} "
                                f"observed={current.isoformat()}."
                            ),
                        )
                    )
                anchor = current

            final_deadline = (
                first_deadline if not rows else anchor + cadence + grace
            )
            if end > final_deadline:
                missed_cycle_count += 1
                violations.append(
                    OperationalFinding(
                        SOAK_MISSED_CYCLE,
                        SEVERITY_CRITICAL,
                        watch_id,
                        (
                            f"No execution observed by final deadline "
                            f"{final_deadline.isoformat()} before window end."
                        ),
                    )
                )

    completed = sum(str(row["status"]) == "COMPLETED" for row in window_runs)
    failed = sum(str(row["status"]) == "FAILED" for row in window_runs)
    running = sum(str(row["status"]) == "RUNNING" for row in window_runs)
    recovered = sum(bool(row["recovered"]) for row in window_runs)
    error_distribution = Counter(
        classify_operational_error(row["error"])
        for row in window_runs
        if str(row["status"]) == "FAILED"
    )

    if failed:
        violations.append(
            OperationalFinding(
                SOAK_FAILED_EXECUTIONS,
                SEVERITY_DEGRADED,
                "soak-window",
                f"{failed} failed execution(s) occurred in the window.",
            )
        )
    if running:
        violations.append(
            OperationalFinding(
                SOAK_RUNNING_EXECUTIONS,
                SEVERITY_DEGRADED,
                "soak-window",
                f"{running} execution(s) remain RUNNING at evidence evaluation.",
            )
        )

    integrity = check_sqlite_integrity(path)
    clean = (
        missed_cycle_count == 0
        and failed == 0
        and running == 0
        and integrity.ok
    )
    return SoakWindowReport(
        started_at=start,
        ended_at=end,
        duration_seconds=int((end - start).total_seconds()),
        clean=clean,
        run_count=len(window_runs),
        completed_run_count=completed,
        failed_run_count=failed,
        running_run_count=running,
        recovered_run_count=recovered,
        missed_cycle_count=missed_cycle_count,
        error_class_distribution=dict(sorted(error_distribution.items())),
        violations=tuple(
            sorted(violations, key=lambda item: (item.severity, item.code, item.subject))
        ),
        integrity=integrity,
    )
