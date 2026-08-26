CREATE TABLE IF NOT EXISTS forecasts (
    forecast_id TEXT PRIMARY KEY,
    target_key TEXT NOT NULL,
    question TEXT NOT NULL,
    horizon TEXT NOT NULL CHECK (horizon IN ('short_term', 'medium_term', 'long_term', 'global_evolutionary')),
    evaluation_deadline TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'RESOLVED', 'INVALIDATED', 'CLOSED')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(target_key, horizon, evaluation_deadline)
);

CREATE TABLE IF NOT EXISTS forecast_versions (
    forecast_version_id TEXT PRIMARY KEY,
    forecast_id TEXT NOT NULL,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    input_snapshot_json TEXT NOT NULL DEFAULT '{}',
    provenance_refs_json TEXT NOT NULL DEFAULT '[]',
    assumptions_json TEXT NOT NULL DEFAULT '[]',
    change_reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(forecast_id, version_number),
    FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id)
);

CREATE TABLE IF NOT EXISTS forecast_scenario_versions (
    scenario_version_id TEXT PRIMARY KEY,
    forecast_version_id TEXT NOT NULL,
    scenario_type TEXT NOT NULL CHECK (scenario_type IN ('baseline', 'positive', 'negative', 'alternative')),
    label TEXT NOT NULL,
    raw_probability REAL NOT NULL CHECK (raw_probability >= 0.0 AND raw_probability <= 1.0),
    calibrated_probability REAL NOT NULL CHECK (calibrated_probability >= 0.0 AND calibrated_probability <= 1.0),
    scenario_confidence REAL NOT NULL CHECK (scenario_confidence >= 0.0 AND scenario_confidence <= 1.0),
    drivers_json TEXT NOT NULL DEFAULT '[]',
    constraints_json TEXT NOT NULL DEFAULT '[]',
    triggers_json TEXT NOT NULL DEFAULT '[]',
    inhibitors_json TEXT NOT NULL DEFAULT '[]',
    uncertainty_factors_json TEXT NOT NULL DEFAULT '[]',
    invalidation_signals_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE(forecast_version_id, scenario_type, label),
    FOREIGN KEY(forecast_version_id) REFERENCES forecast_versions(forecast_version_id)
);

CREATE INDEX IF NOT EXISTS idx_forecasts_status_deadline
    ON forecasts(status, evaluation_deadline);

CREATE INDEX IF NOT EXISTS idx_forecast_versions_forecast
    ON forecast_versions(forecast_id, version_number);

CREATE INDEX IF NOT EXISTS idx_forecast_scenarios_version
    ON forecast_scenario_versions(forecast_version_id, scenario_type);
