import sqlite3

from kgeopolitical_monitor.database import initialize_database


def test_database_initialization_applies_canonical_migrations(tmp_path):
    db = tmp_path / "test.db"

    initialize_database(str(db))
    initialize_database(str(db))

    assert db.exists()

    with sqlite3.connect(db) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        applied = {
            row[0]
            for row in connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            ).fetchall()
        }

    assert {
        "metadata",
        "schema_migrations",
        "sources",
        "raw_items",
        "events",
        "claims",
        "evidence",
    }.issubset(tables)
    assert applied == {
        "001_initial_schema.sql",
        "002_evidence_verification_schema.sql",
    }
