CREATE TABLE IF NOT EXISTS source_collection_attempts (
    collection_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_class TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
    item_count INTEGER NOT NULL CHECK (item_count >= 0),
    error TEXT,
    attempted_at TEXT NOT NULL,
    PRIMARY KEY(collection_id, source_id),
    CHECK (
        (status = 'SUCCESS' AND error IS NULL)
        OR (status = 'FAILED' AND error IS NOT NULL AND length(trim(error)) > 0)
    ),
    FOREIGN KEY(collection_id)
        REFERENCES source_collection_runs(collection_id)
);

CREATE INDEX IF NOT EXISTS idx_source_collection_attempt_source_time
    ON source_collection_attempts(source_id, attempted_at);

CREATE INDEX IF NOT EXISTS idx_source_collection_attempt_collection_status
    ON source_collection_attempts(collection_id, status);
