CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id TEXT PRIMARY KEY,
    node_kind TEXT NOT NULL,
    canonical_ref_type TEXT NOT NULL,
    canonical_ref_id TEXT NOT NULL,
    label TEXT NOT NULL,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(canonical_ref_type, canonical_ref_id)
);

CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    relation_class TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'UPDATED', 'INVALIDATED', 'RESOLVED')),
    valid_from TEXT,
    valid_to TEXT,
    first_observed_at TEXT NOT NULL,
    last_observed_at TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(source_node_id) REFERENCES graph_nodes(node_id),
    FOREIGN KEY(target_node_id) REFERENCES graph_nodes(node_id),
    UNIQUE(source_node_id, target_node_id, relation_type)
);

CREATE TABLE IF NOT EXISTS graph_edge_evidence (
    edge_id TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    evidence_role TEXT NOT NULL CHECK (evidence_role IN ('SUPPORTS', 'CONTRADICTS', 'CONTEXT')),
    added_at TEXT NOT NULL,
    PRIMARY KEY(edge_id, evidence_ref, evidence_role),
    FOREIGN KEY(edge_id) REFERENCES graph_edges(edge_id)
);

CREATE TABLE IF NOT EXISTS graph_edge_history (
    history_id TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'UPDATED', 'INVALIDATED', 'RESOLVED')),
    payload_json TEXT NOT NULL DEFAULT '{}',
    recorded_at TEXT NOT NULL,
    FOREIGN KEY(edge_id) REFERENCES graph_edges(edge_id)
);

CREATE INDEX IF NOT EXISTS idx_graph_nodes_kind
    ON graph_nodes(node_kind);

CREATE INDEX IF NOT EXISTS idx_graph_edges_source_status
    ON graph_edges(source_node_id, status);

CREATE INDEX IF NOT EXISTS idx_graph_edges_target_status
    ON graph_edges(target_node_id, status);

CREATE INDEX IF NOT EXISTS idx_graph_edges_relation_status
    ON graph_edges(relation_type, status);

CREATE INDEX IF NOT EXISTS idx_graph_edge_history_edge_recorded
    ON graph_edge_history(edge_id, recorded_at);
