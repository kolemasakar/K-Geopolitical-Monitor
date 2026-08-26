ALTER TABLE monitoring_runs
    ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0);

ALTER TABLE monitoring_runs
    ADD COLUMN recovered INTEGER NOT NULL DEFAULT 0 CHECK (recovered IN (0, 1));

CREATE TABLE IF NOT EXISTS operational_findings (
    finding_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    watch_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    importance REAL NOT NULL CHECK (importance >= 0.0 AND importance <= 1.0),
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    evidence_refs TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES monitoring_runs(run_id),
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);

CREATE INDEX IF NOT EXISTS idx_operational_findings_watch_rank
    ON operational_findings(watch_id, importance DESC, confidence DESC);
