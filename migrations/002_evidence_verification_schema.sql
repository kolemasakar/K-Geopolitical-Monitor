CREATE TABLE claims (
    id TEXT PRIMARY KEY,
    event_id TEXT,
    text TEXT NOT NULL,
    confidence TEXT
);

CREATE TABLE evidence (
    id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    source_id TEXT,
    provenance TEXT,
    verification_status TEXT
);
