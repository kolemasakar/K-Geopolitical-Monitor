CREATE TABLE IF NOT EXISTS semantic_contradiction_versions (
    contradiction_version_id TEXT PRIMARY KEY,
    contradiction_id TEXT NOT NULL,
    contradiction_version INTEGER NOT NULL CHECK(contradiction_version > 0),
    left_semantic_claim_version_id TEXT NOT NULL,
    right_semantic_claim_version_id TEXT NOT NULL,
    contradiction_dimension TEXT NOT NULL CHECK(contradiction_dimension IN (
        'OCCURRENCE_EXISTENCE', 'ATTRIBUTION_RESPONSIBILITY', 'ACTOR_IDENTITY',
        'QUANTITY_VALUE', 'TIME', 'LOCATION', 'STATUS_OUTCOME', 'SCOPE_EXTENT',
        'CAUSAL_INTERPRETATION', 'OTHER'
    )),
    lifecycle_state TEXT NOT NULL CHECK(lifecycle_state IN (
        'DETECTED', 'UNRESOLVED', 'EVOLVING', 'RESOLVED'
    )),
    reconciliation_code TEXT NOT NULL CHECK(reconciliation_code IN (
        'NONE', 'NEW_EVIDENCE', 'OCCURRENCE_RECONCILED', 'SCOPE_RECONCILED',
        'TIME_RECONCILED', 'LOCATION_RECONCILED', 'ATTRIBUTION_RECONCILED',
        'QUANTITY_RECONCILED', 'ACTOR_IDENTITY_RECONCILED', 'STATUS_UPDATED',
        'CAUSAL_INTERPRETATION_RECONCILED', 'SUPERSEDED_INFORMATION',
        'MANUAL_REVIEW', 'OTHER'
    )),
    assessment_method TEXT NOT NULL,
    assessment_version TEXT NOT NULL,
    note TEXT,
    supersedes_contradiction_version_id TEXT,
    created_at TEXT NOT NULL,
    CHECK(left_semantic_claim_version_id <> right_semantic_claim_version_id),
    CHECK(
        (lifecycle_state = 'RESOLVED' AND reconciliation_code <> 'NONE') OR
        (lifecycle_state <> 'RESOLVED' AND reconciliation_code = 'NONE')
    ),
    UNIQUE(contradiction_id, contradiction_version),
    FOREIGN KEY(left_semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id),
    FOREIGN KEY(right_semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id),
    FOREIGN KEY(supersedes_contradiction_version_id) REFERENCES semantic_contradiction_versions(contradiction_version_id)
);

CREATE INDEX IF NOT EXISTS idx_semantic_contradiction_left
    ON semantic_contradiction_versions(left_semantic_claim_version_id, contradiction_dimension);
CREATE INDEX IF NOT EXISTS idx_semantic_contradiction_right
    ON semantic_contradiction_versions(right_semantic_claim_version_id, contradiction_dimension);
CREATE INDEX IF NOT EXISTS idx_semantic_contradiction_identity
    ON semantic_contradiction_versions(contradiction_id, contradiction_version);

CREATE TABLE IF NOT EXISTS semantic_contradiction_evidence_links (
    contradiction_evidence_link_id TEXT PRIMARY KEY,
    contradiction_version_id TEXT NOT NULL,
    evidence_relation_version_id TEXT NOT NULL,
    claim_side TEXT NOT NULL CHECK(claim_side IN ('LEFT', 'RIGHT')),
    link_role TEXT NOT NULL CHECK(link_role IN (
        'CLAIM_EVIDENCE', 'CONTRADICTION_TRIGGER', 'QUALIFIER', 'RESOLUTION_CONTEXT'
    )),
    note TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(contradiction_version_id, evidence_relation_version_id, claim_side, link_role),
    FOREIGN KEY(contradiction_version_id) REFERENCES semantic_contradiction_versions(contradiction_version_id),
    FOREIGN KEY(evidence_relation_version_id) REFERENCES semantic_evidence_relation_versions(evidence_relation_version_id)
);

CREATE INDEX IF NOT EXISTS idx_semantic_contradiction_evidence_version
    ON semantic_contradiction_evidence_links(contradiction_version_id, claim_side);
CREATE INDEX IF NOT EXISTS idx_semantic_contradiction_evidence_relation
    ON semantic_contradiction_evidence_links(evidence_relation_version_id);

CREATE TRIGGER IF NOT EXISTS semantic_contradiction_versions_no_update
BEFORE UPDATE ON semantic_contradiction_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic contradiction versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_contradiction_versions_no_delete
BEFORE DELETE ON semantic_contradiction_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic contradiction versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_contradiction_evidence_links_no_update
BEFORE UPDATE ON semantic_contradiction_evidence_links
BEGIN
    SELECT RAISE(ABORT, 'semantic contradiction evidence links are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_contradiction_evidence_links_no_delete
BEFORE DELETE ON semantic_contradiction_evidence_links
BEGIN
    SELECT RAISE(ABORT, 'semantic contradiction evidence links are append-only');
END;
