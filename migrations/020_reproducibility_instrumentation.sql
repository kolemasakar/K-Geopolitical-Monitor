CREATE TABLE IF NOT EXISTS research_audit_runs (
    research_run_id TEXT PRIMARY KEY,
    run_kind TEXT NOT NULL CHECK (run_kind IN ('LIVE_COLLECTION')),
    watch_id TEXT NOT NULL,
    collection_id TEXT UNIQUE,
    exact_query_snapshot TEXT NOT NULL,
    research_cutoff TEXT NOT NULL,
    instrumentation_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('RUNNING', 'COMPLETED', 'PARTIAL', 'FAILED')),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    error TEXT,
    CHECK (
        (status = 'RUNNING' AND completed_at IS NULL AND error IS NULL)
        OR (status IN ('COMPLETED', 'PARTIAL') AND completed_at IS NOT NULL AND error IS NULL)
        OR (status = 'FAILED' AND completed_at IS NOT NULL AND error IS NOT NULL AND length(trim(error)) > 0)
    ),
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id),
    FOREIGN KEY(collection_id) REFERENCES source_collection_runs(collection_id)
);

CREATE TABLE IF NOT EXISTS research_query_executions (
    research_run_id TEXT NOT NULL,
    collection_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    adapter_identity TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    exact_query TEXT NOT NULL,
    request_locator TEXT,
    request_locator_capture_state TEXT NOT NULL CHECK (
        request_locator_capture_state IN ('CAPTURED', 'NOT_INSTRUMENTED')
    ),
    captured_at TEXT NOT NULL,
    PRIMARY KEY(research_run_id, source_id),
    FOREIGN KEY(research_run_id) REFERENCES research_audit_runs(research_run_id),
    FOREIGN KEY(collection_id, source_id)
        REFERENCES source_collection_attempts(collection_id, source_id)
);

CREATE TABLE IF NOT EXISTS research_artifact_hashes (
    research_run_id TEXT NOT NULL,
    raw_item_id TEXT NOT NULL,
    hash_algorithm TEXT NOT NULL CHECK (hash_algorithm = 'SHA256'),
    content_hash TEXT NOT NULL CHECK (length(content_hash) = 64),
    hash_basis TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    PRIMARY KEY(research_run_id, raw_item_id),
    FOREIGN KEY(research_run_id) REFERENCES research_audit_runs(research_run_id),
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id)
);

CREATE TABLE IF NOT EXISTS research_provenance_annotations (
    research_run_id TEXT NOT NULL,
    raw_item_id TEXT NOT NULL,
    origin_id TEXT NOT NULL,
    relation_class TEXT NOT NULL CHECK (relation_class IN (
        'PRIMARY_ORIGIN',
        'SYNDICATION',
        'REPOST',
        'TRANSLATION',
        'CITATION',
        'DUPLICATE',
        'DISCOVERY_INDEX'
    )),
    classification_basis TEXT NOT NULL,
    classified_at TEXT NOT NULL,
    PRIMARY KEY(research_run_id, raw_item_id),
    FOREIGN KEY(research_run_id) REFERENCES research_audit_runs(research_run_id),
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id)
);

CREATE INDEX IF NOT EXISTS idx_research_audit_watch_cutoff
    ON research_audit_runs(watch_id, research_cutoff);

CREATE INDEX IF NOT EXISTS idx_research_query_collection_source
    ON research_query_executions(collection_id, source_id);

CREATE INDEX IF NOT EXISTS idx_research_artifact_hash
    ON research_artifact_hashes(content_hash);

CREATE INDEX IF NOT EXISTS idx_research_provenance_origin_relation
    ON research_provenance_annotations(origin_id, relation_class);
