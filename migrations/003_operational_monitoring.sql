CREATE TABLE IF NOT EXISTS monitoring_watches (
    watch_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    query TEXT NOT NULL,
    cadence_minutes INTEGER NOT NULL CHECK (cadence_minutes > 0),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS monitoring_runs (
    run_id TEXT PRIMARY KEY,
    watch_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    result_count INTEGER NOT NULL DEFAULT 0 CHECK (result_count >= 0),
    error TEXT,
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);

CREATE INDEX IF NOT EXISTS idx_monitoring_runs_watch_started
    ON monitoring_runs(watch_id, started_at);
