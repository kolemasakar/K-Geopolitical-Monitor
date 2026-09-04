-- Phase 15.1: append-only forecast outcome-assessment history.
-- This migration does not modify legacy forecast_outcomes/forecast_evaluations.

CREATE TABLE IF NOT EXISTS forecast_outcome_assessments (
    assessment_id TEXT PRIMARY KEY,
    forecast_id TEXT NOT NULL,
    assessment_sequence INTEGER NOT NULL CHECK (assessment_sequence > 0),
    resolution_state TEXT NOT NULL CHECK (resolution_state IN ('RESOLVED', 'UNRESOLVED', 'PARTIAL', 'AMBIGUOUS')),
    legacy_outcome_id TEXT,
    assessment_method TEXT NOT NULL,
    assessment_method_version TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(forecast_id, assessment_sequence),
    FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id),
    FOREIGN KEY(legacy_outcome_id) REFERENCES forecast_outcomes(outcome_id)
);

CREATE TABLE IF NOT EXISTS forecast_outcome_assessment_evidence (
    assessment_id TEXT NOT NULL,
    evidence_order INTEGER NOT NULL CHECK (evidence_order > 0),
    evidence_kind TEXT NOT NULL CHECK (evidence_kind IN ('RAW_ITEM', 'SEMANTIC_CLAIM', 'SEMANTIC_EVIDENCE', 'EXTERNAL_REFERENCE')),
    evidence_ref TEXT NOT NULL,
    provenance_role TEXT NOT NULL CHECK (provenance_role IN ('OUTCOME_EVIDENCE', 'RESOLUTION_CONTEXT')),
    PRIMARY KEY(assessment_id, evidence_order),
    UNIQUE(assessment_id, evidence_kind, evidence_ref, provenance_role),
    FOREIGN KEY(assessment_id) REFERENCES forecast_outcome_assessments(assessment_id)
);

CREATE INDEX IF NOT EXISTS idx_forecast_outcome_assessments_forecast
    ON forecast_outcome_assessments(forecast_id, assessment_sequence, assessed_at);

CREATE INDEX IF NOT EXISTS idx_forecast_outcome_assessment_evidence_ref
    ON forecast_outcome_assessment_evidence(evidence_kind, evidence_ref);

CREATE TRIGGER IF NOT EXISTS trg_forecast_outcome_assessments_no_update
BEFORE UPDATE ON forecast_outcome_assessments
BEGIN
    SELECT RAISE(ABORT, 'forecast_outcome_assessments are append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_forecast_outcome_assessments_no_delete
BEFORE DELETE ON forecast_outcome_assessments
BEGIN
    SELECT RAISE(ABORT, 'forecast_outcome_assessments are append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_forecast_outcome_assessment_evidence_no_update
BEFORE UPDATE ON forecast_outcome_assessment_evidence
BEGIN
    SELECT RAISE(ABORT, 'forecast_outcome_assessment_evidence is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_forecast_outcome_assessment_evidence_no_delete
BEFORE DELETE ON forecast_outcome_assessment_evidence
BEGIN
    SELECT RAISE(ABORT, 'forecast_outcome_assessment_evidence is append-only');
END;
