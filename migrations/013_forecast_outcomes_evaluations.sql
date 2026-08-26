CREATE TABLE IF NOT EXISTS forecast_outcomes (
    outcome_id TEXT PRIMARY KEY,
    forecast_id TEXT NOT NULL UNIQUE,
    resolved_at TEXT NOT NULL,
    outcome_state TEXT NOT NULL CHECK (outcome_state IN ('OBSERVED', 'NOT_OBSERVED', 'PARTIAL', 'AMBIGUOUS')),
    observed_scenario_type TEXT CHECK (observed_scenario_type IS NULL OR observed_scenario_type IN ('baseline', 'positive', 'negative', 'alternative')),
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    explanation TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id)
);

CREATE TABLE IF NOT EXISTS forecast_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    outcome_id TEXT NOT NULL,
    forecast_id TEXT NOT NULL,
    forecast_version_id TEXT NOT NULL,
    scenario_version_id TEXT NOT NULL,
    horizon TEXT NOT NULL CHECK (horizon IN ('short_term', 'medium_term', 'long_term', 'global_evolutionary')),
    scenario_type TEXT NOT NULL CHECK (scenario_type IN ('baseline', 'positive', 'negative', 'alternative')),
    scenario_label TEXT NOT NULL,
    raw_probability REAL NOT NULL CHECK (raw_probability >= 0.0 AND raw_probability <= 1.0),
    calibrated_probability REAL NOT NULL CHECK (calibrated_probability >= 0.0 AND calibrated_probability <= 1.0),
    observed_value REAL CHECK (observed_value IS NULL OR observed_value IN (0.0, 1.0)),
    brier_score_raw REAL,
    brier_score_calibrated REAL,
    calibration_error_raw REAL,
    calibration_error_calibrated REAL,
    evaluation_method TEXT NOT NULL,
    evaluation_method_version TEXT NOT NULL,
    sample_count INTEGER NOT NULL CHECK (sample_count >= 0),
    evaluated_at TEXT NOT NULL,
    UNIQUE(outcome_id, scenario_version_id, evaluation_method, evaluation_method_version),
    FOREIGN KEY(outcome_id) REFERENCES forecast_outcomes(outcome_id),
    FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id),
    FOREIGN KEY(forecast_version_id) REFERENCES forecast_versions(forecast_version_id),
    FOREIGN KEY(scenario_version_id) REFERENCES forecast_scenario_versions(scenario_version_id)
);

CREATE INDEX IF NOT EXISTS idx_forecast_outcomes_forecast
    ON forecast_outcomes(forecast_id, resolved_at);

CREATE INDEX IF NOT EXISTS idx_forecast_evaluations_horizon
    ON forecast_evaluations(horizon, evaluated_at);

CREATE INDEX IF NOT EXISTS idx_forecast_evaluations_scenario
    ON forecast_evaluations(scenario_type, evaluated_at);
