CREATE TABLE IF NOT EXISTS raw_item_translations (
    translation_id TEXT PRIMARY KEY,
    raw_item_id TEXT NOT NULL,
    text_field TEXT NOT NULL CHECK (text_field IN ('title', 'content')),
    source_language TEXT NOT NULL,
    target_language TEXT NOT NULL,
    original_text TEXT NOT NULL,
    translated_text TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('SUCCESS', 'FAILED', 'UNAVAILABLE', 'UNSUPPORTED', 'AMBIGUOUS')
    ),
    method TEXT NOT NULL,
    provider TEXT,
    provider_version TEXT,
    translation_version INTEGER NOT NULL CHECK (translation_version > 0),
    underlying_origin_id TEXT NOT NULL,
    origin_kind TEXT NOT NULL CHECK (origin_kind IN ('ORIGIN_HOST', 'SOURCE_ID')),
    uncertainty_note TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(raw_item_id, text_field, target_language, translation_version),
    FOREIGN KEY(raw_item_id) REFERENCES raw_items(id),
    CHECK (source_language <> target_language),
    CHECK (length(trim(original_text)) > 0),
    CHECK (length(trim(method)) > 0),
    CHECK (length(trim(underlying_origin_id)) > 0),
    CHECK (
        (status = 'SUCCESS' AND translated_text IS NOT NULL AND length(trim(translated_text)) > 0 AND error_message IS NULL)
        OR (status = 'AMBIGUOUS' AND translated_text IS NOT NULL AND length(trim(translated_text)) > 0 AND uncertainty_note IS NOT NULL AND length(trim(uncertainty_note)) > 0 AND error_message IS NULL)
        OR (status IN ('FAILED', 'UNAVAILABLE', 'UNSUPPORTED') AND translated_text IS NULL AND error_message IS NOT NULL AND length(trim(error_message)) > 0)
    )
);

CREATE INDEX IF NOT EXISTS idx_raw_item_translations_item_target
    ON raw_item_translations(raw_item_id, target_language, translation_version);

CREATE INDEX IF NOT EXISTS idx_raw_item_translations_origin
    ON raw_item_translations(underlying_origin_id, origin_kind);

CREATE INDEX IF NOT EXISTS idx_raw_item_translations_status_time
    ON raw_item_translations(status, created_at);
