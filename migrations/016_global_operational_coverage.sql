CREATE TABLE IF NOT EXISTS operational_coverage_contracts (
    coverage_contract_id TEXT PRIMARY KEY,
    scope_key TEXT NOT NULL,
    name TEXT NOT NULL,
    watch_id TEXT,
    assessment_window_seconds INTEGER NOT NULL
        CHECK (assessment_window_seconds > 0),
    freshness_requirement_seconds INTEGER NOT NULL
        CHECK (freshness_requirement_seconds > 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);

CREATE TABLE IF NOT EXISTS operational_coverage_requirements (
    requirement_id TEXT PRIMARY KEY,
    coverage_contract_id TEXT NOT NULL,
    dimension TEXT NOT NULL CHECK (dimension IN (
        'SOURCE_CLASS',
        'SOURCE_ID',
        'SOURCE_AVAILABILITY',
        'REGION_LANGUAGE',
        'FRESHNESS',
        'TIME_WINDOW',
        'REGION',
        'COUNTRY',
        'ACTOR',
        'STORYLINE',
        'EVENT_CATEGORY',
        'LANGUAGE',
        'IMPORTANCE_THRESHOLD',
        'VERIFICATION_REQUIREMENT',
        'CROSS_CHECK_REQUIREMENT',
        'FORECAST_REQUIREMENT',
        'REPORT_DEPTH'
    )),
    requirement_key TEXT NOT NULL,
    required INTEGER NOT NULL DEFAULT 1 CHECK (required IN (0, 1)),
    parameters_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    UNIQUE(
        coverage_contract_id,
        dimension,
        requirement_key,
        required,
        parameters_json
    ),
    FOREIGN KEY(coverage_contract_id)
        REFERENCES operational_coverage_contracts(coverage_contract_id)
);

CREATE TABLE IF NOT EXISTS operational_coverage_snapshots (
    coverage_snapshot_id TEXT PRIMARY KEY,
    coverage_contract_id TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    required_count INTEGER NOT NULL CHECK (required_count > 0),
    satisfied_count INTEGER NOT NULL CHECK (satisfied_count >= 0),
    gap_count INTEGER NOT NULL CHECK (gap_count >= 0),
    unavailable_count INTEGER NOT NULL CHECK (unavailable_count >= 0),
    stale_count INTEGER NOT NULL CHECK (stale_count >= 0),
    unknown_count INTEGER NOT NULL CHECK (unknown_count >= 0),
    unmeasured_count INTEGER NOT NULL CHECK (unmeasured_count >= 0),
    coverage_ratio REAL NOT NULL CHECK (
        coverage_ratio >= 0.0 AND coverage_ratio <= 1.0
    ),
    coverage_confidence REAL NOT NULL CHECK (
        coverage_confidence >= 0.0 AND coverage_confidence <= 1.0
    ),
    limitations_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    UNIQUE(coverage_contract_id, assessed_at, window_start, window_end),
    CHECK (
        satisfied_count + gap_count + unavailable_count + stale_count
        + unknown_count + unmeasured_count = required_count
    ),
    FOREIGN KEY(coverage_contract_id)
        REFERENCES operational_coverage_contracts(coverage_contract_id)
);

CREATE TABLE IF NOT EXISTS operational_coverage_requirement_results (
    coverage_snapshot_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'SATISFIED',
        'GAP',
        'UNAVAILABLE',
        'STALE',
        'UNKNOWN',
        'UNMEASURED'
    )),
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    explanation TEXT NOT NULL,
    measured_at TEXT NOT NULL,
    PRIMARY KEY(coverage_snapshot_id, requirement_id),
    FOREIGN KEY(coverage_snapshot_id)
        REFERENCES operational_coverage_snapshots(coverage_snapshot_id),
    FOREIGN KEY(requirement_id)
        REFERENCES operational_coverage_requirements(requirement_id)
);

CREATE INDEX IF NOT EXISTS idx_operational_coverage_contract_scope
    ON operational_coverage_contracts(scope_key, active);

CREATE INDEX IF NOT EXISTS idx_operational_coverage_requirement_contract
    ON operational_coverage_requirements(
        coverage_contract_id,
        dimension,
        requirement_key
    );

CREATE INDEX IF NOT EXISTS idx_operational_coverage_snapshot_contract_time
    ON operational_coverage_snapshots(coverage_contract_id, assessed_at);

CREATE INDEX IF NOT EXISTS idx_operational_coverage_result_status
    ON operational_coverage_requirement_results(coverage_snapshot_id, status);

CREATE TRIGGER IF NOT EXISTS trg_operational_coverage_snapshot_no_update
BEFORE UPDATE ON operational_coverage_snapshots
BEGIN
    SELECT RAISE(ABORT, 'operational coverage snapshots are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_coverage_snapshot_no_delete
BEFORE DELETE ON operational_coverage_snapshots
BEGIN
    SELECT RAISE(ABORT, 'operational coverage snapshots are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_coverage_result_no_update
BEFORE UPDATE ON operational_coverage_requirement_results
BEGIN
    SELECT RAISE(ABORT, 'operational coverage requirement results are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_coverage_result_no_delete
BEFORE DELETE ON operational_coverage_requirement_results
BEGIN
    SELECT RAISE(ABORT, 'operational coverage requirement results are immutable');
END;
