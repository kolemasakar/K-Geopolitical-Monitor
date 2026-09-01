CREATE TABLE IF NOT EXISTS owner_runtime_health (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    instrumentation_version TEXT NOT NULL,
    last_supervisor_tick_at TEXT NOT NULL,
    last_completed_tick_at TEXT NOT NULL,
    last_successful_execution_at TEXT,
    recovered_runs INTEGER NOT NULL CHECK (recovered_runs >= 0),
    execution_count INTEGER NOT NULL CHECK (execution_count >= 0),
    completed_execution_count INTEGER NOT NULL CHECK (completed_execution_count >= 0),
    failed_execution_count INTEGER NOT NULL CHECK (failed_execution_count >= 0),
    tick_status TEXT NOT NULL CHECK (tick_status IN ('IDLE', 'HEALTHY', 'DEGRADED')),
    last_error TEXT
);
