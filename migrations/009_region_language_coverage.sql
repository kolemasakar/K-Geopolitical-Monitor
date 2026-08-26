CREATE TABLE IF NOT EXISTS region_catalog (
    region_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region_group TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS language_catalog (
    language_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watch_region_language_scopes (
    watch_id TEXT NOT NULL,
    region_code TEXT NOT NULL,
    language_code TEXT NOT NULL,
    required INTEGER NOT NULL DEFAULT 1 CHECK (required IN (0, 1)),
    created_at TEXT NOT NULL,
    PRIMARY KEY(watch_id, region_code, language_code),
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id),
    FOREIGN KEY(region_code) REFERENCES region_catalog(region_code),
    FOREIGN KEY(language_code) REFERENCES language_catalog(language_code)
);

CREATE TABLE IF NOT EXISTS observation_region_language (
    watch_id TEXT NOT NULL,
    raw_item_id TEXT NOT NULL,
    region_code TEXT NOT NULL,
    language_code TEXT NOT NULL,
    attribution_type TEXT NOT NULL CHECK (
        attribution_type IN ('SOURCE_METADATA', 'ANALYST', 'DECLARED', 'TRANSLATION')
    ),
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    original_language INTEGER NOT NULL CHECK (original_language IN (0, 1)),
    created_at TEXT NOT NULL,
    PRIMARY KEY(
        watch_id, raw_item_id, region_code, language_code, attribution_type
    ),
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id),
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id),
    FOREIGN KEY(region_code) REFERENCES region_catalog(region_code),
    FOREIGN KEY(language_code) REFERENCES language_catalog(language_code)
);

CREATE TABLE IF NOT EXISTS region_language_coverage_reports (
    report_id TEXT PRIMARY KEY,
    watch_id TEXT NOT NULL,
    required_scopes TEXT NOT NULL,
    observed_scopes TEXT NOT NULL,
    observed_regions TEXT NOT NULL,
    observed_languages TEXT NOT NULL,
    missing_scopes TEXT NOT NULL,
    coverage_ratio REAL NOT NULL CHECK (coverage_ratio >= 0.0 AND coverage_ratio <= 1.0),
    created_at TEXT NOT NULL,
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);

CREATE INDEX IF NOT EXISTS idx_watch_region_language_scopes_watch
    ON watch_region_language_scopes(watch_id);

CREATE INDEX IF NOT EXISTS idx_observation_region_language_watch
    ON observation_region_language(watch_id, region_code, language_code);

CREATE INDEX IF NOT EXISTS idx_region_language_coverage_watch_time
    ON region_language_coverage_reports(watch_id, created_at);
