CREATE TABLE IF NOT EXISTS semantic_provenance_entity_versions (
    provenance_entity_version_id TEXT PRIMARY KEY,
    provenance_entity_id TEXT NOT NULL,
    provenance_version INTEGER NOT NULL CHECK(provenance_version > 0),
    entity_kind TEXT NOT NULL CHECK(entity_kind IN (
        'PUBLICATION', 'PUBLISHER', 'SOURCE_ENDPOINT', 'OFFICIAL_STATEMENT',
        'OFFICIAL_DOCUMENT', 'WIRE_REPORT', 'DATASET', 'SOCIAL_POST',
        'USER_PROVIDED', 'OTHER', 'UNKNOWN', 'MIXED'
    )),
    canonical_name TEXT NOT NULL,
    source_id TEXT,
    raw_item_id TEXT,
    canonical_url TEXT,
    language TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    supersedes_version_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(provenance_entity_id, provenance_version),
    FOREIGN KEY(source_id) REFERENCES sources(id),
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id),
    FOREIGN KEY(supersedes_version_id) REFERENCES semantic_provenance_entity_versions(provenance_entity_version_id)
);

CREATE INDEX IF NOT EXISTS idx_semantic_provenance_entity_identity
    ON semantic_provenance_entity_versions(provenance_entity_id, provenance_version);
CREATE INDEX IF NOT EXISTS idx_semantic_provenance_entity_source
    ON semantic_provenance_entity_versions(source_id);
CREATE INDEX IF NOT EXISTS idx_semantic_provenance_entity_raw
    ON semantic_provenance_entity_versions(raw_item_id);

CREATE TABLE IF NOT EXISTS semantic_claim_provenance_role_versions (
    claim_provenance_role_version_id TEXT PRIMARY KEY,
    claim_provenance_role_id TEXT NOT NULL,
    role_version INTEGER NOT NULL CHECK(role_version > 0),
    semantic_claim_version_id TEXT NOT NULL,
    provenance_entity_version_id TEXT NOT NULL,
    provenance_role TEXT NOT NULL CHECK(provenance_role IN (
        'PUBLICATION', 'PUBLISHER', 'IMMEDIATE_ACQUIRED_SOURCE', 'CITED_SOURCE',
        'QUOTED_SOURCE', 'UNDERLYING_ORIGIN', 'PROVENANCE_CONTEXT'
    )),
    attribution_state TEXT NOT NULL CHECK(attribution_state IN (
        'OBSERVED', 'ASSERTED', 'UNRESOLVED', 'MIXED'
    )),
    note TEXT,
    supersedes_role_version_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(claim_provenance_role_id, role_version),
    FOREIGN KEY(semantic_claim_version_id) REFERENCES semantic_claim_versions(semantic_claim_version_id),
    FOREIGN KEY(provenance_entity_version_id) REFERENCES semantic_provenance_entity_versions(provenance_entity_version_id),
    FOREIGN KEY(supersedes_role_version_id) REFERENCES semantic_claim_provenance_role_versions(claim_provenance_role_version_id)
);

CREATE INDEX IF NOT EXISTS idx_semantic_claim_provenance_claim
    ON semantic_claim_provenance_role_versions(semantic_claim_version_id, provenance_role);
CREATE INDEX IF NOT EXISTS idx_semantic_claim_provenance_entity
    ON semantic_claim_provenance_role_versions(provenance_entity_version_id);

CREATE TABLE IF NOT EXISTS semantic_provenance_relation_versions (
    provenance_relation_version_id TEXT PRIMARY KEY,
    provenance_relation_id TEXT NOT NULL,
    relation_version INTEGER NOT NULL CHECK(relation_version > 0),
    subject_entity_version_id TEXT NOT NULL,
    object_entity_version_id TEXT NOT NULL,
    relation_type TEXT NOT NULL CHECK(relation_type IN (
        'PUBLISHED_BY', 'ACQUIRED_FROM', 'CITES', 'QUOTES', 'SYNDICATED_FROM',
        'REPOSTED_FROM', 'TRANSLATED_FROM', 'DERIVED_FROM',
        'DATA_EXTRACTED_FROM', 'OTHER'
    )),
    note TEXT,
    supersedes_relation_version_id TEXT,
    created_at TEXT NOT NULL,
    CHECK(subject_entity_version_id <> object_entity_version_id),
    UNIQUE(provenance_relation_id, relation_version),
    FOREIGN KEY(subject_entity_version_id) REFERENCES semantic_provenance_entity_versions(provenance_entity_version_id),
    FOREIGN KEY(object_entity_version_id) REFERENCES semantic_provenance_entity_versions(provenance_entity_version_id),
    FOREIGN KEY(supersedes_relation_version_id) REFERENCES semantic_provenance_relation_versions(provenance_relation_version_id)
);

CREATE INDEX IF NOT EXISTS idx_semantic_provenance_relation_subject
    ON semantic_provenance_relation_versions(subject_entity_version_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_semantic_provenance_relation_object
    ON semantic_provenance_relation_versions(object_entity_version_id, relation_type);

CREATE TRIGGER IF NOT EXISTS semantic_provenance_entity_versions_no_update
BEFORE UPDATE ON semantic_provenance_entity_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic provenance entity versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_provenance_entity_versions_no_delete
BEFORE DELETE ON semantic_provenance_entity_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic provenance entity versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_claim_provenance_role_versions_no_update
BEFORE UPDATE ON semantic_claim_provenance_role_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic claim provenance role versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_claim_provenance_role_versions_no_delete
BEFORE DELETE ON semantic_claim_provenance_role_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic claim provenance role versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_provenance_relation_versions_no_update
BEFORE UPDATE ON semantic_provenance_relation_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic provenance relation versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS semantic_provenance_relation_versions_no_delete
BEFORE DELETE ON semantic_provenance_relation_versions
BEGIN
    SELECT RAISE(ABORT, 'semantic provenance relation versions are append-only');
END;