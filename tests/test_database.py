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
        "monitoring_watch_alert_policies",
        "strategic_alerts",
        "strategic_alert_events",
        "region_catalog",
        "language_catalog",
        "watch_region_language_scopes",
        "observation_region_language",
        "region_language_coverage_reports",
        "graph_nodes",
        "graph_edges",
        "graph_edge_evidence",
        "graph_edge_history",
        "forecasts",
        "forecast_versions",
        "forecast_scenario_versions",
        "forecast_version_inputs",
        "forecast_outcomes",
        "forecast_evaluations",
        "forecast_calibration_runs",
        "forecast_calibration_buckets",
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
        "008_strategic_alerts.sql",
        "009_region_language_coverage.sql",
        "010_advanced_geopolitical_graph.sql",
        "011_advanced_forecasting.sql",
        "012_forecast_provenance_inputs.sql",
        "013_forecast_outcomes_evaluations.sql",
        "014_forecast_calibration_history.sql",
    }
