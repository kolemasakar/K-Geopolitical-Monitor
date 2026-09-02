CREATE TABLE IF NOT EXISTS semantic_evidence_relation_versions (
    evidence_relation_version_id TEXT PRIMARY KEY,
    evidence_relation_id TEXT NOT NULL,
    relation_version INTEGER NOT NULL CHECK(relation_version > 0),
    semantic_claim_version_id TEXT NOT NULL,
    evidence_provenance_entity_version_id TEXT NOT NULL,
    raw_item_id TEXT,
    relation_type TEXT NOT NULL CHECK(relation_type IN ('SUPPORTS','CONTRADICTS','QUALIFIES','CONTEXT_ONLY','ATTRIBUTION_ONLY','DUPLICATE_OR_SAME_ORIGIN')),
    assessment_method TEXT NOT NULL,
    assessment_version TEXT NOT NULL,
    note TEXT,
    supersedes_relation_version_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(evidence_relation_id, relation_version),
    FOREIGN KEY(semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id),
    FOREIGN KEY(evidence_provenance_entity_version_id) REFERENCES semantic_provenance_entity_versions(provenance_entity_version_id),
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id),
    FOREIGN KEY(supersedes_relation_version_id) REFERENCES semantic_evidence_relation_versions(evidence_relation_version_id)
);
CREATE INDEX IF NOT EXISTS idx_semantic_evidence_relation_claim ON semantic_evidence_relation_versions(semantic_claim_version_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_semantic_evidence_relation_provenance ON semantic_evidence_relation_versions(evidence_provenance_entity_version_id);
CREATE INDEX IF NOT EXISTS idx_semantic_evidence_relation_raw ON semantic_evidence_relation_versions(raw_item_id);

CREATE TABLE IF NOT EXISTS semantic_independence_assessment_versions (
    independence_assessment_version_id TEXT PRIMARY KEY,
    independence_assessment_id TEXT NOT NULL,
    assessment_version_number INTEGER NOT NULL CHECK(assessment_version_number > 0),
    semantic_claim_version_id TEXT NOT NULL,
    subject_evidence_relation_version_id TEXT NOT NULL,
    comparison_evidence_relation_version_id TEXT NOT NULL,
    independence_state TEXT NOT NULL CHECK(independence_state IN ('INDEPENDENT','NOT_INDEPENDENT','UNKNOWN','MIXED')),
    rationale_code TEXT NOT NULL CHECK(rationale_code IN ('EXPLICIT_DISTINCT_UNDERLYING_ORIGINS','SAME_UNDERLYING_ORIGIN','DERIVATION_PATH','DUPLICATE_OR_SAME_ORIGIN','UNRESOLVED_ORIGIN','MIXED_ORIGIN','INSUFFICIENT_PROVENANCE','MANUAL_REVIEW','OTHER')),
    assessment_method TEXT NOT NULL,
    assessment_version TEXT NOT NULL,
    note TEXT,
    supersedes_assessment_version_id TEXT,
    created_at TEXT NOT NULL,
    CHECK(subject_evidence_relation_version_id <> comparison_evidence_relation_version_id),
    UNIQUE(independence_assessment_id, assessment_version_number),
    FOREIGN KEY(semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id),
    FOREIGN KEY(subject_evidence_relation_version_id) REFERENCES semantic_evidence_relation_versions(evidence_relation_version_id),
    FOREIGN KEY(comparison_evidence_relation_version_id) REFERENCES semantic_evidence_relation_versions(evidence_relation_version_id),
    FOREIGN KEY(supersedes_assessment_version_id) REFERENCES semantic_independence_assessment_versions(independence_assessment_version_id)
);
CREATE INDEX IF NOT EXISTS idx_semantic_independence_claim ON semantic_independence_assessment_versions(semantic_claim_version_id, independence_state);
CREATE INDEX IF NOT EXISTS idx_semantic_independence_subject ON semantic_independence_assessment_versions(subject_evidence_relation_version_id);
CREATE INDEX IF NOT EXISTS idx_semantic_independence_comparison ON semantic_independence_assessment_versions(comparison_evidence_relation_version_id);

CREATE TRIGGER IF NOT EXISTS semantic_evidence_relation_versions_no_update BEFORE UPDATE ON semantic_evidence_relation_versions BEGIN SELECT RAISE(ABORT, 'semantic evidence relation versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_evidence_relation_versions_no_delete BEFORE DELETE ON semantic_evidence_relation_versions BEGIN SELECT RAISE(ABORT, 'semantic evidence relation versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_independence_assessment_versions_no_update BEFORE UPDATE ON semantic_independence_assessment_versions BEGIN SELECT RAISE(ABORT, 'semantic independence assessment versions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS semantic_independence_assessment_versions_no_delete BEFORE DELETE ON semantic_independence_assessment_versions BEGIN SELECT RAISE(ABORT, 'semantic independence assessment versions are append-only'); END;
