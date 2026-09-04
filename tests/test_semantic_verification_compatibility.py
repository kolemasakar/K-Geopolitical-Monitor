import sqlite3

from kgeopolitical_monitor.confidence_engine import calculate_confidence
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.verification import evaluate_claim


def test_legacy_count_based_verification_remains_readable_but_is_compatibility_only():
    assert evaluate_claim(1) == "DETECTED"
    assert evaluate_claim(2) == "PARTLY_VERIFIED"


def test_legacy_scalar_confidence_remains_readable_but_is_not_p13_5_schema(tmp_path):
    legacy_score = calculate_confidence(
        evidence_items=[
            {"source_id": "publisher-a", "reliability": "HIGH"},
            {"source_id": "publisher-b", "reliability": "HIGH"},
        ],
        contradictions=[],
    )
    assert 0.0 <= legacy_score <= 1.0

    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    with sqlite3.connect(runtime.database_path) as connection:
        confidence_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(semantic_factual_confidence_versions)"
            ).fetchall()
        }
        decision_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(semantic_verification_decision_versions)"
            ).fetchall()
        }

    assert "confidence" not in confidence_columns
    assert "confidence_score" not in confidence_columns
    assert "factual_confidence" not in confidence_columns
    assert "coverage_confidence" not in confidence_columns
    assert "independent_origin_count" not in confidence_columns
    assert "source_reliability" not in confidence_columns
    assert "confidence" not in decision_columns
    assert "confidence_score" not in decision_columns
    assert "coverage_confidence" not in decision_columns
