CREATE TABLE IF NOT EXISTS pilot_coverage_reports (
    run_id TEXT PRIMARY KEY,
    watch_id TEXT NOT NULL,
    examined_count INTEGER NOT NULL,
    matched_count INTEGER NOT NULL,
    source_classes TEXT NOT NULL,
    coverage_confidence REAL NOT NULL,
    gaps TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES monitoring_runs(run_id),
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);
