-- Phase 15.3 — Calibration Engine
-- Additive scoreable observation history over exact P15 outcome assessments.
-- This does not replace or rewrite legacy M12 forecast_evaluations or
-- forecast_calibration_* history.

CREATE TABLE IF NOT EXISTS forecast_calibration_observations (
    observation_id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    forecast_id TEXT NOT NULL,
    forecast_version_id TEXT NOT NULL,
    scenario_version_id TEXT NOT NULL,
    legacy_outcome_id TEXT NOT NULL,
    horizon TEXT NOT NULL CHECK(horizon IN ('immediate', 'short_term', 'medium_term', 'long_term')),
    scenario_type TEXT NOT NULL CHECK(scenario_type IN ('baseline', 'positive', 'negative', 'alternative')),
    scenario_label TEXT NOT NULL,
    legacy_outcome_state TEXT NOT NULL CHECK(legacy_outcome_state IN ('OBSERVED', 'NOT_OBSERVED')),
    observed_value REAL NOT NULL CHECK(observed_value IN (0.0, 1.0)),
    raw_probability REAL NOT NULL CHECK(raw_probability >= 0.0 AND raw_probability <= 1.0),
    calibrated_probability REAL NOT NULL CHECK(calibrated_probability >= 0.0 AND calibrated_probability <= 1.0),
    brier_score_raw REAL NOT NULL CHECK(brier_score_raw >= 0.0 AND brier_score_raw <= 1.0),
    brier_score_calibrated REAL NOT NULL CHECK(brier_score_calibrated >= 0.0 AND brier_score_calibrated <= 1.0),
    raw_reliability_bucket INTEGER NOT NULL CHECK(raw_reliability_bucket >= 0),
    calibrated_reliability_bucket INTEGER NOT NULL CHECK(calibrated_reliability_bucket >= 0),
    reliability_bucket_count INTEGER NOT NULL CHECK(reliability_bucket_count >= 2),
    scoring_method TEXT NOT NULL,
    scoring_method_version TEXT NOT NULL,
    evaluated_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(
        assessment_id,
        scenario_version_id,
        scoring_method,
        scoring_method_version,
        reliability_bucket_count
    ),
    CHECK(raw_reliability_bucket < reliability_bucket_count),
    CHECK(calibrated_reliability_bucket < reliability_bucket_count),
    FOREIGN KEY(assessment_id) REFERENCES forecast_outcome_assessments(assessment_id),
    FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id),
    FOREIGN KEY(forecast_version_id) REFERENCES forecast_versions(forecast_version_id),
    FOREIGN KEY(scenario_version_id) REFERENCES forecast_scenario_versions(scenario_version_id),
    FOREIGN KEY(legacy_outcome_id) REFERENCES forecast_outcomes(outcome_id)
);

CREATE INDEX IF NOT EXISTS idx_forecast_calibration_observations_assessment
    ON forecast_calibration_observations(assessment_id, scenario_version_id);
CREATE INDEX IF NOT EXISTS idx_forecast_calibration_observations_cohort
    ON forecast_calibration_observations(horizon, scenario_type, scoring_method, scoring_method_version);
CREATE INDEX IF NOT EXISTS idx_forecast_calibration_observations_forecast
    ON forecast_calibration_observations(forecast_id, forecast_version_id);

CREATE TRIGGER IF NOT EXISTS forecast_calibration_observations_no_update
BEFORE UPDATE ON forecast_calibration_observations
BEGIN
    SELECT RAISE(ABORT, 'forecast calibration observations are append-only');
END;

CREATE TRIGGER IF NOT EXISTS forecast_calibration_observations_no_delete
BEFORE DELETE ON forecast_calibration_observations
BEGIN
    SELECT RAISE(ABORT, 'forecast calibration observations are append-only');
END;
