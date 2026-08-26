CREATE TABLE IF NOT EXISTS monitoring_watch_alert_policies (
    watch_id TEXT PRIMARY KEY,
    priority TEXT NOT NULL CHECK (priority IN ('NORMAL', 'HIGH', 'CRITICAL')),
    minimum_importance REAL NOT NULL CHECK (minimum_importance >= 0.0 AND minimum_importance <= 1.0),
    minimum_confidence REAL NOT NULL CHECK (minimum_confidence >= 0.0 AND minimum_confidence <= 1.0),
    minimum_verification_rank INTEGER NOT NULL CHECK (minimum_verification_rank >= 0 AND minimum_verification_rank <= 2),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id)
);

CREATE TABLE IF NOT EXISTS strategic_alerts (
    alert_id TEXT PRIMARY KEY,
    watch_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    dedup_key TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('NORMAL', 'HIGH', 'CRITICAL')),
    status TEXT NOT NULL CHECK (status IN ('OPEN', 'UPDATED', 'INVALIDATED', 'RESOLVED')),
    first_triggered_at TEXT NOT NULL,
    last_updated_at TEXT NOT NULL,
    evidence_refs TEXT NOT NULL,
    explanation TEXT NOT NULL,
    invalidation_reason TEXT,
    UNIQUE(watch_id, trigger_type, dedup_key),
    FOREIGN KEY(watch_id) REFERENCES monitoring_watches(watch_id),
    FOREIGN KEY(finding_id) REFERENCES operational_findings(finding_id)
);

CREATE TABLE IF NOT EXISTS strategic_alert_events (
    event_id TEXT PRIMARY KEY,
    alert_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('OPEN', 'UPDATED', 'INVALIDATED', 'RESOLVED')),
    event_at TEXT NOT NULL,
    reason TEXT,
    payload_json TEXT NOT NULL,
    FOREIGN KEY(alert_id) REFERENCES strategic_alerts(alert_id)
);

CREATE INDEX IF NOT EXISTS idx_strategic_alerts_watch_status_priority
    ON strategic_alerts(watch_id, status, priority);

CREATE INDEX IF NOT EXISTS idx_strategic_alert_events_alert_time
    ON strategic_alert_events(alert_id, event_at);
