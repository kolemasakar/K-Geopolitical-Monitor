CREATE TABLE IF NOT EXISTS forecast_version_inputs (
    input_id TEXT PRIMARY KEY,
    forecast_version_id TEXT NOT NULL,
    input_kind TEXT NOT NULL CHECK (input_kind IN (
        'SOURCE_EVIDENCE',
        'CANONICAL_EVENT',
        'GRAPH_RELATIONSHIP',
        'OPERATIONAL_FINDING',
        'ANALYST_ASSUMPTION'
    )),
    reference_id TEXT,
    statement TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    CHECK (
        (input_kind = 'ANALYST_ASSUMPTION' AND reference_id IS NULL AND statement IS NOT NULL)
        OR
        (input_kind <> 'ANALYST_ASSUMPTION' AND reference_id IS NOT NULL AND statement IS NULL)
    ),
    UNIQUE(forecast_version_id, input_kind, reference_id, statement),
    FOREIGN KEY(forecast_version_id) REFERENCES forecast_versions(forecast_version_id)
);

CREATE INDEX IF NOT EXISTS idx_forecast_version_inputs_version_kind
    ON forecast_version_inputs(forecast_version_id, input_kind);
