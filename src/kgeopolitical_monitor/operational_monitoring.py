"""M5 project-local operational monitoring runtime foundation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from uuid import uuid4

from .database import initialize_database
from .runtime_storage import RuntimeStoragePolicy


RUNNING = "RUNNING"
COMPLETED = "COMPLETED"
FAILED = "FAILED"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Operational monitoring timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class MonitoringWatch:
    watch_id: str
    name: str
    query: str
    cadence_minutes: int
    enabled: bool = True
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.watch_id.strip():
            raise ValueError("watch_id must not be empty")
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.query.strip():
            raise ValueError("query must not be empty")
        if self.cadence_minutes <= 0:
            raise ValueError("cadence_minutes must be positive")
        _normalize_time(self.created_at)


@dataclass(frozen=True)
class MonitoringRun:
    run_id: str
    watch_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    result_count: int = 0
    error: str | None = None


class SQLiteOperationalMonitoringRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        initialize_database(str(database_path))

    def save_watch(self, watch: MonitoringWatch) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO monitoring_watches(
                    watch_id, name, query, cadence_minutes, enabled, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    watch.watch_id,
                    watch.name,
                    watch.query,
                    watch.cadence_minutes,
                    int(watch.enabled),
                    _normalize_time(watch.created_at).isoformat(),
                ),
            )

    def get_watch(self, watch_id: str) -> MonitoringWatch | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT watch_id, name, query, cadence_minutes, enabled, created_at
                FROM monitoring_watches
                WHERE watch_id = ?
                """,
                (watch_id,),
            ).fetchone()

        if row is None:
            return None
        return MonitoringWatch(
            watch_id=row[0],
            name=row[1],
            query=row[2],
            cadence_minutes=int(row[3]),
            enabled=bool(row[4]),
            created_at=datetime.fromisoformat(row[5]),
        )

    def list_watches(self, enabled_only: bool = False) -> list[MonitoringWatch]:
        query = (
            "SELECT watch_id, name, query, cadence_minutes, enabled, created_at "
            "FROM monitoring_watches"
        )
        params: tuple[object, ...] = ()
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY watch_id"

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            MonitoringWatch(
                watch_id=row[0],
                name=row[1],
                query=row[2],
                cadence_minutes=int(row[3]),
                enabled=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]),
            )
            for row in rows
        ]

    def save_run(self, run: MonitoringRun) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO monitoring_runs(
                    run_id, watch_id, status, started_at, completed_at, result_count, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.watch_id,
                    run.status,
                    _normalize_time(run.started_at).isoformat(),
                    _normalize_time(run.completed_at).isoformat()
                    if run.completed_at is not None
                    else None,
                    run.result_count,
                    run.error,
                ),
            )

    def latest_run(self, watch_id: str) -> MonitoringRun | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT run_id, watch_id, status, started_at, completed_at, result_count, error
                FROM monitoring_runs
                WHERE watch_id = ?
                ORDER BY started_at DESC, run_id DESC
                LIMIT 1
                """,
                (watch_id,),
            ).fetchone()

        if row is None:
            return None
        return MonitoringRun(
            run_id=row[0],
            watch_id=row[1],
            status=row[2],
            started_at=datetime.fromisoformat(row[3]),
            completed_at=datetime.fromisoformat(row[4]) if row[4] else None,
            result_count=int(row[5]),
            error=row[6],
        )

    def update_run(
        self,
        run_id: str,
        status: str,
        completed_at: datetime,
        result_count: int = 0,
        error: str | None = None,
    ) -> None:
        completed_at = _normalize_time(completed_at)
        if status not in {COMPLETED, FAILED}:
            raise ValueError("run may only transition to COMPLETED or FAILED")
        if result_count < 0:
            raise ValueError("result_count must not be negative")

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE monitoring_runs
                SET status = ?, completed_at = ?, result_count = ?, error = ?
                WHERE run_id = ? AND status = 'RUNNING'
                """,
                (status, completed_at.isoformat(), result_count, error, run_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("run does not exist or is not RUNNING")


class OperationalMonitoringRuntime:
    def __init__(
        self,
        project_root: str | Path,
        database_path: str | Path | None = None,
    ):
        self.storage_policy = RuntimeStoragePolicy(Path(project_root))
        self.database_path = self.storage_policy.resolve_database(database_path)
        self.repository = SQLiteOperationalMonitoringRepository(self.database_path)

    def create_watch(
        self,
        name: str,
        query: str,
        cadence_minutes: int,
        *,
        watch_id: str | None = None,
        enabled: bool = True,
        created_at: datetime | None = None,
    ) -> MonitoringWatch:
        watch = MonitoringWatch(
            watch_id=watch_id or f"watch-{uuid4().hex}",
            name=name,
            query=query,
            cadence_minutes=cadence_minutes,
            enabled=enabled,
            created_at=created_at or utc_now(),
        )
        self.repository.save_watch(watch)
        return watch

    def due_watches(self, now: datetime | None = None) -> list[MonitoringWatch]:
        current = _normalize_time(now or utc_now())
        due: list[MonitoringWatch] = []

        for watch in self.repository.list_watches(enabled_only=True):
            latest = self.repository.latest_run(watch.watch_id)
            if latest is None:
                due.append(watch)
                continue
            if latest.status == RUNNING:
                continue

            next_due = _normalize_time(latest.started_at) + timedelta(
                minutes=watch.cadence_minutes
            )
            if current >= next_due:
                due.append(watch)

        return due

    def start_run(
        self,
        watch_id: str,
        *,
        run_id: str | None = None,
        started_at: datetime | None = None,
    ) -> MonitoringRun:
        watch = self.repository.get_watch(watch_id)
        if watch is None:
            raise ValueError("watch does not exist")
        if not watch.enabled:
            raise ValueError("disabled watch cannot start a run")

        existing = self.repository.latest_run(watch_id)
        if existing is not None and existing.status == RUNNING:
            raise ValueError("watch already has a RUNNING run")

        run = MonitoringRun(
            run_id=run_id or f"run-{uuid4().hex}",
            watch_id=watch_id,
            status=RUNNING,
            started_at=_normalize_time(started_at or utc_now()),
        )
        self.repository.save_run(run)
        return run

    def complete_run(
        self,
        run_id: str,
        *,
        result_count: int = 0,
        completed_at: datetime | None = None,
    ) -> None:
        self.repository.update_run(
            run_id,
            COMPLETED,
            completed_at or utc_now(),
            result_count=result_count,
        )

    def fail_run(
        self,
        run_id: str,
        error: str,
        *,
        completed_at: datetime | None = None,
    ) -> None:
        if not error.strip():
            raise ValueError("failed run requires an error")
        self.repository.update_run(
            run_id,
            FAILED,
            completed_at or utc_now(),
            error=error,
        )
