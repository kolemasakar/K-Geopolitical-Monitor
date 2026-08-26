CREATE TABLE IF NOT EXISTS report_snapshots (
    report_id TEXT PRIMARY KEY,
    report_type TEXT NOT NULL CHECK (report_type IN (
        'STRATEGIC_ALERT',
        'GLOBAL_GEOPOLITICAL_BRIEF',
        'REGIONAL_COUNTRY_BRIEF',
        'STORYLINE_REPORT',
        'EVENT_DOSSIER',
        'FORECAST_REPORT',
        'STRATEGIC_OUTLOOK'
    )),
    scope_key TEXT NOT NULL,
    subject_ref_type TEXT,
    subject_ref_id TEXT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    as_of TEXT NOT NULL,
    created_at TEXT NOT NULL,
    generator_version TEXT NOT NULL,
    CHECK (
        (subject_ref_type IS NULL AND subject_ref_id IS NULL)
        OR (subject_ref_type IS NOT NULL AND subject_ref_id IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS report_sections (
    section_id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL,
    section_order INTEGER NOT NULL CHECK (section_order >= 0),
    section_type TEXT NOT NULL,
    heading TEXT NOT NULL,
    presentation_class TEXT NOT NULL CHECK (presentation_class IN (
        'OBSERVED_FACT',
        'VERIFICATION_STATE',
        'ANALYTICAL_CONTEXT',
        'GRAPH_INFERENCE',
        'FORECAST_SCENARIO',
        'ANALYST_ASSUMPTION',
        'COVERAGE_METADATA'
    )),
    content_json TEXT NOT NULL DEFAULT '{}',
    explanation TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(report_id, section_order),
    FOREIGN KEY(report_id) REFERENCES report_snapshots(report_id)
);

CREATE TABLE IF NOT EXISTS report_references (
    reference_id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL,
    section_id TEXT,
    reference_kind TEXT NOT NULL CHECK (reference_kind IN (
        'SOURCE',
        'RAW_ITEM',
        'CLAIM',
        'EVENT',
        'FINDING',
        'ALERT',
        'GRAPH_NODE',
        'GRAPH_EDGE',
        'FORECAST',
        'FORECAST_VERSION',
        'SCENARIO_VERSION',
        'REGION',
        'LANGUAGE',
        'COVERAGE_REPORT',
        'ANALYST_ASSUMPTION'
    )),
    reference_value TEXT NOT NULL,
    reference_role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(report_id) REFERENCES report_snapshots(report_id),
    FOREIGN KEY(section_id) REFERENCES report_sections(section_id)
);

CREATE INDEX IF NOT EXISTS idx_report_snapshots_type_as_of
    ON report_snapshots(report_type, as_of);

CREATE INDEX IF NOT EXISTS idx_report_sections_report_order
    ON report_sections(report_id, section_order);

CREATE INDEX IF NOT EXISTS idx_report_references_report_kind
    ON report_references(report_id, reference_kind);
