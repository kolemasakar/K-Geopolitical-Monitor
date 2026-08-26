"""M11.3 evidence-backed geopolitical relationship lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import sqlite3
from typing import Iterable

from .advanced_graph import (
    ACTIVE,
    CONTEXT,
    CONTRADICTS,
    INVALIDATED,
    RESOLVED,
    SUPPORTS,
    UPDATED,
    GraphEdge,
    GraphEdgeEvidence,
    SQLiteAdvancedGraphRepository,
)
from .operational_monitoring import _normalize_time


@dataclass(frozen=True)
class RelationshipHistoryEntry:
    history_id: str
    edge_id: str
    event_type: str
    status: str
    payload: dict
    recorded_at: datetime


def _edge_snapshot(edge: GraphEdge) -> dict:
    return {
        "relation_class": edge.relation_class,
        "confidence": float(edge.confidence),
        "status": edge.status,
        "valid_from": _normalize_time(edge.valid_from).isoformat() if edge.valid_from else None,
        "valid_to": _normalize_time(edge.valid_to).isoformat() if edge.valid_to else None,
        "explanation": edge.explanation,
    }


def _history_id(edge_id: str, event_type: str, recorded_at: datetime, payload: dict) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = sha256(
        f"{edge_id}\x1f{event_type}\x1f{_normalize_time(recorded_at).isoformat()}\x1f{material}".encode(
            "utf-8"
        )
    ).hexdigest()[:32]
    return f"ghist-{digest}"


class RelationshipLifecycleManager:
    """Adds material-change history and evidence semantics around the durable graph store."""

    def __init__(self, repository: SQLiteAdvancedGraphRepository):
        self.repository = repository

    def save_relationship(
        self,
        edge: GraphEdge,
        *,
        evidence: Iterable[GraphEdgeEvidence] = (),
    ) -> GraphEdge:
        evidence_items = tuple(evidence)
        for item in evidence_items:
            if item.edge_id != edge.edge_id:
                raise ValueError("relationship evidence must reference the saved edge")

        previous = self.repository.get_edge(edge.edge_id)
        self.repository.save_edge(edge)

        for item in evidence_items:
            self.repository.add_edge_evidence(item)

        if previous is not None:
            before = _edge_snapshot(previous)
            after = _edge_snapshot(edge)
            if before != after:
                event_type = (
                    f"STATUS_{edge.status}"
                    if previous.status != edge.status
                    else "RELATIONSHIP_UPDATED"
                )
                payload = {"previous": before, "current": after}
                recorded_at = _normalize_time(edge.updated_at)
                history_id = _history_id(edge.edge_id, event_type, recorded_at, payload)
                with sqlite3.connect(self.repository.database_path) as connection:
                    connection.execute("PRAGMA foreign_keys = ON")
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO graph_edge_history(
                            history_id, edge_id, event_type, status, payload_json, recorded_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            history_id,
                            edge.edge_id,
                            event_type,
                            edge.status,
                            json.dumps(payload, sort_keys=True),
                            recorded_at.isoformat(),
                        ),
                    )

        return self.repository.get_edge(edge.edge_id) or edge

    def transition(
        self,
        edge_id: str,
        *,
        status: str,
        observed_at: datetime,
        confidence: float | None = None,
        explanation: str | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        evidence: Iterable[GraphEdgeEvidence] = (),
    ) -> GraphEdge:
        current = self.repository.get_edge(edge_id)
        if current is None:
            raise ValueError("graph relationship does not exist")

        observed = _normalize_time(observed_at)
        new_status = str(status).strip().upper()
        if new_status not in {ACTIVE, UPDATED, INVALIDATED, RESOLVED}:
            raise ValueError(f"unsupported graph edge status: {new_status}")

        next_edge = GraphEdge(
            edge_id=current.edge_id,
            source_node_id=current.source_node_id,
            target_node_id=current.target_node_id,
            relation_type=current.relation_type,
            relation_class=current.relation_class,
            confidence=current.confidence if confidence is None else float(confidence),
            status=new_status,
            first_observed_at=current.first_observed_at,
            last_observed_at=max(current.last_observed_at, observed),
            explanation=current.explanation if explanation is None else explanation,
            valid_from=current.valid_from if valid_from is None else valid_from,
            valid_to=current.valid_to if valid_to is None else valid_to,
            created_at=current.created_at,
            updated_at=observed,
        )
        return self.save_relationship(next_edge, evidence=evidence)

    def add_evidence(
        self,
        edge_id: str,
        evidence_ref: str,
        evidence_role: str,
        *,
        added_at: datetime,
    ) -> GraphEdgeEvidence:
        if self.repository.get_edge(edge_id) is None:
            raise ValueError("graph relationship does not exist")
        evidence = GraphEdgeEvidence(
            edge_id=edge_id,
            evidence_ref=evidence_ref,
            evidence_role=evidence_role,
            added_at=added_at,
        )
        self.repository.add_edge_evidence(evidence)
        return evidence

    def history(self, edge_id: str) -> tuple[RelationshipHistoryEntry, ...]:
        with sqlite3.connect(self.repository.database_path) as connection:
            rows = connection.execute(
                """
                SELECT history_id, edge_id, event_type, status, payload_json, recorded_at
                FROM graph_edge_history
                WHERE edge_id = ?
                ORDER BY recorded_at, history_id
                """,
                (edge_id,),
            ).fetchall()
        return tuple(
            RelationshipHistoryEntry(
                history_id=row[0],
                edge_id=row[1],
                event_type=row[2],
                status=row[3],
                payload=json.loads(row[4]),
                recorded_at=datetime.fromisoformat(row[5]),
            )
            for row in rows
        )


__all__ = [
    "ACTIVE",
    "UPDATED",
    "INVALIDATED",
    "RESOLVED",
    "SUPPORTS",
    "CONTRADICTS",
    "CONTEXT",
    "RelationshipHistoryEntry",
    "RelationshipLifecycleManager",
]
