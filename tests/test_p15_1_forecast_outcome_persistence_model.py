from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.forecast_calibration_contract import (
    OUTCOME_RESOLVED,
    OUTCOME_UNRESOLVED,
)
from kgeopolitical_monitor.forecast_outcome_persistence import (
    ForecastOutcomeAssessment,
    OutcomeEvidenceReference,
    P15_1_GATE,
    SQLiteForecastOutcomeAssessmentRepository,
)


NOW = datetime(2026, 9, 4, 17, 30, tzinfo=timezone.utc)


def _seed_forecast(db_path, forecast_id="forecast-p15-1"):
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """INSERT INTO forecasts(
                   forecast_id, target_key, question, horizon, evaluation_deadline,
                   status, created_at, updated_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                forecast_id,
                f"target-{forecast_id}",
                "Will the target event occur?",
                "short_term",
                "2026-09-10T00:00:00+00:00",
                "ACTIVE",
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )


def test_p15_1_gate_name():
    assert P15_1_GATE == "P15_1_FORECAST_OUTCOME_PERSISTENCE_MODEL_VALIDATED"


def test_migration_028_is_applied_and_additive(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        migrations = {
            row[0] for row in connection.execute("SELECT version FROM schema_migrations")
        }
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert "028_forecast_outcome_assessment_history.sql" in migrations
    assert "forecast_outcomes" in tables
    assert "forecast_evaluations" in tables
    assert "forecast_outcome_assessments" in tables
    assert "forecast_outcome_assessment_evidence" in tables


def test_resolution_state_is_separate_from_legacy_outcome_state(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    repository = SQLiteForecastOutcomeAssessmentRepository(db_path)
    assessment = ForecastOutcomeAssessment.create(
        "forecast-p15-1",
        1,
        OUTCOME_UNRESOLVED,
        explanation="Evaluation deadline has not yet produced sufficient outcome evidence.",
        assessed_at=NOW,
    )
    repository.save(assessment)
    stored = repository.list_for_forecast("forecast-p15-1")
    assert stored[0].resolution_state == OUTCOME_UNRESOLVED
    with sqlite3.connect(db_path) as connection:
        legacy_count = connection.execute("SELECT COUNT(*) FROM forecast_outcomes").fetchone()[0]
    assert legacy_count == 0


def test_resolved_assessment_requires_explicit_outcome_evidence(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    with pytest.raises(ValueError, match="requires outcome evidence"):
        ForecastOutcomeAssessment.create(
            "forecast-p15-1",
            1,
            OUTCOME_RESOLVED,
            explanation="Resolved without evidence is forbidden.",
            assessed_at=NOW,
        )


def test_append_only_assessment_history_and_typed_provenance(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    repository = SQLiteForecastOutcomeAssessmentRepository(db_path)
    first = ForecastOutcomeAssessment.create(
        "forecast-p15-1",
        1,
        OUTCOME_UNRESOLVED,
        evidence=(
            OutcomeEvidenceReference("EXTERNAL_REFERENCE", "official-release-1", "RESOLUTION_CONTEXT"),
        ),
        explanation="Initial outcome review remains unresolved.",
        assessed_at=NOW,
    )
    second = ForecastOutcomeAssessment.create(
        "forecast-p15-1",
        2,
        OUTCOME_RESOLVED,
        evidence=(
            OutcomeEvidenceReference("RAW_ITEM", "raw-item-123"),
            OutcomeEvidenceReference("SEMANTIC_CLAIM", "claim-456"),
        ),
        explanation="Later evidence supports a scoreable resolution state.",
        assessed_at=NOW,
    )
    repository.save(first)
    repository.save(second)
    stored = repository.list_for_forecast("forecast-p15-1")
    assert [item.assessment_sequence for item in stored] == [1, 2]
    assert stored[1].resolution_state == OUTCOME_RESOLVED
    assert [item.evidence_kind for item in stored[1].evidence] == ["RAW_ITEM", "SEMANTIC_CLAIM"]

    with sqlite3.connect(db_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE forecast_outcome_assessments SET explanation = 'rewrite' WHERE assessment_id = ?",
                (first.assessment_id,),
            )


def test_legacy_outcome_link_must_match_same_forecast(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path, "forecast-a")
    _seed_forecast(db_path, "forecast-b")
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """INSERT INTO forecast_outcomes(
                   outcome_id, forecast_id, resolved_at, outcome_state,
                   observed_scenario_type, evidence_refs_json, explanation, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "outcome-a",
                "forecast-a",
                NOW.isoformat(),
                "NOT_OBSERVED",
                None,
                "[]",
                "Legacy result",
                NOW.isoformat(),
            ),
        )
    repository = SQLiteForecastOutcomeAssessmentRepository(db_path)
    assessment = ForecastOutcomeAssessment.create(
        "forecast-b",
        1,
        OUTCOME_RESOLVED,
        evidence=(OutcomeEvidenceReference("EXTERNAL_REFERENCE", "evidence-1"),),
        explanation="Cross-forecast compatibility link must fail.",
        assessed_at=NOW,
        legacy_outcome_id="outcome-a",
    )
    with pytest.raises(ValueError, match="different forecast"):
        repository.save(assessment)


def test_p15_1_schema_contains_no_factual_verification_fields(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(forecast_outcome_assessments)")
        }
    forbidden = {
        "verification_status",
        "factual_confidence",
        "independent_origin_count",
        "coverage_confidence",
        "source_count",
        "host_count",
        "domain_count",
        "forecast_probability",
    }
    assert columns.isdisjoint(forbidden)
