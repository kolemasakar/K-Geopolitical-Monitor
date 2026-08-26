"""M11.4 temporal and causal queries over the durable advanced graph."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from typing import Iterable

from .advanced_graph import (
    ACTIVE,
    UPDATED,
    GraphEdge,
    SQLiteAdvancedGraphRepository,
)
from .operational_monitoring import _normalize_time, utc_now
from .relationship_lifecycle import RelationshipHistoryEntry, RelationshipLifecycleManager


CURRENT_STATUSES = {ACTIVE, UPDATED}
CAUSAL_RELATION_CLASSES = {"CAUSAL", "INFLUENCE"}


@dataclass(frozen=True)
class TemporalEdgeState:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    relation_class: str
    confidence: float
    status: str
    valid_from: datetime | None
    valid_to: datetime | None
    explanation: str
    as_of: datetime

    def is_effective_at(self, value: datetime) -> bool:
        current = _normalize_time(value)
        if self.status not in CURRENT_STATUSES:
            return False
        if self.valid_from is not None and current < _normalize_time(self.valid_from):
            return False
        if self.valid_to is not None and current > _normalize_time(self.valid_to):
            return False
        return True


@dataclass(frozen=True)
class CausalPath:
    node_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    relation_types: tuple[str, ...]

    @property
    def depth(self) -> int:
        return len(self.edge_ids)


class TemporalCausalGraph:
    """Deterministic temporal snapshots and bounded causal traversal."""

    def __init__(self, repository: SQLiteAdvancedGraphRepository):
        self.repository = repository
        self.lifecycle = RelationshipLifecycleManager(repository)

    @staticmethod
    def _state_dict(edge: GraphEdge) -> dict:
        return {
            "relation_class": edge.relation_class,
            "confidence": float(edge.confidence),
            "status": edge.status,
            "valid_from": _normalize_time(edge.valid_from).isoformat() if edge.valid_from else None,
            "valid_to": _normalize_time(edge.valid_to).isoformat() if edge.valid_to else None,
            "explanation": edge.explanation,
        }

    @staticmethod
    def _parse_time(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def history(self, edge_id: str) -> tuple[RelationshipHistoryEntry, ...]:
        return self.lifecycle.history(edge_id)

    def _material_transitions(self, edge_id: str) -> list[tuple[datetime, dict, dict]]:
        with sqlite3.connect(self.repository.database_path) as connection:
            rows = connection.execute(
                """
                SELECT payload_json, recorded_at
                FROM graph_edge_history
                WHERE edge_id = ?
                ORDER BY recorded_at, history_id
                """,
                (edge_id,),
            ).fetchall()

        transitions: list[tuple[datetime, dict, dict]] = []
        for payload_json, recorded_at in rows:
            payload = json.loads(payload_json)
            previous = payload.get("previous")
            current = payload.get("current")
            if isinstance(previous, dict) and isinstance(current, dict):
                transitions.append((datetime.fromisoformat(recorded_at), previous, current))
        return transitions

    def state_at(self, edge_id: str, at: datetime) -> TemporalEdgeState | None:
        requested = _normalize_time(at)
        edge = self.repository.get_edge(edge_id)
        if edge is None:
            return None
        if requested < _normalize_time(edge.created_at):
            return None

        transitions = self._material_transitions(edge_id)
        if transitions:
            state = dict(transitions[0][1])
            for recorded_at, _previous, current in transitions:
                if _normalize_time(recorded_at) <= requested:
                    state = dict(current)
                else:
                    break
        else:
            state = self._state_dict(edge)

        return TemporalEdgeState(
            edge_id=edge.edge_id,
            source_node_id=edge.source_node_id,
            target_node_id=edge.target_node_id,
            relation_type=edge.relation_type,
            relation_class=str(state["relation_class"]),
            confidence=float(state["confidence"]),
            status=str(state["status"]),
            valid_from=self._parse_time(state.get("valid_from")),
            valid_to=self._parse_time(state.get("valid_to")),
            explanation=str(state["explanation"]),
            as_of=requested,
        )

    def snapshot_at(
        self,
        at: datetime,
        *,
        include_inactive: bool = False,
        relation_classes: Iterable[str] | None = None,
    ) -> tuple[TemporalEdgeState, ...]:
        requested = _normalize_time(at)
        allowed_classes = (
            {str(value).strip().upper() for value in relation_classes}
            if relation_classes is not None
            else None
        )
        states: list[TemporalEdgeState] = []
        for edge in self.repository.list_edges():
            state = self.state_at(edge.edge_id, requested)
            if state is None:
                continue
            if allowed_classes is not None and state.relation_class not in allowed_classes:
                continue
            if not include_inactive and not state.is_effective_at(requested):
                continue
            states.append(state)
        return tuple(sorted(states, key=lambda item: item.edge_id))

    def current_edges(
        self,
        *,
        as_of: datetime | None = None,
        relation_classes: Iterable[str] | None = None,
    ) -> tuple[TemporalEdgeState, ...]:
        return self.snapshot_at(
            _normalize_time(as_of or utc_now()),
            include_inactive=False,
            relation_classes=relation_classes,
        )

    def _causal_edge_order_key(self, edge: TemporalEdgeState) -> tuple[str, str, str, str]:
        target = self.repository.get_node(edge.target_node_id)
        if target is None:
            return ("", edge.target_node_id, edge.relation_type, edge.edge_id)
        return (
            target.canonical_ref_type,
            target.canonical_ref_id,
            edge.relation_type,
            edge.edge_id,
        )

    def causal_paths(
        self,
        start_node_id: str,
        *,
        max_depth: int = 5,
        as_of: datetime | None = None,
        max_paths: int = 100,
    ) -> tuple[CausalPath, ...]:
        start = str(start_node_id).strip()
        if not start:
            raise ValueError("start_node_id must not be empty")
        if max_depth <= 0:
            raise ValueError("max_depth must be positive")
        if max_paths <= 0:
            raise ValueError("max_paths must be positive")

        effective_at = _normalize_time(as_of or utc_now())
        edges = self.snapshot_at(
            effective_at,
            relation_classes=CAUSAL_RELATION_CLASSES,
        )
        adjacency: dict[str, list[TemporalEdgeState]] = {}
        for edge in edges:
            adjacency.setdefault(edge.source_node_id, []).append(edge)
        for outgoing in adjacency.values():
            outgoing.sort(key=self._causal_edge_order_key)

        queue: list[tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = [
            ((start,), (), ())
        ]
        results: list[CausalPath] = []
        while queue and len(results) < max_paths:
            node_ids, edge_ids, relation_types = queue.pop(0)
            if len(edge_ids) >= max_depth:
                continue
            current_node = node_ids[-1]
            for edge in adjacency.get(current_node, []):
                if edge.target_node_id in node_ids:
                    continue
                next_nodes = (*node_ids, edge.target_node_id)
                next_edges = (*edge_ids, edge.edge_id)
                next_relations = (*relation_types, edge.relation_type)
                path = CausalPath(next_nodes, next_edges, next_relations)
                results.append(path)
                if len(results) >= max_paths:
                    break
                if path.depth < max_depth:
                    queue.append((next_nodes, next_edges, next_relations))

        return tuple(results)


__all__ = [
    "CURRENT_STATUSES",
    "CAUSAL_RELATION_CLASSES",
    "TemporalEdgeState",
    "CausalPath",
    "TemporalCausalGraph",
]
