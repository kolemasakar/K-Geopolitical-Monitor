"""Database initialization and persistence foundation."""

from pathlib import Path
import sqlite3


def initialize_database(path: str = "data/kgeopolitical_monitor.db") -> None:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
