CREATE TABLE IF NOT EXISTS semantic_claim_versions (
    semantic_claim_version_id TEXT PRIMARY KEY,
    semantic_claim_id TEXT NOT NULL,
    semantic_version INTEGER NOT NULL CHECK(semantic_version > 0),
    normalized_proposition TEXT NOT NULL,
    claimant_actor TEXT,
    subject_text TEXT,
    object_theme TEXT,
    event_action_type TEXT,
    polarity TEXT NOT NULL CHECK(polarity IN ('AFFIRMATIVE', 'NEGATED', 'UNKNOWN')),
    modality TEXT NOT NULL CHECK(modality IN (
        'ASSERTED', 'REPORTED', 'ALLEGED', 'DENIED', 'ESTIMATED', 'QUESTIONED', 'UNKNOWN'
    )),
    time_scope_json TEXT NOT NULL DEFAULT '{}',
    location_scope_json TEXT NOT NULL DEFAULT '{}',
    quantity_json TEXT NOT NULL DEFAULT '{}',
    original_language TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    extraction_version TEXT NOT NULL,
    extraction_confidence REAL NOT NULL CHECK(extraction_confidence >= 0.0 AND extraction_confidence <= 1.0),
    supersedes_version_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(semantic_claim_id, semantic_version),
    FOREIGN KEY(supersedes_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id)
);

CREATE INDEX IF NOT EXISTS idx_semantic_claim_versions_claim
    ON semantic_claim_versions(semantic_claim_id, semantic_version);

CREATE TABLE IF NOT EXISTS semantic_claim_links (
    link_id TEXT PRIMARY KEY,
    semantic_claim_version_id TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK(target_type IN ('LEGACY_CLAIM', 'LIVE_ANALYSIS_CLAIM', 'RAW_ITEM')),
    target_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(semantic_claim_version_id, target_type, target_id),
    FOREIGN KEY(semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id)
);

CREATE INDEX IF NOT EXISTS idx_semantic_claim_links_version
    ON semantic_claim_links(semantic_claim_version_id);
CREATE INDEX IF NOT EXISTS idx_semantic_claim_links_target
    ON semantic_claim_links(target_type, target_id);

CREATE TRIGGER IF NOT EXISTS semantic_claim_versions_no_update
BEFORE UPDATE ON semantic_claim_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic claim versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_claim_versions_no_delete
BEFORE DELETE ON semantic_claim_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic claim versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_claim_links_no_update
BEFORE UPDATE ON semantic_claim_links
BEGIN
    SELECT RAISE(ABORT, 'semantic claim links are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_claim_links_no_delete
BEFORE DELETE ON semantic_claim_links
BEGIN
    SELECT RAISE(ABORT, 'semantic claim links are append-only');
END;
