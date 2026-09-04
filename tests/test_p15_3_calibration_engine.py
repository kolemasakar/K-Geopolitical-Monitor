from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.forecast_calibration_contract import (
    OUTCOME_AMBIGUOUS,
    OUTCOME_PARTIAL,
    OUTCOME_RESOLVED,
    OUTCOME_UNRESOLVED,
)
from kgeopolitical_monitor.forecast_calibration_engine import (
    CalibrationEngineError,
    P15_3_GATE,
    ProvenanceBoundCalibrationEngine,
    reliability_bucket,
)
from kgeopolitical_monitor.forecast_outcome_persistence import (
    ForecastOutcomeAssessment,
    OutcomeEvidenceReference,
    SQLiteForecastOutcomeAssessmentRepository,
)
from kgeopolitical_monitor.forecast_outcome_resolution import ProvenanceBoundOutcomeResolver


NOW = datetime(2026, 9, 4, 19, 0, tzinfo=timezone.utc)


def _seed_forecast(db_path, forecast_id="forecast-p15-3"):
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


def _seed_version_and_scenarios(db_path, forecast_id="forecast-p15-3"):
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """INSERT INTO forecast_versions(
                   forecast_version_id, forecast_id, version_number,
                   input_snapshot_json, provenance_refs_json, assumptions_json,
                   change_reason, created_at
               ) VALUES (?, ?, ?, '{}', '[]', '[]', ?, ?)""",
            ("fv-p15-3", forecast_id, 1, "P15.3 test version", NOW.isoformat()),
        )
        connection.executemany(
            """INSERT INTO forecast_scenario_versions(
                   scenario_version_id, forecast_version_id, scenario_type, label,
                   raw_probability, calibrated_probability, scenario_confidence,
                   drivers_json, constraints_json, triggers_json, inhibitors_json,
                   uncertainty_factors_json, invalidation_signals_json
               ) VALUES (?, ?, ?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', '[]', '[]')""",
            [
                ("sv-baseline", "fv-p15-3", "baseline", "Baseline", 0.8, 0.7, 0.01),
                ("sv-positive", "fv-p15-3", "positive", "Positive", 0.2, 0.3, 0.99),
            ],
        )


def _seed_raw_item(db_path):
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO raw_items(id, title, content, collected_at) VALUES (?, ?, ?, ?)",
            ("raw-p15-3", "Outcome evidence", "Persisted outcome evidence", NOW.isoformat()),
        )


def _seed_legacy_outcome(db_path, state="OBSERVED", observed_scenario_type="baseline"):
    if state == "NOT_OBSERVED":
        observed_scenario_type = None
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """INSERT INTO forecast_outcomes(
                   outcome_id, forecast_id, resolved_at, outcome_state,
                   observed_scenario_type, evidence_refs_json, explanation, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "legacy-p15-3",
                "forecast-p15-3",
                NOW.isoformat(),
                state,
                observed_scenario_type,
                '["raw-p15-3"]',
                f"Legacy {state} result",
                NOW.isoformat(),
            ),
        )
    return "legacy-p15-3"


def _seed_binary_scoreable_case(db_path, state="OBSERVED"):
    _seed_forecast(db_path)
    _seed_version_and_scenarios(db_path)
    _seed_raw_item(db_path)
    legacy_outcome_id = _seed_legacy_outcome(db_path, state=state)
    assessment = ProvenanceBoundOutcomeResolver(db_path).resolve(
        "forecast-p15-3",
        assessed_at=NOW,
        explanation="Persisted evidence resolves the binary forecast outcome.",
        legacy_outcome_id=legacy_outcome_id,
        evidence=(OutcomeEvidenceReference("RAW_ITEM", "raw-p15-3", "OUTCOME_EVIDENCE"),),
    )
    return assessment


def test_p15_3_gate_name():
    assert P15_3_GATE == "P15_3_CALIBRATION_ENGINE_VALIDATED"


def test_migration_029_is_applied_additively(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        migrations = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert "029_forecast_calibration_observations.sql" in migrations
    assert "forecast_calibration_observations" in tables
    assert "forecast_evaluations" in tables
    assert "forecast_calibration_runs" in tables
    assert "forecast_calibration_buckets" in tables


@pytest.mark.parametrize(
    "resolution_state",
    [OUTCOME_UNRESOLVED, OUTCOME_PARTIAL, OUTCOME_AMBIGUOUS],
)
def test_non_resolved_assessments_fail_closed(tmp_path, resolution_state):
    db_path = tmp_path / f"{resolution_state.lower()}.db"
    _seed_forecast(db_path)
    repository = SQLiteForecastOutcomeAssessmentRepository(db_path)
    assessment = ForecastOutcomeAssessment.create(
        "forecast-p15-3",
        1,
        resolution_state,
        explanation="This assessment is deliberately not scoreable.",
        assessed_at=NOW,
    )
    repository.save(assessment)
    with pytest.raises(CalibrationEngineError, match="not scoreable"):
        ProvenanceBoundCalibrationEngine(db_path).score_assessment(
            assessment.assessment_id,
            "fv-does-not-matter",
            evaluated_at=NOW,
        )


def test_resolved_without_binary_legacy_outcome_fails_closed(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    _seed_raw_item(db_path)
    repository = SQLiteForecastOutcomeAssessmentRepository(db_path)
    assessment = ForecastOutcomeAssessment.create(
        "forecast-p15-3",
        1,
        OUTCOME_RESOLVED,
        evidence=(OutcomeEvidenceReference("RAW_ITEM", "raw-p15-3"),),
        explanation="Resolution lifecycle alone does not supply a binary scoring target.",
        assessed_at=NOW,
    )
    repository.save(assessment)
    with pytest.raises(CalibrationEngineError, match="binary legacy outcome link"):
        ProvenanceBoundCalibrationEngine(db_path).score_assessment(
            assessment.assessment_id,
            "fv-does-not-matter",
            evaluated_at=NOW,
        )


def test_external_only_resolved_assessment_is_not_scoreable(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    _seed_version_and_scenarios(db_path)
    _seed_raw_item(db_path)
    legacy_outcome_id = _seed_legacy_outcome(db_path)
    repository = SQLiteForecastOutcomeAssessmentRepository(db_path)
    assessment = ForecastOutcomeAssessment.create(
        "forecast-p15-3",
        1,
        OUTCOME_RESOLVED,
        evidence=(OutcomeEvidenceReference("EXTERNAL_REFERENCE", "https://example.invalid/outcome"),),
        explanation="P15.3 must preserve the P15.2 persisted-provenance boundary.",
        assessed_at=NOW,
        legacy_outcome_id=legacy_outcome_id,
    )
    repository.save(assessment)
    with pytest.raises(CalibrationEngineError, match="persisted OUTCOME_EVIDENCE"):
        ProvenanceBoundCalibrationEngine(db_path).score_assessment(
            assessment.assessment_id,
            "fv-p15-3",
            evaluated_at=NOW,
        )


def test_observed_outcome_scores_raw_and_calibrated_probabilities_separately(tmp_path):
    db_path = tmp_path / "kgm.db"
    assessment = _seed_binary_scoreable_case(db_path, state="OBSERVED")
    observations = ProvenanceBoundCalibrationEngine(db_path).score_assessment(
        assessment.assessment_id,
        "fv-p15-3",
        evaluated_at=NOW,
    )
    by_type = {item.scenario_type: item for item in observations}
    assert set(by_type) == {"baseline", "positive"}

    baseline = by_type["baseline"]
    assert baseline.observed_value == 1.0
    assert baseline.raw_probability == pytest.approx(0.8)
    assert baseline.calibrated_probability == pytest.approx(0.7)
    assert baseline.brier_score_raw == pytest.approx(0.04)
    assert baseline.brier_score_calibrated == pytest.approx(0.09)
    assert baseline.raw_reliability_bucket == 8
    assert baseline.calibrated_reliability_bucket == 7

    positive = by_type["positive"]
    assert positive.observed_value == 0.0
    assert positive.brier_score_raw == pytest.approx(0.04)
    assert positive.brier_score_calibrated == pytest.approx(0.09)
    assert positive.raw_reliability_bucket == 2
    assert positive.calibrated_reliability_bucket == 3


def test_not_observed_outcome_maps_every_scenario_to_zero(tmp_path):
    db_path = tmp_path / "kgm.db"
    assessment = _seed_binary_scoreable_case(db_path, state="NOT_OBSERVED")
    observations = ProvenanceBoundCalibrationEngine(db_path).score_assessment(
        assessment.assessment_id,
        "fv-p15-3",
        evaluated_at=NOW,
    )
    by_type = {item.scenario_type: item for item in observations}
    assert all(item.observed_value == 0.0 for item in observations)
    assert by_type["baseline"].brier_score_raw == pytest.approx(0.64)
    assert by_type["baseline"].brier_score_calibrated == pytest.approx(0.49)
    assert by_type["positive"].brier_score_raw == pytest.approx(0.04)
    assert by_type["positive"].brier_score_calibrated == pytest.approx(0.09)


def test_reliability_bucket_boundary_and_validation():
    assert reliability_bucket(0.0, 10) == 0
    assert reliability_bucket(0.0999, 10) == 0
    assert reliability_bucket(0.1, 10) == 1
    assert reliability_bucket(0.9999, 10) == 9
    assert reliability_bucket(1.0, 10) == 9
    with pytest.raises(CalibrationEngineError, match="between 0 and 1"):
        reliability_bucket(1.01, 10)
    with pytest.raises(CalibrationEngineError, match="at least 2"):
        reliability_bucket(0.5, 1)


def test_scenario_confidence_is_not_used_as_probability(tmp_path):
    db_path = tmp_path / "kgm.db"
    assessment = _seed_binary_scoreable_case(db_path, state="OBSERVED")
    observations = ProvenanceBoundCalibrationEngine(db_path).score_assessment(
        assessment.assessment_id,
        "fv-p15-3",
        evaluated_at=NOW,
    )
    by_type = {item.scenario_type: item for item in observations}
    # Seed confidence is 0.01 for baseline and 0.99 for positive. Scores must
    # still follow the separate raw/calibrated probabilities 0.8/0.7 and 0.2/0.3.
    assert by_type["baseline"].raw_probability == pytest.approx(0.8)
    assert by_type["baseline"].calibrated_probability == pytest.approx(0.7)
    assert by_type["positive"].raw_probability == pytest.approx(0.2)
    assert by_type["positive"].calibrated_probability == pytest.approx(0.3)


def test_calibration_observation_is_idempotent_and_append_only(tmp_path):
    db_path = tmp_path / "kgm.db"
    assessment = _seed_binary_scoreable_case(db_path)
    engine = ProvenanceBoundCalibrationEngine(db_path)
    first = engine.score_assessment(
        assessment.assessment_id,
        "fv-p15-3",
        evaluated_at=NOW,
    )
    second = engine.score_assessment(
        assessment.assessment_id,
        "fv-p15-3",
        evaluated_at=NOW + timedelta(hours=1),
    )
    assert [item.observation_id for item in first] == [item.observation_id for item in second]
    assert [item.evaluated_at for item in first] == [item.evaluated_at for item in second]

    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM forecast_calibration_observations"
        ).fetchone()[0]
        assert count == 2
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE forecast_calibration_observations SET raw_probability = 0.5"
            )
        connection.rollback()
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM forecast_calibration_observations")


def test_calibration_engine_does_not_write_factual_verification_state(tmp_path):
    db_path = tmp_path / "kgm.db"
    assessment = _seed_binary_scoreable_case(db_path)
    with sqlite3.connect(db_path) as connection:
        before = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0]
    ProvenanceBoundCalibrationEngine(db_path).score_assessment(
        assessment.assessment_id,
        "fv-p15-3",
        evaluated_at=NOW,
    )
    with sqlite3.connect(db_path) as connection:
        after = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0]
    assert after == before


def test_p15_3_schema_contains_no_truth_promotion_fields(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(forecast_calibration_observations)"
            )
        }
    forbidden = {
        "verification_status",
        "verification_state",
        "factual_confidence",
        "independent_origin_count",
        "coverage_confidence",
        "source_count",
        "host_count",
        "domain_count",
        "scenario_confidence",
    }
    assert columns.isdisjoint(forbidden)
