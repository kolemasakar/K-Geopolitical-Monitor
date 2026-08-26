"""Database initialization and canonical migration execution."""

from pathlib import Path
import sqlite3
from typing import Iterable


def _default_migrations_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "migrations"


def _migration_files(migrations_dir: Path) -> Iterable[Path]:
    return sorted(path for path in migrations_dir.glob("*.sql") if path.is_file())


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

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        apply_migrations(connection, migrations_dir=migrations_dir)
