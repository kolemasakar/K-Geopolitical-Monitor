from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.advanced_forecasting import (
    ForecastRecord,
    ForecastVersion,
    ScenarioVersion,
    SQLiteAdvancedForecastRepository,
)
from kgeopolitical_monitor.forecast_calibration_history import (
    CALIBRATED,
    RAW,
    CalibrationCohort,
    SQLiteForecastCalibrationRepository,
)
from kgeopolitical_monitor.forecast_evaluation import (
    AMBIGUOUS,
    OBSERVED,
    ForecastOutcome,
    SQLiteForecastEvaluationRepository,
)
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType


NOW = datetime(2026, 8, 26, 19, 0, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)
RESOLVED_AT = DEADLINE + timedelta(hours=1)


def _seed_evidence(db):
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            ("source-calibration", "Calibration Source", "Official sources", "official"),
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES (?, ?, ?, ?, ?)",
            ("raw-calibration", "source-calibration", "Outcome evidence", "evidence", RESOLVED_AT.isoformat()),
        )


def _add_forecast(db, index, *, ambiguous=False, horizon=ForecastHorizon.SHORT):
    forecast_repo = SQLiteAdvancedForecastRepository(db)
    target_key = f"calibration-{index}"
    forecast = ForecastRecord.create(
        target_key,
        f"Will scenario {index} occur?",
        horizon,
        DEADLINE + timedelta(minutes=index),
        created_at=NOW,
    )
    forecast_repo.save_forecast(forecast)
    version = ForecastVersion.create(
        forecast.forecast_id,
        1,
        input_snapshot={"source": "raw-calibration"},
        provenance_refs=("SOURCE_EVIDENCE:raw-calibration",),
        assumptions=("Calibration fixture",),
        change_reason="Calibration fixture",
        created_at=NOW,
    )
    raw_baseline = 0.45 + (index % 4) * 0.10
    calibrated_baseline = min(0.85, raw_baseline + 0.05)
    scenarios = (
        ScenarioVersion.create(
            version.forecast_version_id,
            ScenarioType.BASELINE,
            "Baseline occurs",
            raw_baseline,
            calibrated_baseline,
            0.70,
        ),
        ScenarioVersion.create(
            version.forecast_version_id,
            ScenarioType.NEGATIVE,
            "Baseline does not occur",
            1.0 - raw_baseline,
            1.0 - calibrated_baseline,
            0.65,
        ),
    )
    forecast_repo.save_version(version, scenarios)

    evaluation_repo = SQLiteForecastEvaluationRepository(db)
    if ambiguous:
        outcome = ForecastOutcome.create(
            forecast.forecast_id,
            RESOLVED_AT + timedelta(minutes=index),
            AMBIGUOUS,
            evidence_refs=("raw-calibration",),
            explanation="Outcome is ambiguous and must not enter calibration.",
            created_at=RESOLVED_AT + timedelta(minutes=index),
        )
    else:
        outcome = ForecastOutcome.create(
            forecast.forecast_id,
            RESOLVED_AT + timedelta(minutes=index),
            OBSERVED,
            observed_scenario_type=ScenarioType.BASELINE,
            evidence_refs=("raw-calibration",),
            explanation="Baseline scenario observed.",
            created_at=RESOLVED_AT + timedelta(minutes=index),
        )
    evaluation_repo.save_outcome(outcome)
    evaluation_repo.evaluate_version(
        outcome.outcome_id,
        version.forecast_version_id,
        evaluated_at=RESOLVED_AT + timedelta(minutes=index),
    )
    return forecast, version, scenarios


def _setup(tmp_path):
    db = tmp_path / "project.db"
    SQLiteAdvancedForecastRepository(db)
    _seed_evidence(db)
    return db


def test_calibration_requires_minimum_five_scorable_evaluations(tmp_path):
    db = _setup(tmp_path)
    _add_forecast(db, 1)
    _add_forecast(db, 2)

    repo = SQLiteForecastCalibrationRepository(db)
    with pytest.raises(ValueError, match="at least 5 scorable evaluations; found 4"):
        repo.create_run(CalibrationCohort(horizon=ForecastHorizon.SHORT), created_at=NOW)


def test_calibration_run_is_reproducible_restart_safe_and_excludes_unscored_rows(tmp_path):
    db = _setup(tmp_path)
    for index in range(1, 4):
        _add_forecast(db, index)
    _add_forecast(db, 99, ambiguous=True)

    repo = SQLiteForecastCalibrationRepository(db)
    cohort = CalibrationCohort(horizon=ForecastHorizon.SHORT)
    run, buckets = repo.create_run(cohort, created_at=NOW)
    repeated_run, repeated_buckets = repo.create_run(
        cohort,
        created_at=NOW + timedelta(days=1),
    )

    assert run == repeated_run
    assert buckets == repeated_buckets
    assert run.sample_count == 6
    assert len(run.evaluation_ids) == 6
    assert len(buckets) > 0
    assert sum(item.sample_count for item in buckets if item.probability_basis == RAW) == 6
    assert sum(item.sample_count for item in buckets if item.probability_basis == CALIBRATED) == 6

    restarted = SQLiteForecastCalibrationRepository(db)
    assert restarted.get_run(run.calibration_id) == run
    assert restarted.list_buckets(run.calibration_id) == buckets


def test_scenario_type_cohorts_and_performance_breakdown_are_explicit(tmp_path):
    db = _setup(tmp_path)
    for index in range(1, 7):
        _add_forecast(db, index)

    repo = SQLiteForecastCalibrationRepository(db)
    baseline_run, _ = repo.create_run(
        CalibrationCohort(
            horizon=ForecastHorizon.SHORT,
            scenario_type=ScenarioType.BASELINE,
        ),
        created_at=NOW,
    )
    negative_run, _ = repo.create_run(
        CalibrationCohort(
            horizon=ForecastHorizon.SHORT,
            scenario_type=ScenarioType.NEGATIVE,
        ),
        created_at=NOW,
    )

    assert baseline_run.sample_count == 6
    assert negative_run.sample_count == 6
    assert baseline_run.calibration_id != negative_run.calibration_id
    assert baseline_run.cohort.scenario_type == ScenarioType.BASELINE.value
    assert negative_run.cohort.scenario_type == ScenarioType.NEGATIVE.value

    breakdown = repo.performance_breakdown()
    assert [(item.horizon, item.scenario_type, item.sample_count) for item in breakdown] == [
        (ForecastHorizon.SHORT.value, ScenarioType.BASELINE.value, 6),
        (ForecastHorizon.SHORT.value, ScenarioType.NEGATIVE.value, 6),
    ]
    assert all(item.forecast_count == 6 for item in breakdown)


def test_new_scorable_evaluations_create_new_calibration_history_snapshot(tmp_path):
    db = _setup(tmp_path)
    for index in range(1, 4):
        _add_forecast(db, index)

    repo = SQLiteForecastCalibrationRepository(db)
    cohort = CalibrationCohort(horizon=ForecastHorizon.SHORT)
    first, _ = repo.create_run(cohort, created_at=NOW)

    _add_forecast(db, 4)
    second, _ = repo.create_run(cohort, created_at=NOW + timedelta(hours=1))

    assert first.sample_count == 6
    assert second.sample_count == 8
    assert first.calibration_id != second.calibration_id
    assert repo.get_run(first.calibration_id) == first
    assert repo.get_run(second.calibration_id) == second


def test_calibration_history_does_not_rewrite_scenario_probabilities(tmp_path):
    db = _setup(tmp_path)
    saved = []
    for index in range(1, 4):
        saved.append(_add_forecast(db, index))

    forecast_repo = SQLiteAdvancedForecastRepository(db)
    before = {
        version.forecast_version_id: forecast_repo.list_scenarios(version.forecast_version_id)
        for _, version, _ in saved
    }

    SQLiteForecastCalibrationRepository(db).create_run(
        CalibrationCohort(horizon=ForecastHorizon.SHORT),
        created_at=NOW,
    )

    after = {
        version.forecast_version_id: forecast_repo.list_scenarios(version.forecast_version_id)
        for _, version, _ in saved
    }
    assert after == before
