"""Project-local SQLite backup and restore helpers for E4 deployment validation."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from .operational_monitoring import OperationalMonitoringRuntime
from .runtime_storage import RuntimeStoragePolicy


def _integrity_check(database_path: Path) -> None:
    with sqlite3.connect(database_path) as connection:
        row = connection.execute("PRAGMA integrity_check").fetchone()
    if row is None or str(row[0]).casefold() != "ok":
        raise RuntimeError("SQLite integrity check failed")


def backup_project_database(
    project_root: str | Path,
    backup_path: str | Path,
) -> Path:
    """Create a non-overwriting consistent SQLite backup of project-local runtime state."""

    runtime = OperationalMonitoringRuntime(Path(project_root))
    source = runtime.database_path.resolve()
    destination = Path(backup_path).expanduser().resolve()

    if destination == source:
        raise ValueError("backup destination must differ from the runtime database")
    if destination.exists():
        raise FileExistsError("backup destination already exists")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as source_connection, sqlite3.connect(
        destination
    ) as destination_connection:
        source_connection.backup(destination_connection)

    _integrity_check(destination)
    return destination


def restore_project_database(
    backup_path: str | Path,
    project_root: str | Path,
) -> Path:
    """Restore a validated backup into a fresh project-local data directory."""

    source = Path(backup_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError("backup database does not exist")
    _integrity_check(source)

    policy = RuntimeStoragePolicy(Path(project_root))
    destination = policy.resolve_database().resolve()
    if destination.exists():
        raise FileExistsError("restore refuses to overwrite an existing runtime database")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as source_connection, sqlite3.connect(
        destination
    ) as destination_connection:
        source_connection.backup(destination_connection)

    _integrity_check(destination)
    return destination
