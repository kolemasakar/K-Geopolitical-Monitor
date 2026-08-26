CREATE TABLE IF NOT EXISTS claims (
    id TEXT PRIMARY KEY,
    event_id TEXT,
    text TEXT NOT NULL,
    confidence TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    source_id TEXT,
    provenance TEXT,
    verification_status TEXT
);
