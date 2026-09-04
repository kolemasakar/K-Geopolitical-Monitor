-- Phase 16.5 append-only operator quality feedback persistence.
-- Feedback is operator workflow evidence, never automatic factual verification.

CREATE TABLE IF NOT EXISTS operator_quality_feedback (
    feedback_id TEXT PRIMARY KEY,
    delivery_intent_id TEXT NOT NULL,
    reviewed_transport_attempt_id TEXT,
    canonical_object_type TEXT NOT NULL CHECK (canonical_object_type IN (
        'STRATEGIC_ALERT', 'REPORT', 'FINDING', 'SEMANTIC_CLAIM'
    )),
    canonical_object_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'USEFUL',
        'NOT_USEFUL',
        'TIMELY',
        'LATE',
        'DUPLICATE_NOISY',
        'MISSING_CONTEXT',
        'INCORRECT_PRIORITIZATION',
        'FACTUAL_CORRECTION_REQUESTED',
        'DELIVERY_FORMAT_ISSUE',
        'NOTE'
    )),
    note TEXT CHECK (note IS NULL OR length(note) <= 1000),
    created_at TEXT NOT NULL,
    FOREIGN KEY(delivery_intent_id) REFERENCES delivery_intents(delivery_intent_id),
    FOREIGN KEY(reviewed_transport_attempt_id) REFERENCES delivery_transport_attempts(transport_attempt_id)
);

CREATE INDEX IF NOT EXISTS idx_operator_quality_feedback_intent
    ON operator_quality_feedback(delivery_intent_id, created_at, feedback_id);
CREATE INDEX IF NOT EXISTS idx_operator_quality_feedback_type
    ON operator_quality_feedback(feedback_type, created_at);
CREATE INDEX IF NOT EXISTS idx_operator_quality_feedback_canonical_object
    ON operator_quality_feedback(canonical_object_type, canonical_object_id, created_at);

CREATE TRIGGER IF NOT EXISTS operator_quality_feedback_no_update
BEFORE UPDATE ON operator_quality_feedback
BEGIN
    SELECT RAISE(ABORT, 'operator quality feedback is append-only');
END;

CREATE TRIGGER IF NOT EXISTS operator_quality_feedback_no_delete
BEFORE DELETE ON operator_quality_feedback
BEGIN
    SELECT RAISE(ABORT, 'operator quality feedback is append-only');
END;
