CREATE TABLE IF NOT EXISTS source_portfolio_versions (
    portfolio_entry_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    portfolio_version INTEGER NOT NULL CHECK (portfolio_version > 0),
    source_name TEXT NOT NULL,
    publisher_name TEXT NOT NULL,
    source_class TEXT NOT NULL,
    source_role TEXT NOT NULL CHECK (
        source_role IN (
            'PRIMARY',
            'OFFICIAL',
            'MEDIA',
            'DISCOVERY',
            'STRUCTURED_DATA',
            'OSINT',
            'SOCIAL',
            'USER_PROVIDED',
            'OTHER_APPROVED'
        )
    ),
    region_scope_json TEXT NOT NULL,
    language_scope_json TEXT NOT NULL,
    access_mode TEXT NOT NULL CHECK (
        access_mode IN (
            'PUBLIC_ANONYMOUS',
            'PUBLIC_CREDENTIALED',
            'RESTRICTED',
            'USER_PROVIDED'
        )
    ),
    cost_mode TEXT NOT NULL CHECK (cost_mode IN ('FREE', 'PAID', 'UNKNOWN')),
    authentication_mode TEXT NOT NULL CHECK (
        authentication_mode IN ('NONE', 'API_KEY', 'OAUTH', 'OTHER')
    ),
    expected_freshness_minutes INTEGER NOT NULL
        CHECK (expected_freshness_minutes > 0),
    collection_cadence_minutes INTEGER NOT NULL
        CHECK (collection_cadence_minutes > 0),
    adapter_id TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    outbound_domains_json TEXT NOT NULL,
    outbound_protocols_json TEXT NOT NULL,
    fallback_source_ids_json TEXT NOT NULL,
    availability_state TEXT NOT NULL CHECK (
        availability_state IN (
            'PLANNED',
            'ACTIVE',
            'DEGRADED',
            'UNAVAILABLE',
            'STALE',
            'RETIRED'
        )
    ),
    data_classification TEXT NOT NULL CHECK (
        data_classification IN (
            'PUBLIC',
            'USER_PROVIDED',
            'RESTRICTED',
            'SENSITIVE'
        )
    ),
    origin_characteristics TEXT NOT NULL,
    independence_constraints TEXT NOT NULL,
    terms_notes TEXT NOT NULL DEFAULT '',
    owner TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    review_status TEXT NOT NULL CHECK (
        review_status IN ('PLANNED', 'APPROVED', 'REJECTED', 'RETIRED')
    ),
    paid_provider_approved INTEGER NOT NULL DEFAULT 0
        CHECK (paid_provider_approved IN (0, 1)),
    reviewed_at TEXT NOT NULL,
    supersedes_entry_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(source_id, portfolio_version),
    FOREIGN KEY(source_id) REFERENCES sources(id),
    FOREIGN KEY(supersedes_entry_id)
        REFERENCES source_portfolio_versions(portfolio_entry_id),
    CHECK (length(trim(source_name)) > 0),
    CHECK (length(trim(publisher_name)) > 0),
    CHECK (length(trim(source_class)) > 0),
    CHECK (length(trim(adapter_id)) > 0),
    CHECK (length(trim(adapter_version)) > 0),
    CHECK (length(trim(origin_characteristics)) > 0),
    CHECK (length(trim(independence_constraints)) > 0),
    CHECK (length(trim(owner)) > 0),
    CHECK (length(trim(reviewer)) > 0),
    CHECK (
        (access_mode = 'PUBLIC_ANONYMOUS' AND authentication_mode = 'NONE')
        OR (access_mode = 'USER_PROVIDED' AND authentication_mode = 'NONE')
        OR (
            access_mode IN ('PUBLIC_CREDENTIALED', 'RESTRICTED')
            AND authentication_mode <> 'NONE'
        )
    ),
    CHECK (
        data_classification NOT IN ('RESTRICTED', 'SENSITIVE')
        OR access_mode <> 'PUBLIC_ANONYMOUS'
    ),
    CHECK (
        availability_state NOT IN ('ACTIVE', 'DEGRADED', 'UNAVAILABLE', 'STALE')
        OR review_status = 'APPROVED'
    ),
    CHECK (
        (availability_state = 'RETIRED' AND review_status = 'RETIRED')
        OR (availability_state <> 'RETIRED' AND review_status <> 'RETIRED')
    ),
    CHECK (
        paid_provider_approved = 0
        OR cost_mode = 'PAID'
    ),
    CHECK (
        cost_mode <> 'PAID'
        OR review_status <> 'APPROVED'
        OR paid_provider_approved = 1
    )
);

CREATE INDEX IF NOT EXISTS idx_source_portfolio_source_version
    ON source_portfolio_versions(source_id, portfolio_version DESC);

CREATE INDEX IF NOT EXISTS idx_source_portfolio_review_availability
    ON source_portfolio_versions(review_status, availability_state);

CREATE INDEX IF NOT EXISTS idx_source_portfolio_class_role
    ON source_portfolio_versions(source_class, source_role);

CREATE TRIGGER IF NOT EXISTS trg_source_portfolio_no_update
BEFORE UPDATE ON source_portfolio_versions
BEGIN
    SELECT RAISE(ABORT, 'source portfolio versions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_source_portfolio_no_delete
BEFORE DELETE ON source_portfolio_versions
BEGIN
    SELECT RAISE(ABORT, 'source portfolio versions are immutable');
END;
