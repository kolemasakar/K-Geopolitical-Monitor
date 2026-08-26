CREATE TABLE IF NOT EXISTS source_collection_runs (
    collection_id TEXT PRIMARY KEY,
    watch_id TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    item_count INTEGER NOT NULL,
    source_success_count INTEGER NOT NULL,
    source_failure_count INTEGER NOT NULL,
    failures TEXT NOT NULL,
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);

CREATE TABLE IF NOT EXISTS live_source_provenance (
    raw_item_id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL,
    original_url TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id),
    FOREIGN KEY(collection_id) REFERENCES source_collection_runs(collection_id)
);
