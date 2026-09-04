CREATE TABLE IF NOT EXISTS semantic_verification_policy_versions (
    policy_version_id TEXT PRIMARY KEY,
    policy_id TEXT NOT NULL,
    policy_version INTEGER NOT NULL CHECK(policy_version > 0),
    policy_name TEXT NOT NULL,
    rules_json TEXT NOT NULL,
    review_status TEXT NOT NULL CHECK(review_status IN ('APPROVED','RETIRED')),
    supersedes_policy_version_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(policy_id, policy_version),
    FOREIGN KEY(supersedes_policy_version_id) REFERENCES semantic_verification_policy_versions(policy_version_id)
);
CREATE INDEX IF NOT EXISTS idx_semantic_verification_policy_identity
    ON semantic_verification_policy_versions(policy_id, policy_version);

CREATE TABLE IF NOT EXISTS semantic_factual_confidence_versions (
    factual_confidence_version_id TEXT PRIMARY KEY,
    factual_confidence_id TEXT NOT NULL,
    confidence_version INTEGER NOT NULL CHECK(confidence_version > 0),
    semantic_claim_version_id TEXT NOT NULL,
    evidence_sufficiency TEXT NOT NULL CHECK(evidence_sufficiency IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    provenance_independence TEXT NOT NULL CHECK(provenance_independence IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    authority_proximity TEXT NOT NULL CHECK(authority_proximity IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    contradiction_resolution TEXT NOT NULL CHECK(contradiction_resolution IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    temporal_freshness TEXT NOT NULL CHECK(temporal_freshness IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    extraction_certainty TEXT NOT NULL CHECK(extraction_certainty IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    translation_certainty TEXT NOT NULL CHECK(translation_certainty IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    claim_specific_certainty TEXT NOT NULL CHECK(claim_specific_certainty IN ('UNKNOWN','LOW','MEDIUM','HIGH')),
    coverage_limitation TEXT NOT NULL CHECK(coverage_limitation IN ('UNKNOWN','LIMITED','ADEQUATE')),
    assessment_method TEXT NOT NULL,
    assessment_version TEXT NOT NULL,
    note TEXT,
    supersedes_confidence_version_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(factual_confidence_id, confidence_version),
    FOREIGN KEY(semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id),
    FOREIGN KEY(supersedes_confidence_version_id) REFERENCES semantic_factual_confidence_versions(factual_confidence_version_id)
);
CREATE INDEX IF NOT EXISTS idx_semantic_factual_confidence_claim
    ON semantic_factual_confidence_versions(semantic_claim_version_id, confidence_version);

CREATE TABLE IF NOT EXISTS semantic_verification_decision_versions (
    verification_decision_version_id TEXT PRIMARY KEY,
    verification_decision_id TEXT NOT NULL,
    decision_version INTEGER NOT NULL CHECK(decision_version > 0),
    semantic_claim_version_id TEXT NOT NULL,
    policy_version_id TEXT NOT NULL,
    factual_confidence_version_id TEXT NOT NULL,
    verification_state TEXT NOT NULL CHECK(verification_state IN ('DETECTED','PARTLY_VERIFIED','VERIFIED','DISPUTED','UNVERIFIABLE')),
    decision_code TEXT NOT NULL CHECK(decision_code IN ('INITIAL','HOLD','PROMOTE','DEMOTE','DISPUTE','MARK_UNVERIFIABLE')),
    evidence_snapshot_json TEXT NOT NULL,
    independence_snapshot_json TEXT NOT NULL,
    contradiction_snapshot_json TEXT NOT NULL,
    rationale TEXT NOT NULL,
    supersedes_decision_version_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(verification_decision_id, decision_version),
    FOREIGN KEY(semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id),
    FOREIGN KEY(policy_version_id) REFERENCES semantic_verification_policy_versions(policy_version_id),
    FOREIGN KEY(factual_confidence_version_id) REFERENCES semantic_factual_confidence_versions(factual_confidence_version_id),
    FOREIGN KEY(supersedes_decision_version_id) REFERENCES semantic_verification_decision_versions(verification_decision_version_id)
);
CREATE INDEX IF NOT EXISTS idx_semantic_verification_decision_claim
    ON semantic_verification_decision_versions(semantic_claim_version_id, decision_version);

CREATE TRIGGER IF NOT EXISTS semantic_verification_policy_versions_no_update
BEFORE UPDATE ON semantic_verification_policy_versions
BEGIN SELECT RAISE(ABORT, 'semantic verification policy versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_verification_policy_versions_no_delete
BEFORE DELETE ON semantic_verification_policy_versions
BEGIN SELECT RAISE(ABORT, 'semantic verification policy versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_factual_confidence_versions_no_update
BEFORE UPDATE ON semantic_factual_confidence_versions
BEGIN SELECT RAISE(ABORT, 'semantic factual confidence versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_factual_confidence_versions_no_delete
BEFORE DELETE ON semantic_factual_confidence_versions
BEGIN SELECT RAISE(ABORT, 'semantic factual confidence versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_verification_decision_versions_no_update
BEFORE UPDATE ON semantic_verification_decision_versions
BEGIN SELECT RAISE(ABORT, 'semantic verification decision versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_verification_decision_versions_no_delete
BEFORE DELETE ON semantic_verification_decision_versions
BEGIN SELECT RAISE(ABORT, 'semantic verification decision versions are append-only'); END;
