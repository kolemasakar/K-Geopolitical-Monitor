"""Database initialization and canonical migration execution."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator, Iterable


RUNTIME_BUSY_TIMEOUT_MS = 5_000
RUNTIME_JOURNAL_MODE = "delete"
RUNTIME_SYNCHRONOUS = "FULL"
RUNTIME_ISOLATION_LEVEL = "DEFERRED"


def _default_migrations_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "migrations"


def _migration_files(migrations_dir: Path) -> Iterable[Path]:
    return sorted(path for path in migrations_dir.glob("*.sql") if path.is_file())


def _configure_runtime_connection(connection: sqlite3.Connection) -> sqlite3.Connection:
    """Apply and verify the E9A owner-only SQLite connection profile."""

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA busy_timeout = {RUNTIME_BUSY_TIMEOUT_MS}")
    connection.execute(f"PRAGMA synchronous = {RUNTIME_SYNCHRONOUS}")

    foreign_keys = int(connection.execute("PRAGMA foreign_keys").fetchone()[0])
    busy_timeout = int(connection.execute("PRAGMA busy_timeout").fetchone()[0])
    synchronous = int(connection.execute("PRAGMA synchronous").fetchone()[0])
    journal_mode = str(connection.execute("PRAGMA journal_mode").fetchone()[0]).lower()

    if foreign_keys != 1:
        raise RuntimeError("SQLite runtime profile failed to enable foreign keys")
    if busy_timeout != RUNTIME_BUSY_TIMEOUT_MS:
        raise RuntimeError("SQLite runtime profile failed to set busy_timeout")
    if synchronous != 2:  # SQLite numeric value for FULL.
        raise RuntimeError("SQLite runtime profile failed to set synchronous=FULL")
    if journal_mode != RUNTIME_JOURNAL_MODE:
        raise RuntimeError(
            "SQLite runtime journal_mode differs from the validated E9A profile: "
            f"expected {RUNTIME_JOURNAL_MODE}, got {journal_mode}"
        )

    return connection


def connect_runtime_database(path: str | Path) -> sqlite3.Connection:
    """Open one writable runtime connection with explicit bounded contention."""

    connection = sqlite3.connect(
        Path(path),
        timeout=RUNTIME_BUSY_TIMEOUT_MS / 1000,
        isolation_level=RUNTIME_ISOLATION_LEVEL,
    )
    try:
        return _configure_runtime_connection(connection)
    except BaseException:
        connection.close()
        raise


@contextmanager
def runtime_database_connection(path: str | Path) -> Iterator[sqlite3.Connection]:
    """Yield a profiled runtime connection and always close it afterward."""

    connection = connect_runtime_database(path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def apply_migrations(connection: sqlite3.Connection, migrations_dir: str | Path | None = None) -> None:
    directory = Path(migrations_dir) if migrations_dir is not None else _default_migrations_dir()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    applied = {
        row[0]
        for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
    }

    for migration in _migration_files(directory):
        version = migration.name
        if version in applied:
            continue

        connection.executescript(migration.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO schema_migrations(version) VALUES (?)",
            (version,),
        )


def initialize_database(
    path: str = "data/kgeopolitical_monitor.db",
    migrations_dir: str | Path | None = None,
) -> None:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    bootstrap_connection = sqlite3.connect(
        db_path,
        timeout=RUNTIME_BUSY_TIMEOUT_MS / 1000,
        isolation_level=RUNTIME_ISOLATION_LEVEL,
    )
    try:
        journal_mode = str(
            bootstrap_connection.execute(
                f"PRAGMA journal_mode = {RUNTIME_JOURNAL_MODE}"
            ).fetchone()[0]
        ).lower()
        if journal_mode != RUNTIME_JOURNAL_MODE:
            raise RuntimeError(
                "SQLite runtime profile failed to establish journal_mode="
                f"{RUNTIME_JOURNAL_MODE}"
            )
        _configure_runtime_connection(bootstrap_connection)
        with bootstrap_connection:
            bootstrap_connection.execute(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            apply_migrations(bootstrap_connection, migrations_dir=migrations_dir)
    finally:
        bootstrap_connection.close()
