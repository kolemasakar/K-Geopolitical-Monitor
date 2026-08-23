CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_class TEXT,
    reliability TEXT
);

CREATE TABLE IF NOT EXISTS raw_items (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    title TEXT,
    content TEXT,
    collected_at TEXT,
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT,
    importance TEXT
);
