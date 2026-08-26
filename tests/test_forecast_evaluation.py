from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.advanced_forecasting import (
    ForecastRecord,
    ForecastVersion,
    ScenarioVersion,
    SQLiteAdvancedForecastRepository,
)
from kgeopolitical_monitor.forecast_evaluation import (
    AMBIGUOUS,
    OBSERVED,
    PARTIAL,
    ForecastOutcome,
    SQLiteForecastEvaluationRepository,
)
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType


NOW = datetime(2026, 8, 26, 18, 0, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)
RESOLVED_AT = DEADLINE + timedelta(hours=1)


def _seed_evidence(db):
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            ("source-outcome", "Outcome Source", "Official sources", "official"),
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES (?, ?, ?, ?, ?)",
            ("raw-outcome-1", "source-outcome", "Outcome evidence", "evidence", RESOLVED_AT.isoformat()),
        )


def _forecast(target_key="forecast-eval-1", horizon=ForecastHorizon.SHORT):
    return ForecastRecord.create(
        target_key,
        f"Outcome question for {target_key}",
        horizon,
        DEADLINE,
        created_at=NOW,
    )


def _save_version(repo, forecast, version_number=1, raw_baseline=0.60, calibrated_baseline=0.55):
    version = ForecastVersion.create(
        forecast.forecast_id,
        version_number,
        input_snapshot={"inputs": ["raw-outcome-1"]},
        provenance_refs=("SOURCE_EVIDENCE:raw-outcome-1",),
        assumptions=("Explicit assumption",),
        change_reason="Historical evaluation fixture",
        created_at=NOW + timedelta(hours=version_number - 1),
    )
    scenarios = (
        ScenarioVersion.create(
            version.forecast_version_id,
            ScenarioType.BASELINE,
            "Agreement announced",
            raw_baseline,
            calibrated_baseline,
            0.80,
            drivers=("Driver",),
            constraints=("Constraint",),
            triggers=("Trigger",),
            inhibitors=("Inhibitor",),
            uncertainty_factors=("Uncertainty",),
            invalidation_signals=("Invalidation",),
        ),
        ScenarioVersion.create(
            version.forecast_version_id,
            ScenarioType.NEGATIVE,
            "No agreement announced",
            1.0 - raw_baseline,
            1.0 - calibrated_baseline,
            0.65,
            drivers=("Delay",),
            constraints=("Deadline",),
            triggers=("Deadline passes",),
            inhibitors=("Breakthrough",),
            uncertainty_factors=("Private talks",),
            invalidation_signals=("Agreement signed",),
        ),
    )
    repo.save_version(version, scenarios)
    return version, scenarios


def _setup(tmp_path, target_key="forecast-eval-1", horizon=ForecastHorizon.SHORT):
    db = tmp_path / f"{target_key}.db"
    repo = SQLiteAdvancedForecastRepository(db)
    _seed_evidence(db)
    forecast = _forecast(target_key, horizon)
    repo.save_forecast(forecast)
    version, scenarios = _save_version(repo, forecast)
    return db, repo, forecast, version, scenarios


def test_forecast_outcome_is_durable_restart_safe_and_evidence_backed(tmp_path):
    db, _, forecast, _, _ = _setup(tmp_path)
    outcome_repo = SQLiteForecastEvaluationRepository(db)
    outcome = ForecastOutcome.create(
        forecast.forecast_id,
        RESOLVED_AT,
        OBSERVED,
        observed_scenario_type=ScenarioType.BASELINE,
        evidence_refs=("raw-outcome-1",),
        explanation="Official evidence confirms the baseline scenario.",
        created_at=RESOLVED_AT,
    )

    outcome_repo.save_outcome(outcome)
    outcome_repo.save_outcome(outcome)

    restarted = SQLiteForecastEvaluationRepository(db)
    assert restarted.get_outcome(outcome.outcome_id) == outcome


def test_unknown_outcome_evidence_reference_fails_closed(tmp_path):
    db, _, forecast, _, _ = _setup(tmp_path)
    outcome = ForecastOutcome.create(
        forecast.forecast_id,
        RESOLVED_AT,
        OBSERVED,
        observed_scenario_type=ScenarioType.BASELINE,
        evidence_refs=("raw-missing",),
        explanation="Missing evidence must fail.",
        created_at=RESOLVED_AT,
    )

    with pytest.raises(ValueError, match="unknown outcome evidence reference"):
        SQLiteForecastEvaluationRepository(db).save_outcome(outcome)

    assert SQLiteForecastEvaluationRepository(db).get_outcome(outcome.outcome_id) is None


def test_observed_outcome_evaluates_exact_version_with_existing_metric_helpers(tmp_path):
    db, _, forecast, version, _ = _setup(tmp_path)
    outcome_repo = SQLiteForecastEvaluationRepository(db)
    outcome = ForecastOutcome.create(
        forecast.forecast_id,
        RESOLVED_AT,
        OBSERVED,
        observed_scenario_type=ScenarioType.BASELINE,
        evidence_refs=("raw-outcome-1",),
        explanation="Baseline scenario observed.",
        created_at=RESOLVED_AT,
    )
    outcome_repo.save_outcome(outcome)

    evaluations = outcome_repo.evaluate_version(
        outcome.outcome_id,
        version.forecast_version_id,
        evaluated_at=RESOLVED_AT,
    )
    repeated = outcome_repo.evaluate_version(
        outcome.outcome_id,
        version.forecast_version_id,
        evaluated_at=RESOLVED_AT + timedelta(hours=1),
    )

    assert evaluations == repeated
    assert len(evaluations) == 2
    baseline = next(item for item in evaluations if item.scenario_type == ScenarioType.BASELINE.value)
    negative = next(item for item in evaluations if item.scenario_type == ScenarioType.NEGATIVE.value)

    assert baseline.observed_value == 1.0
    assert negative.observed_value == 0.0
    assert baseline.brier_score_raw == pytest.approx(0.16)
    assert baseline.brier_score_calibrated == pytest.approx(0.2025)
    assert negative.brier_score_raw == pytest.approx(0.16)
    assert negative.brier_score_calibrated == pytest.approx(0.2025)
    assert baseline.calibration_error_raw == pytest.approx(0.40)
    assert baseline.calibration_error_calibrated == pytest.approx(0.45)
    assert baseline.sample_count == 1


def test_partial_and_ambiguous_outcomes_do_not_create_false_binary_precision(tmp_path):
    for suffix, outcome_state in (("partial", PARTIAL), ("ambiguous", AMBIGUOUS)):
        db, _, forecast, version, _ = _setup(tmp_path / suffix, target_key=f"forecast-{suffix}")
        outcome_repo = SQLiteForecastEvaluationRepository(db)
        outcome = ForecastOutcome.create(
            forecast.forecast_id,
            RESOLVED_AT,
            outcome_state,
            observed_scenario_type=ScenarioType.BASELINE if outcome_state == PARTIAL else None,
            evidence_refs=("raw-outcome-1",),
            explanation=f"{outcome_state} outcome cannot support binary scoring.",
            created_at=RESOLVED_AT,
        )
        outcome_repo.save_outcome(outcome)
        evaluations = outcome_repo.evaluate_version(
            outcome.outcome_id,
            version.forecast_version_id,
            evaluated_at=RESOLVED_AT,
        )

        assert len(evaluations) == 2
        for item in evaluations:
            assert item.observed_value is None
            assert item.brier_score_raw is None
            assert item.brier_score_calibrated is None
            assert item.calibration_error_raw is None
            assert item.calibration_error_calibrated is None
            assert item.sample_count == 0


def test_evaluation_rejects_forecast_version_from_another_forecast(tmp_path):
    db, repo, forecast1, _, _ = _setup(tmp_path, target_key="forecast-link-1")
    forecast2 = _forecast("forecast-link-2")
    repo.save_forecast(forecast2)
    version2, _ = _save_version(repo, forecast2)

    outcome_repo = SQLiteForecastEvaluationRepository(db)
    outcome = ForecastOutcome.create(
        forecast1.forecast_id,
        RESOLVED_AT,
        OBSERVED,
        observed_scenario_type=ScenarioType.BASELINE,
        evidence_refs=("raw-outcome-1",),
        explanation="Outcome belongs to forecast one.",
        created_at=RESOLVED_AT,
    )
    outcome_repo.save_outcome(outcome)

    with pytest.raises(ValueError, match="different forecasts"):
        outcome_repo.evaluate_version(
            outcome.outcome_id,
            version2.forecast_version_id,
            evaluated_at=RESOLVED_AT,
        )


def test_horizon_aware_historical_summary_separates_scorable_and_unscorable(tmp_path):
    db, repo, forecast1, version1, _ = _setup(tmp_path, target_key="forecast-summary-1")
    outcome_repo = SQLiteForecastEvaluationRepository(db)
    outcome1 = ForecastOutcome.create(
        forecast1.forecast_id,
        RESOLVED_AT,
        OBSERVED,
        observed_scenario_type=ScenarioType.BASELINE,
        evidence_refs=("raw-outcome-1",),
        explanation="Observed baseline scenario.",
        created_at=RESOLVED_AT,
    )
    outcome_repo.save_outcome(outcome1)
    outcome_repo.evaluate_version(outcome1.outcome_id, version1.forecast_version_id, evaluated_at=RESOLVED_AT)

    forecast2 = _forecast("forecast-summary-2")
    repo.save_forecast(forecast2)
    version2, _ = _save_version(repo, forecast2)
    outcome2 = ForecastOutcome.create(
        forecast2.forecast_id,
        RESOLVED_AT,
        AMBIGUOUS,
        evidence_refs=("raw-outcome-1",),
        explanation="Evidence remains ambiguous.",
        created_at=RESOLVED_AT,
    )
    outcome_repo.save_outcome(outcome2)
    outcome_repo.evaluate_version(outcome2.outcome_id, version2.forecast_version_id, evaluated_at=RESOLVED_AT)

    summary = outcome_repo.summarize_horizon(ForecastHorizon.SHORT)

    assert summary.horizon == ForecastHorizon.SHORT.value
    assert summary.forecast_count == 2
    assert summary.evaluation_count == 4
    assert summary.scorable_evaluation_count == 2
    assert summary.unscorable_evaluation_count == 2
    assert summary.mean_brier_score_raw == pytest.approx(0.16)
    assert summary.mean_brier_score_calibrated == pytest.approx(0.2025)
    assert summary.mean_calibration_error_raw == pytest.approx(0.40)
    assert summary.mean_calibration_error_calibrated == pytest.approx(0.45)
