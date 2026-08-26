CREATE TABLE IF NOT EXISTS forecast_calibration_runs (
    calibration_id TEXT PRIMARY KEY,
    calibration_method TEXT NOT NULL,
    calibration_method_version TEXT NOT NULL,
    evaluation_method TEXT NOT NULL,
    evaluation_method_version TEXT NOT NULL,
    cohort_horizon TEXT CHECK (cohort_horizon IS NULL OR cohort_horizon IN ('short_term', 'medium_term', 'long_term', 'global_evolutionary')),
    cohort_scenario_type TEXT CHECK (cohort_scenario_type IS NULL OR cohort_scenario_type IN ('baseline', 'positive', 'negative', 'alternative')),
    min_sample_count INTEGER NOT NULL CHECK (min_sample_count > 0),
    sample_count INTEGER NOT NULL CHECK (sample_count >= min_sample_count),
    evaluation_ids_json TEXT NOT NULL,
    raw_mean_probability REAL NOT NULL CHECK (raw_mean_probability >= 0.0 AND raw_mean_probability <= 1.0),
    calibrated_mean_probability REAL NOT NULL CHECK (calibrated_mean_probability >= 0.0 AND calibrated_mean_probability <= 1.0),
    observed_frequency REAL NOT NULL CHECK (observed_frequency >= 0.0 AND observed_frequency <= 1.0),
    raw_brier_mean REAL NOT NULL CHECK (raw_brier_mean >= 0.0 AND raw_brier_mean <= 1.0),
    calibrated_brier_mean REAL NOT NULL CHECK (calibrated_brier_mean >= 0.0 AND calibrated_brier_mean <= 1.0),
    raw_calibration_error_mean REAL NOT NULL CHECK (raw_calibration_error_mean >= 0.0 AND raw_calibration_error_mean <= 1.0),
    calibrated_calibration_error_mean REAL NOT NULL CHECK (calibrated_calibration_error_mean >= 0.0 AND calibrated_calibration_error_mean <= 1.0),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS forecast_calibration_buckets (
    calibration_id TEXT NOT NULL,
    probability_basis TEXT NOT NULL CHECK (probability_basis IN ('RAW', 'CALIBRATED')),
    bucket_index INTEGER NOT NULL CHECK (bucket_index >= 0),
    bucket_lower REAL NOT NULL CHECK (bucket_lower >= 0.0 AND bucket_lower <= 1.0),
    bucket_upper REAL NOT NULL CHECK (bucket_upper >= 0.0 AND bucket_upper <= 1.0),
    sample_count INTEGER NOT NULL CHECK (sample_count > 0),
    mean_probability REAL NOT NULL CHECK (mean_probability >= 0.0 AND mean_probability <= 1.0),
    observed_frequency REAL NOT NULL CHECK (observed_frequency >= 0.0 AND observed_frequency <= 1.0),
    mean_brier_score REAL NOT NULL CHECK (mean_brier_score >= 0.0 AND mean_brier_score <= 1.0),
    mean_calibration_error REAL NOT NULL CHECK (mean_calibration_error >= 0.0 AND mean_calibration_error <= 1.0),
    PRIMARY KEY(calibration_id, probability_basis, bucket_index),
    FOREIGN KEY(calibration_id) REFERENCES forecast_calibration_runs(calibration_id)
);

CREATE INDEX IF NOT EXISTS idx_forecast_calibration_runs_cohort
    ON forecast_calibration_runs(cohort_horizon, cohort_scenario_type, created_at);

CREATE INDEX IF NOT EXISTS idx_forecast_calibration_buckets_run
    ON forecast_calibration_buckets(calibration_id, probability_basis, bucket_index);
