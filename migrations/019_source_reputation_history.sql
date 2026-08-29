CREATE TABLE IF NOT EXISTS source_reputation_history (
    assessment_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    assessment_version INTEGER NOT NULL CHECK (assessment_version > 0),
    status TEXT NOT NULL CHECK (
        status IN (
            'ACTIVE',
            'WATCH',
            'COMPROMISED',
            'RESTRICTED',
            'SUSPENDED',
            'RESTORED',
            'RETIRED'
        )
    ),
    reliability_rating TEXT NOT NULL CHECK (
        reliability_rating IN ('HIGH', 'MEDIUM', 'LOW', 'UNKNOWN')
    ),
    reason TEXT NOT NULL,
    evidence_refs_json TEXT NOT NULL,
    policy_name TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    reviewed_at TEXT NOT NULL,
    review_due_at TEXT,
    supersedes_assessment_id TEXT,
    restoration_of_assessment_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(source_id, assessment_version),
    FOREIGN KEY(source_id) REFERENCES sources(id),
    FOREIGN KEY(supersedes_assessment_id)
        REFERENCES source_reputation_history(assessment_id),
    FOREIGN KEY(restoration_of_assessment_id)
        REFERENCES source_reputation_history(assessment_id),
    CHECK (length(trim(reason)) > 0),
    CHECK (length(trim(policy_name)) > 0),
    CHECK (length(trim(policy_version)) > 0),
    CHECK (
        (status = 'RESTORED' AND restoration_of_assessment_id IS NOT NULL)
        OR (status <> 'RESTORED' AND restoration_of_assessment_id IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_source_reputation_source_version
    ON source_reputation_history(source_id, assessment_version DESC);

CREATE INDEX IF NOT EXISTS idx_source_reputation_status_time
    ON source_reputation_history(status, assessed_at);

CREATE INDEX IF NOT EXISTS idx_source_reputation_review_due
    ON source_reputation_history(review_due_at);
