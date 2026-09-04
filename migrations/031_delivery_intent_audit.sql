-- Phase 16.1 canonical delivery intent and audit persistence.
-- Additive/project-local only. Delivery records are not truth records.

CREATE TABLE IF NOT EXISTS delivery_intents (
    delivery_intent_id TEXT PRIMARY KEY,
    canonical_object_type TEXT NOT NULL CHECK (canonical_object_type IN (
        'STRATEGIC_ALERT', 'REPORT', 'FINDING', 'SEMANTIC_CLAIM'
    )),
    canonical_object_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('INITIAL', 'UPDATE', 'RESOLUTION')),
    policy_key TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_delivery_intents_canonical_object
    ON delivery_intents(canonical_object_type, canonical_object_id, created_at);

CREATE TABLE IF NOT EXISTS delivery_intent_audit_events (
    delivery_audit_event_id TEXT PRIMARY KEY,
    delivery_intent_id TEXT NOT NULL,
    event_sequence INTEGER NOT NULL CHECK (event_sequence > 0),
    state TEXT NOT NULL CHECK (state IN (
        'PENDING', 'SUPPRESSED', 'READY', 'ATTEMPTED', 'DELIVERED', 'FAILED'
    )),
    reason_code TEXT,
    detail TEXT,
    recorded_at TEXT NOT NULL,
    UNIQUE(delivery_intent_id, event_sequence),
    FOREIGN KEY(delivery_intent_id) REFERENCES delivery_intents(delivery_intent_id)
);

CREATE INDEX IF NOT EXISTS idx_delivery_intent_audit_intent_sequence
    ON delivery_intent_audit_events(delivery_intent_id, event_sequence);

-- Reserved by the P16.1 audit model for provider-neutral P16.3 transport evidence.
-- P16.1 never writes these tables.
CREATE TABLE IF NOT EXISTS delivery_transport_attempts (
    transport_attempt_id TEXT PRIMARY KEY,
    delivery_intent_id TEXT NOT NULL,
    attempt_sequence INTEGER NOT NULL CHECK (attempt_sequence > 0),
    transport_name TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('ATTEMPTED', 'DELIVERED', 'FAILED')),
    error_code TEXT,
    error_detail TEXT,
    attempted_at TEXT NOT NULL,
    UNIQUE(delivery_intent_id, attempt_sequence),
    FOREIGN KEY(delivery_intent_id) REFERENCES delivery_intents(delivery_intent_id)
);

CREATE TABLE IF NOT EXISTS delivery_receipts (
    delivery_receipt_id TEXT PRIMARY KEY,
    transport_attempt_id TEXT NOT NULL,
    receipt_type TEXT NOT NULL,
    external_reference TEXT,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY(transport_attempt_id) REFERENCES delivery_transport_attempts(transport_attempt_id)
);

CREATE INDEX IF NOT EXISTS idx_delivery_transport_attempts_intent
    ON delivery_transport_attempts(delivery_intent_id, attempt_sequence);
CREATE INDEX IF NOT EXISTS idx_delivery_receipts_attempt
    ON delivery_receipts(transport_attempt_id);

CREATE TRIGGER IF NOT EXISTS delivery_intents_no_update
BEFORE UPDATE ON delivery_intents
BEGIN
    SELECT RAISE(ABORT, 'delivery intents are append-only');
END;

CREATE TRIGGER IF NOT EXISTS delivery_intents_no_delete
BEFORE DELETE ON delivery_intents
BEGIN
    SELECT RAISE(ABORT, 'delivery intents are append-only');
END;

CREATE TRIGGER IF NOT EXISTS delivery_intent_audit_events_no_update
BEFORE UPDATE ON delivery_intent_audit_events
BEGIN
    SELECT RAISE(ABORT, 'delivery intent audit events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS delivery_intent_audit_events_no_delete
BEFORE DELETE ON delivery_intent_audit_events
BEGIN
    SELECT RAISE(ABORT, 'delivery intent audit events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS delivery_transport_attempts_no_update
BEFORE UPDATE ON delivery_transport_attempts
BEGIN
    SELECT RAISE(ABORT, 'delivery transport attempts are append-only');
END;

CREATE TRIGGER IF NOT EXISTS delivery_transport_attempts_no_delete
BEFORE DELETE ON delivery_transport_attempts
BEGIN
    SELECT RAISE(ABORT, 'delivery transport attempts are append-only');
END;

CREATE TRIGGER IF NOT EXISTS delivery_receipts_no_update
BEFORE UPDATE ON delivery_receipts
BEGIN
    SELECT RAISE(ABORT, 'delivery receipts are append-only');
END;

CREATE TRIGGER IF NOT EXISTS delivery_receipts_no_delete
BEFORE DELETE ON delivery_receipts
BEGIN
    SELECT RAISE(ABORT, 'delivery receipts are append-only');
END;
