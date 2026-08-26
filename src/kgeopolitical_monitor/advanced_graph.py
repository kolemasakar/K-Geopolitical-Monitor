"""M11 durable project-local advanced geopolitical graph baseline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

from .database import initialize_database
from .operational_monitoring import _normalize_time, utc_now


ACTIVE = "ACTIVE"
UPDATED = "UPDATED"
INVALIDATED = "INVALIDATED"
RESOLVED = "RESOLVED"

SUPPORTS = "SUPPORTS"
CONTRADICTS = "CONTRADICTS"
CONTEXT = "CONTEXT"

BASELINE_NODE_KINDS = (
    "ACTOR",
    "EVENT",
    "CLAIM",
    "FINDING",
    "SOURCE",
    "REGION",
)

BASELINE_RELATION_CLASSES = (
    "STRUCTURAL",
    "PARTICIPATION",
    "POLITICAL",
    "SECURITY",
    "ECONOMIC",
    "CAUSAL",
    "INFLUENCE",
    "TEMPORAL",
    "CONTEXTUAL",
)


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _upper_token(value: str, field_name: str) -> str:
    return _nonempty(value, field_name).upper()


def _stable_id(prefix: str, *parts: str) -> str:
    material = "\x1f".join(parts)
    digest = sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def graph_node_id(canonical_ref_type: str, canonical_ref_id: str) -> str:
    return _stable_id(
        "gnode",
        _upper_token(canonical_ref_type, "canonical_ref_type"),
        _nonempty(canonical_ref_id, "canonical_ref_id"),
    )


def graph_edge_id(source_node_id: str, target_node_id: str, relation_type: str) -> str:
    return _stable_id(
        "gedge",
        _nonempty(source_node_id, "source_node_id"),
        _nonempty(target_node_id, "target_node_id"),
        _upper_token(relation_type, "relation_type"),
    )


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_kind: str
    canonical_ref_type: str
    canonical_ref_id: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        ref_type = _upper_token(self.canonical_ref_type, "canonical_ref_type")
        ref_id = _nonempty(self.canonical_ref_id, "canonical_ref_id")
        node_kind = _upper_token(self.node_kind, "node_kind")
        label = _nonempty(self.label, "label")
        expected_id = graph_node_id(ref_type, ref_id)
        if self.node_id != expected_id:
            raise ValueError("node_id must match deterministic canonical graph identity")
        _normalize_time(self.created_at)
        _normalize_time(self.updated_at)
        json.dumps(self.attributes, sort_keys=True)
        object.__setattr__(self, "canonical_ref_type", ref_type)
        object.__setattr__(self, "canonical_ref_id", ref_id)
        object.__setattr__(self, "node_kind", node_kind)
        object.__setattr__(self, "label", label)

    @classmethod
    def from_canonical(
        cls,
        canonical_ref_type: str,
        canonical_ref_id: str,
        node_kind: str,
        label: str,
        *,
        attributes: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "GraphNode":
        created = created_at or utc_now()
        updated = updated_at or created
        return cls(
            node_id=graph_node_id(canonical_ref_type, canonical_ref_id),
            node_kind=node_kind,
            canonical_ref_type=canonical_ref_type,
            canonical_ref_id=canonical_ref_id,
            label=label,
            attributes=dict(attributes or {}),
            created_at=created,
            updated_at=updated,
        )


@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    relation_class: str
    confidence: float
    status: str
    first_observed_at: datetime
    last_observed_at: datetime
    explanation: str
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        source = _nonempty(self.source_node_id, "source_node_id")
        target = _nonempty(self.target_node_id, "target_node_id")
        relation_type = _upper_token(self.relation_type, "relation_type")
        relation_class = _upper_token(self.relation_class, "relation_class")
        status = _upper_token(self.status, "status")
        if relation_class not in BASELINE_RELATION_CLASSES:
            raise ValueError(f"unsupported relation_class: {relation_class}")
        if status not in {ACTIVE, UPDATED, INVALIDATED, RESOLVED}:
            raise ValueError(f"unsupported graph edge status: {status}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        explanation = _nonempty(self.explanation, "explanation")
        first = _normalize_time(self.first_observed_at)
        last = _normalize_time(self.last_observed_at)
        if last < first:
            raise ValueError("last_observed_at must not precede first_observed_at")
        valid_from = _normalize_time(self.valid_from) if self.valid_from is not None else None
        valid_to = _normalize_time(self.valid_to) if self.valid_to is not None else None
        if valid_from is not None and valid_to is not None and valid_to < valid_from:
            raise ValueError("valid_to must not precede valid_from")
        _normalize_time(self.created_at)
        _normalize_time(self.updated_at)
        expected_id = graph_edge_id(source, target, relation_type)
        if self.edge_id != expected_id:
            raise ValueError("edge_id must match deterministic graph relation identity")
        object.__setattr__(self, "source_node_id", source)
        object.__setattr__(self, "target_node_id", target)
        object.__setattr__(self, "relation_type", relation_type)
        object.__setattr__(self, "relation_class", relation_class)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "explanation", explanation)

    @classmethod
    def between(
        cls,
        source_node_id: str,
        target_node_id: str,
        relation_type: str,
        relation_class: str,
        confidence: float,
        explanation: str,
        *,
        observed_at: datetime,
        status: str = ACTIVE,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "GraphEdge":
        created = created_at or observed_at
        updated = updated_at or created
        return cls(
            edge_id=graph_edge_id(source_node_id, target_node_id, relation_type),
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            relation_class=relation_class,
            confidence=float(confidence),
            status=status,
            first_observed_at=observed_at,
            last_observed_at=observed_at,
            explanation=explanation,
            valid_from=valid_from,
            valid_to=valid_to,
            created_at=created,
            updated_at=updated,
        )


@dataclass(frozen=True)
class GraphEdgeEvidence:
    edge_id: str
    evidence_ref: str
    evidence_role: str
    added_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _nonempty(self.edge_id, "edge_id")
        _nonempty(self.evidence_ref, "evidence_ref")
        role = _upper_token(self.evidence_role, "evidence_role")
        if role not in {SUPPORTS, CONTRADICTS, CONTEXT}:
            raise ValueError(f"unsupported evidence_role: {role}")
        _normalize_time(self.added_at)
        object.__setattr__(self, "evidence_role", role)


class SQLiteAdvancedGraphRepository:
    """Durable graph storage using the canonical project-local SQLite database."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    def save_node(self, node: GraphNode) -> GraphNode:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO graph_nodes(
                    node_id, node_kind, canonical_ref_type, canonical_ref_id,
                    label, attributes_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    node_kind = excluded.node_kind,
                    label = excluded.label,
                    attributes_json = excluded.attributes_json,
                    updated_at = excluded.updated_at
                """,
                (
                    node.node_id,
                    node.node_kind,
                    node.canonical_ref_type,
                    node.canonical_ref_id,
                    node.label,
                    json.dumps(node.attributes, sort_keys=True),
                    _normalize_time(node.created_at).isoformat(),
                    _normalize_time(node.updated_at).isoformat(),
                ),
            )
        return node

    def get_node(self, node_id: str) -> GraphNode | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT node_id, node_kind, canonical_ref_type, canonical_ref_id,
                       label, attributes_json, created_at, updated_at
                FROM graph_nodes
                WHERE node_id = ?
                """,
                (node_id,),
            ).fetchone()
        return self._node_from_row(row) if row is not None else None

    def get_node_by_canonical(
        self,
        canonical_ref_type: str,
        canonical_ref_id: str,
    ) -> GraphNode | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT node_id, node_kind, canonical_ref_type, canonical_ref_id,
                       label, attributes_json, created_at, updated_at
                FROM graph_nodes
                WHERE canonical_ref_type = ? AND canonical_ref_id = ?
                """,
                (
                    _upper_token(canonical_ref_type, "canonical_ref_type"),
                    _nonempty(canonical_ref_id, "canonical_ref_id"),
                ),
            ).fetchone()
        return self._node_from_row(row) if row is not None else None

    def save_edge(self, edge: GraphEdge) -> GraphEdge:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            existing = connection.execute(
                "SELECT 1 FROM graph_edges WHERE edge_id = ?",
                (edge.edge_id,),
            ).fetchone()
            connection.execute(
                """
                INSERT INTO graph_edges(
                    edge_id, source_node_id, target_node_id, relation_type,
                    relation_class, confidence, status, valid_from, valid_to,
                    first_observed_at, last_observed_at, explanation,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(edge_id) DO UPDATE SET
                    relation_class = excluded.relation_class,
                    confidence = excluded.confidence,
                    status = excluded.status,
                    valid_from = excluded.valid_from,
                    valid_to = excluded.valid_to,
                    first_observed_at = MIN(graph_edges.first_observed_at, excluded.first_observed_at),
                    last_observed_at = MAX(graph_edges.last_observed_at, excluded.last_observed_at),
                    explanation = excluded.explanation,
                    updated_at = excluded.updated_at
                """,
                (
                    edge.edge_id,
                    edge.source_node_id,
                    edge.target_node_id,
                    edge.relation_type,
                    edge.relation_class,
                    edge.confidence,
                    edge.status,
                    self._iso_or_none(edge.valid_from),
                    self._iso_or_none(edge.valid_to),
                    _normalize_time(edge.first_observed_at).isoformat(),
                    _normalize_time(edge.last_observed_at).isoformat(),
                    edge.explanation,
                    _normalize_time(edge.created_at).isoformat(),
                    _normalize_time(edge.updated_at).isoformat(),
                ),
            )
            if existing is None:
                history_id = _stable_id("ghist", edge.edge_id, "CREATED")
                connection.execute(
                    """
                    INSERT OR IGNORE INTO graph_edge_history(
                        history_id, edge_id, event_type, status, payload_json, recorded_at
                    ) VALUES (?, ?, 'CREATED', ?, '{}', ?)
                    """,
                    (
                        history_id,
                        edge.edge_id,
                        edge.status,
                        _normalize_time(edge.created_at).isoformat(),
                    ),
                )
        return edge

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT edge_id, source_node_id, target_node_id, relation_type,
                       relation_class, confidence, status, valid_from, valid_to,
                       first_observed_at, last_observed_at, explanation,
                       created_at, updated_at
                FROM graph_edges
                WHERE edge_id = ?
                """,
                (edge_id,),
            ).fetchone()
        return self._edge_from_row(row) if row is not None else None

    def list_edges(
        self,
        *,
        node_id: str | None = None,
        status: str | None = None,
        relation_type: str | None = None,
    ) -> list[GraphEdge]:
        clauses: list[str] = []
        params: list[object] = []
        if node_id is not None:
            clauses.append("(source_node_id = ? OR target_node_id = ?)")
            params.extend((node_id, node_id))
        if status is not None:
            clauses.append("status = ?")
            params.append(_upper_token(status, "status"))
        if relation_type is not None:
            clauses.append("relation_type = ?")
            params.append(_upper_token(relation_type, "relation_type"))

        query = (
            "SELECT edge_id, source_node_id, target_node_id, relation_type, "
            "relation_class, confidence, status, valid_from, valid_to, "
            "first_observed_at, last_observed_at, explanation, created_at, updated_at "
            "FROM graph_edges"
        )
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY edge_id"

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._edge_from_row(row) for row in rows]

    def add_edge_evidence(self, evidence: GraphEdgeEvidence) -> GraphEdgeEvidence:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT OR IGNORE INTO graph_edge_evidence(
                    edge_id, evidence_ref, evidence_role, added_at
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    evidence.edge_id,
                    evidence.evidence_ref,
                    evidence.evidence_role,
                    _normalize_time(evidence.added_at).isoformat(),
                ),
            )
        return evidence

    def list_edge_evidence(self, edge_id: str) -> list[GraphEdgeEvidence]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT edge_id, evidence_ref, evidence_role, added_at
                FROM graph_edge_evidence
                WHERE edge_id = ?
                ORDER BY evidence_role, evidence_ref
                """,
                (edge_id,),
            ).fetchall()
        return [
            GraphEdgeEvidence(
                edge_id=row[0],
                evidence_ref=row[1],
                evidence_role=row[2],
                added_at=datetime.fromisoformat(row[3]),
            )
            for row in rows
        ]

    def history_count(self, edge_id: str) -> int:
        with sqlite3.connect(self.database_path) as connection:
            return int(
                connection.execute(
                    "SELECT COUNT(*) FROM graph_edge_history WHERE edge_id = ?",
                    (edge_id,),
                ).fetchone()[0]
            )

    @staticmethod
    def _iso_or_none(value: datetime | None) -> str | None:
        return _normalize_time(value).isoformat() if value is not None else None

    @staticmethod
    def _node_from_row(row: tuple) -> GraphNode:
        return GraphNode(
            node_id=row[0],
            node_kind=row[1],
            canonical_ref_type=row[2],
            canonical_ref_id=row[3],
            label=row[4],
            attributes=json.loads(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
        )

    @staticmethod
    def _edge_from_row(row: tuple) -> GraphEdge:
        return GraphEdge(
            edge_id=row[0],
            source_node_id=row[1],
            target_node_id=row[2],
            relation_type=row[3],
            relation_class=row[4],
            confidence=float(row[5]),
            status=row[6],
            valid_from=datetime.fromisoformat(row[7]) if row[7] else None,
            valid_to=datetime.fromisoformat(row[8]) if row[8] else None,
            first_observed_at=datetime.fromisoformat(row[9]),
            last_observed_at=datetime.fromisoformat(row[10]),
            explanation=row[11],
            created_at=datetime.fromisoformat(row[12]),
            updated_at=datetime.fromisoformat(row[13]),
        )


def project_m4_knowledge_graph(
    graph: Any,
    repository: SQLiteAdvancedGraphRepository,
    *,
    observed_at: datetime,
) -> tuple[int, int]:
    """Project the validated M4 in-memory graph into the durable M11 store."""

    current = _normalize_time(observed_at)
    node_map: dict[str, str] = {}
    node_count = 0
    edge_count = 0

    for legacy_id in sorted(graph.nodes):
        legacy = graph.nodes[legacy_id]
        node = GraphNode.from_canonical(
            "M4_NODE",
            str(legacy.node_id),
            str(legacy.node_type),
            str(legacy.attributes.get("name", legacy.node_id)),
            attributes=dict(legacy.attributes),
            created_at=current,
            updated_at=current,
        )
        repository.save_node(node)
        node_map[str(legacy.node_id)] = node.node_id
        node_count += 1

    ordered_edges: Iterable[Any] = sorted(
        graph.edges,
        key=lambda item: (str(item.source), str(item.target), str(item.relation)),
    )
    for legacy in ordered_edges:
        source_id = node_map[str(legacy.source)]
        target_id = node_map[str(legacy.target)]
        edge = GraphEdge.between(
            source_id,
            target_id,
            str(legacy.relation),
            "CONTEXTUAL",
            float(legacy.confidence),
            "Projected from validated M4 KnowledgeGraph compatibility interface.",
            observed_at=current,
        )
        repository.save_edge(edge)
        repository.add_edge_evidence(
            GraphEdgeEvidence(
                edge_id=edge.edge_id,
                evidence_ref=f"compat:m4:{legacy.source}:{legacy.target}:{legacy.relation}",
                evidence_role=CONTEXT,
                added_at=current,
            )
        )
        edge_count += 1

    return node_count, edge_count
