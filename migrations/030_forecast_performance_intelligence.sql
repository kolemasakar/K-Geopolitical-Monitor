-- Phase 15.4 — Performance Intelligence and Drift/Bias Analysis
-- Additive, append-only performance snapshots derived exclusively from
-- immutable Phase 15.3 calibration observations.
-- These tables describe forecast-performance evidence only. They do not
-- alter or promote factual-verification state.

CREATE TABLE IF NOT EXISTS forecast_performance_aggregates (
    aggregate_id TEXT PRIMARY KEY,
    cohort_definition_json TEXT NOT NULL,
    observation_set_hash TEXT NOT NULL,
    forecast_id TEXT,
    horizon TEXT CHECK(horizon IS NULL OR horizon IN ('short_term', 'medium_term', 'long_term', 'global_evolutionary')),
    scenario_type TEXT CHECK(scenario_type IS NULL OR scenario_type IN ('baseline', 'positive', 'negative', 'alternative')),
    scoring_method TEXT NOT NULL,
    scoring_method_version TEXT NOT NULL,
    reliability_bucket_count INTEGER NOT NULL CHECK(reliability_bucket_count >= 2),
    evaluated_from TEXT,
    evaluated_to TEXT,
    sample_count INTEGER NOT NULL CHECK(sample_count > 0),
    forecast_count INTEGER NOT NULL CHECK(forecast_count > 0 AND forecast_count <= sample_count),
    sample_qualification TEXT NOT NULL CHECK(sample_qualification IN ('N_LT_5', 'N_5_TO_19', 'N_GE_20')),
    mean_raw_probability REAL NOT NULL CHECK(mean_raw_probability >= 0.0 AND mean_raw_probability <= 1.0),
    mean_calibrated_probability REAL NOT NULL CHECK(mean_calibrated_probability >= 0.0 AND mean_calibrated_probability <= 1.0),
    observed_rate REAL NOT NULL CHECK(observed_rate >= 0.0 AND observed_rate <= 1.0),
    mean_brier_raw REAL NOT NULL CHECK(mean_brier_raw >= 0.0 AND mean_brier_raw <= 1.0),
    mean_brier_calibrated REAL NOT NULL CHECK(mean_brier_calibrated >= 0.0 AND mean_brier_calibrated <= 1.0),
    expected_calibration_error_raw REAL NOT NULL CHECK(expected_calibration_error_raw >= 0.0 AND expected_calibration_error_raw <= 1.0),
    expected_calibration_error_calibrated REAL NOT NULL CHECK(expected_calibration_error_calibrated >= 0.0 AND expected_calibration_error_calibrated <= 1.0),
    bias_raw REAL NOT NULL CHECK(bias_raw >= -1.0 AND bias_raw <= 1.0),
    bias_calibrated REAL NOT NULL CHECK(bias_calibrated >= -1.0 AND bias_calibrated <= 1.0),
    brier_improvement REAL NOT NULL CHECK(brier_improvement >= -1.0 AND brier_improvement <= 1.0),
    calibration_error_improvement REAL NOT NULL CHECK(calibration_error_improvement >= -1.0 AND calibration_error_improvement <= 1.0),
    aggregate_method TEXT NOT NULL,
    aggregate_method_version TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    UNIQUE(cohort_definition_json, observation_set_hash, aggregate_method, aggregate_method_version),
    FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id)
);

CREATE TABLE IF NOT EXISTS forecast_performance_aggregate_observations (
    aggregate_id TEXT NOT NULL,
    observation_order INTEGER NOT NULL CHECK(observation_order > 0),
    observation_id TEXT NOT NULL,
    PRIMARY KEY(aggregate_id, observation_order),
    UNIQUE(aggregate_id, observation_id),
    FOREIGN KEY(aggregate_id) REFERENCES forecast_performance_aggregates(aggregate_id),
    FOREIGN KEY(observation_id) REFERENCES forecast_calibration_observations(observation_id)
);

CREATE TABLE IF NOT EXISTS forecast_performance_drift_comparisons (
    comparison_id TEXT PRIMARY KEY,
    baseline_aggregate_id TEXT NOT NULL,
    recent_aggregate_id TEXT NOT NULL,
    baseline_sample_count INTEGER NOT NULL CHECK(baseline_sample_count > 0),
    recent_sample_count INTEGER NOT NULL CHECK(recent_sample_count > 0),
    mean_raw_probability_delta REAL NOT NULL CHECK(mean_raw_probability_delta >= -1.0 AND mean_raw_probability_delta <= 1.0),
    mean_calibrated_probability_delta REAL NOT NULL CHECK(mean_calibrated_probability_delta >= -1.0 AND mean_calibrated_probability_delta <= 1.0),
    observed_rate_delta REAL NOT NULL CHECK(observed_rate_delta >= -1.0 AND observed_rate_delta <= 1.0),
    mean_brier_raw_delta REAL NOT NULL CHECK(mean_brier_raw_delta >= -1.0 AND mean_brier_raw_delta <= 1.0),
    mean_brier_calibrated_delta REAL NOT NULL CHECK(mean_brier_calibrated_delta >= -1.0 AND mean_brier_calibrated_delta <= 1.0),
    calibration_error_raw_delta REAL NOT NULL CHECK(calibration_error_raw_delta >= -1.0 AND calibration_error_raw_delta <= 1.0),
    calibration_error_calibrated_delta REAL NOT NULL CHECK(calibration_error_calibrated_delta >= -1.0 AND calibration_error_calibrated_delta <= 1.0),
    bias_raw_shift REAL NOT NULL CHECK(bias_raw_shift >= -2.0 AND bias_raw_shift <= 2.0),
    bias_calibrated_shift REAL NOT NULL CHECK(bias_calibrated_shift >= -2.0 AND bias_calibrated_shift <= 2.0),
    comparison_method TEXT NOT NULL,
    comparison_method_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(baseline_aggregate_id, recent_aggregate_id, comparison_method, comparison_method_version),
    CHECK(baseline_aggregate_id <> recent_aggregate_id),
    FOREIGN KEY(baseline_aggregate_id) REFERENCES forecast_performance_aggregates(aggregate_id),
    FOREIGN KEY(recent_aggregate_id) REFERENCES forecast_performance_aggregates(aggregate_id)
);

CREATE INDEX IF NOT EXISTS idx_forecast_performance_aggregates_cohort
    ON forecast_performance_aggregates(horizon, scenario_type, scoring_method, scoring_method_version);
CREATE INDEX IF NOT EXISTS idx_forecast_performance_aggregates_window
    ON forecast_performance_aggregates(evaluated_from, evaluated_to);
CREATE INDEX IF NOT EXISTS idx_forecast_performance_aggregate_observations_observation
    ON forecast_performance_aggregate_observations(observation_id, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_forecast_performance_drift_pair
    ON forecast_performance_drift_comparisons(baseline_aggregate_id, recent_aggregate_id);

CREATE TRIGGER IF NOT EXISTS forecast_performance_aggregates_no_update
BEFORE UPDATE ON forecast_performance_aggregates
BEGIN
    SELECT RAISE(ABORT, 'forecast performance aggregates are append-only');
END;

CREATE TRIGGER IF NOT EXISTS forecast_performance_aggregates_no_delete
BEFORE DELETE ON forecast_performance_aggregates
BEGIN
    SELECT RAISE(ABORT, 'forecast performance aggregates are append-only');
END;

CREATE TRIGGER IF NOT EXISTS forecast_performance_aggregate_observations_no_update
BEFORE UPDATE ON forecast_performance_aggregate_observations
BEGIN
    SELECT RAISE(ABORT, 'forecast performance aggregate membership is append-only');
END;

CREATE TRIGGER IF NOT EXISTS forecast_performance_aggregate_observations_no_delete
BEFORE DELETE ON forecast_performance_aggregate_observations
BEGIN
    SELECT RAISE(ABORT, 'forecast performance aggregate membership is append-only');
END;

CREATE TRIGGER IF NOT EXISTS forecast_performance_drift_comparisons_no_update
BEFORE UPDATE ON forecast_performance_drift_comparisons
BEGIN
    SELECT RAISE(ABORT, 'forecast performance drift comparisons are append-only');
END;

CREATE TRIGGER IF NOT EXISTS forecast_performance_drift_comparisons_no_delete
BEFORE DELETE ON forecast_performance_drift_comparisons
BEGIN
    SELECT RAISE(ABORT, 'forecast performance drift comparisons are append-only');
END;
