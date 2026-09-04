from pathlib import Path
import sqlite3

from kgeopolitical_monitor.database import initialize_database


ROOT = Path(__file__).resolve().parents[1]


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
        "source_collection_attempts",
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
        "forecast_outcome_assessments",
        "forecast_outcome_assessment_evidence",
        "forecast_calibration_observations",
        "forecast_performance_aggregates",
        "forecast_performance_aggregate_observations",
        "forecast_performance_drift_comparisons",
        "report_snapshots",
        "report_sections",
        "report_references",
        "operational_coverage_contracts",
        "operational_coverage_requirements",
        "operational_coverage_snapshots",
        "operational_coverage_requirement_results",
        "raw_item_translations",
        "source_reputation_history",
        "research_audit_runs",
        "research_query_executions",
        "research_artifact_hashes",
        "research_provenance_annotations",
        "owner_runtime_health",
        "source_portfolio_versions",
        "semantic_claim_versions",
        "semantic_claim_links",
        "semantic_provenance_entity_versions",
        "semantic_claim_provenance_role_versions",
        "semantic_provenance_relation_versions",
        "semantic_evidence_relation_versions",
        "semantic_independence_assessment_versions",
        "semantic_contradiction_versions",
        "semantic_contradiction_evidence_links",
        "semantic_verification_policy_versions",
        "semantic_factual_confidence_versions",
        "semantic_verification_decision_versions",
        "delivery_intents",
        "delivery_intent_audit_events",
        "delivery_transport_attempts",
        "delivery_receipts",
    }.issubset(tables)
    assert {"retry_count", "recovered"}.issubset(monitoring_run_columns)

    expected_migrations = {
        path.name for path in (ROOT / "migrations").glob("*.sql") if path.is_file()
    }
    assert applied == expected_migrations
    assert "031_delivery_intent_audit.sql" in applied
