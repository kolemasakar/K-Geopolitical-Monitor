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
        monitoring_run_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(monitoring_runs)").fetchall()
        }

    assert {
        "metadata",
        "schema_migrations",
        "sources",
        "raw_items",
        "events",
        "claims",
        "evidence",
        "monitoring_watches",
        "monitoring_runs",
        "operational_findings",
        "pilot_coverage_reports",
        "source_collection_runs",
        "live_source_provenance",
        "live_analysis_runs",
        "live_analysis_claims",
        "live_analysis_evidence",
    }.issubset(tables)
    assert {"retry_count", "recovered"}.issubset(monitoring_run_columns)
    assert applied == {
        "001_initial_schema.sql",
        "002_evidence_verification_schema.sql",
        "003_operational_monitoring.sql",
        "004_operational_cycle_and_findings.sql",
        "005_controlled_pilot_coverage.sql",
        "006_live_source_collection.sql",
        "007_live_end_to_end_analysis.sql",
    }
