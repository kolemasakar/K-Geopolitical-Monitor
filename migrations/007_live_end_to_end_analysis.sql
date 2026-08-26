CREATE TABLE IF NOT EXISTS live_analysis_runs (
    analysis_run_id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL UNIQUE,
    watch_id TEXT NOT NULL,
    status TEXT NOT NULL,
    claim_count INTEGER NOT NULL,
    finding_count INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(collection_id) REFERENCES source_collection_runs(collection_id),
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);

CREATE TABLE IF NOT EXISTS live_analysis_claims (
    claim_id TEXT PRIMARY KEY,
    analysis_run_id TEXT NOT NULL,
    claim_key TEXT NOT NULL,
    title TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    confidence REAL NOT NULL,
    importance REAL NOT NULL,
    independent_origin_count INTEGER NOT NULL,
    source_class_count INTEGER NOT NULL,
    origins_json TEXT NOT NULL,
    UNIQUE(analysis_run_id, claim_key),
    FOREIGN KEY(analysis_run_id) REFERENCES live_analysis_runs(analysis_run_id)
);

CREATE TABLE IF NOT EXISTS live_analysis_evidence (
    claim_id TEXT NOT NULL,
    raw_item_id TEXT NOT NULL,
    original_url TEXT NOT NULL,
    origin_host TEXT NOT NULL,
    PRIMARY KEY(claim_id, raw_item_id),
    FOREIGN KEY(claim_id) REFERENCES live_analysis_claims(claim_id),
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id)
);
