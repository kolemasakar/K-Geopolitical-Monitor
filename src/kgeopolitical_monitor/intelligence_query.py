"""Explainable intelligence query facade for legacy and durable graph layers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from .advanced_graph import SQLiteAdvancedGraphRepository
from .operational_monitoring import _normalize_time, utc_now
from .temporal_causal_graph import TemporalCausalGraph, TemporalEdgeState


@dataclass
class QueryResult:
    query: str
    findings: list[Any]
    confidence: float = 0.0


@dataclass(frozen=True)
class AdvancedQueryResult:
    query_type: str
    as_of: str
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]
    paths: tuple[dict[str, Any], ...] = ()

    def explanation(self) -> dict[str, Any]:
        graph_ids = sorted(
            {item["node_id"] for item in self.nodes}
            | {item["edge_id"] for item in self.edges}
        )
        canonical_refs = sorted(
            {
                f"{item['canonical_ref_type']}:{item['canonical_ref_id']}"
                for item in self.nodes
            }
        )
        evidence_refs = sorted(
            {
                evidence["evidence_ref"]
                for edge in self.edges
                for evidence in edge.get("evidence", ())
            }
        )
        return {
            "query_type": self.query_type,
            "as_of": self.as_of,
            "graph_ids": graph_ids,
            "canonical_refs": canonical_refs,
            "evidence_refs": evidence_refs,
            "path_count": len(self.paths),
        }


class IntelligenceQuery:
    def __init__(
        self,
        graph=None,
        causal_engine=None,
        advanced_repository: SQLiteAdvancedGraphRepository | None = None,
        temporal_graph: TemporalCausalGraph | None = None,
    ):
        self.graph = graph
        self.causal_engine = causal_engine
        self.advanced_repository = advanced_repository
        self.temporal_graph = temporal_graph or (
            TemporalCausalGraph(advanced_repository)
            if advanced_repository is not None
            else None
        )

    # M4 compatibility facade.
    def find_entity(self, entity_id):
        if self.graph is None:
            return None
        return self.graph.nodes.get(entity_id)

    def find_relations(self, entity_id):
        if self.graph is None:
            return []
        return [
            edge
            for edge in self.graph.edges
            if edge.source == entity_id or edge.target == entity_id
        ]

    def trace_causal_chain(self, cause: str, max_depth: int = 5):
        if self.causal_engine is None or max_depth <= 0:
            return []

        chain = []
        frontier = [(cause, 0)]
        visited_links = set()

        while frontier:
            current, depth = frontier.pop(0)
            if depth >= max_depth:
                continue

            for link in self.causal_engine.get_effects(current):
                key = (link.cause, link.effect)
                if key in visited_links:
                    continue
                visited_links.add(key)
                chain.append(link)
                frontier.append((link.effect, depth + 1))

        return chain

    def query(self, text: str) -> QueryResult:
        if self.graph is None:
            return QueryResult(query=text, findings=[], confidence=0.0)

        needle = text.strip().lower()
        if not needle:
            return QueryResult(query=text, findings=[], confidence=0.0)

        findings = []
        matching_edge_confidences = []
        exact_entity_match = False

        for node in self.graph.nodes.values():
            searchable = [node.node_id, node.node_type]
            searchable.extend(node.attributes.keys())
            searchable.extend(node.attributes.values())

            if node.node_id.lower() == needle:
                exact_entity_match = True

            if any(needle in str(value).lower() for value in searchable):
                findings.append(node)

        for edge in self.graph.edges:
            searchable = [edge.source, edge.target, edge.relation]
            if any(needle in str(value).lower() for value in searchable):
                findings.append(edge)
                matching_edge_confidences.append(edge.confidence)

        if exact_entity_match:
            confidence = 1.0
        elif matching_edge_confidences:
            confidence = sum(matching_edge_confidences) / len(matching_edge_confidences)
        elif findings:
            confidence = 0.5
        else:
            confidence = 0.0

        return QueryResult(query=text, findings=findings, confidence=confidence)

    def build_explanation(self, query_text: str):
        result = self.query(query_text)
        evidence = []

        for item in result.findings:
            if hasattr(item, "node_id"):
                evidence.append(
                    {
                        "type": "node",
                        "id": item.node_id,
                        "node_type": item.node_type,
                    }
                )
            elif hasattr(item, "source") and hasattr(item, "target"):
                evidence.append(
                    {
                        "type": "edge",
                        "source": item.source,
                        "target": item.target,
                        "relation": item.relation,
                        "confidence": item.confidence,
                    }
                )

        return {
            "query": query_text,
            "evidence": evidence,
            "confidence": result.confidence,
        }

    # M11 durable advanced graph facade.
    def _advanced(self) -> tuple[SQLiteAdvancedGraphRepository, TemporalCausalGraph]:
        if self.advanced_repository is None or self.temporal_graph is None:
            raise ValueError("advanced graph backend is not configured")
        return self.advanced_repository, self.temporal_graph

    @staticmethod
    def _node_payload(node) -> dict[str, Any]:
        return {
            "node_id": node.node_id,
            "node_kind": node.node_kind,
            "canonical_ref_type": node.canonical_ref_type,
            "canonical_ref_id": node.canonical_ref_id,
            "label": node.label,
            "attributes": dict(node.attributes),
        }

    def _edge_payload(self, state: TemporalEdgeState) -> dict[str, Any]:
        repository, _ = self._advanced()
        evidence = repository.list_edge_evidence(state.edge_id)
        return {
            "edge_id": state.edge_id,
            "source_node_id": state.source_node_id,
            "target_node_id": state.target_node_id,
            "relation_type": state.relation_type,
            "relation_class": state.relation_class,
            "confidence": state.confidence,
            "status": state.status,
            "valid_from": state.valid_from.isoformat() if state.valid_from else None,
            "valid_to": state.valid_to.isoformat() if state.valid_to else None,
            "explanation": state.explanation,
            "evidence": tuple(
                {
                    "evidence_ref": item.evidence_ref,
                    "evidence_role": item.evidence_role,
                }
                for item in evidence
            ),
        }

    def _result(
        self,
        query_type: str,
        at: datetime,
        *,
        nodes: Iterable[Any],
        edges: Iterable[TemporalEdgeState],
        paths: Iterable[dict[str, Any]] = (),
    ) -> AdvancedQueryResult:
        node_payloads = tuple(
            sorted(
                (self._node_payload(node) for node in nodes if node is not None),
                key=lambda item: (
                    item["canonical_ref_type"],
                    item["canonical_ref_id"],
                    item["node_id"],
                ),
            )
        )
        edge_payloads = tuple(
            sorted(
                (self._edge_payload(edge) for edge in edges),
                key=lambda item: item["edge_id"],
            )
        )
        return AdvancedQueryResult(
            query_type=query_type,
            as_of=_normalize_time(at).isoformat(),
            nodes=node_payloads,
            edges=edge_payloads,
            paths=tuple(paths),
        )

    def direct_neighborhood(
        self,
        node_id: str,
        *,
        as_of: datetime | None = None,
        include_historical: bool = False,
    ) -> AdvancedQueryResult:
        repository, temporal = self._advanced()
        at = _normalize_time(as_of or utc_now())
        focal = repository.get_node(node_id)
        if focal is None:
            raise ValueError("graph node does not exist")
        states = temporal.snapshot_at(at, include_inactive=include_historical)
        edges = tuple(
            state
            for state in states
            if state.source_node_id == node_id or state.target_node_id == node_id
        )
        neighbor_ids = {
            state.target_node_id if state.source_node_id == node_id else state.source_node_id
            for state in edges
        }
        nodes = [focal, *(repository.get_node(value) for value in sorted(neighbor_ids))]
        return self._result("DIRECT_NEIGHBORHOOD", at, nodes=nodes, edges=edges)

    def multi_hop_paths(
        self,
        start_node_id: str,
        target_node_id: str,
        *,
        max_depth: int = 4,
        as_of: datetime | None = None,
        relation_classes: Iterable[str] | None = None,
        max_paths: int = 100,
    ) -> AdvancedQueryResult:
        repository, temporal = self._advanced()
        at = _normalize_time(as_of or utc_now())
        if max_depth <= 0:
            raise ValueError("max_depth must be positive")
        if max_paths <= 0:
            raise ValueError("max_paths must be positive")
        if repository.get_node(start_node_id) is None or repository.get_node(target_node_id) is None:
            raise ValueError("start and target graph nodes must exist")

        states = temporal.snapshot_at(at, relation_classes=relation_classes)
        adjacency: dict[str, list[TemporalEdgeState]] = {}
        for state in states:
            adjacency.setdefault(state.source_node_id, []).append(state)
        for outgoing in adjacency.values():
            outgoing.sort(
                key=lambda edge: (
                    (repository.get_node(edge.target_node_id).canonical_ref_type if repository.get_node(edge.target_node_id) else ""),
                    (repository.get_node(edge.target_node_id).canonical_ref_id if repository.get_node(edge.target_node_id) else edge.target_node_id),
                    edge.relation_type,
                    edge.edge_id,
                )
            )

        queue: list[tuple[tuple[str, ...], tuple[str, ...]]] = [((start_node_id,), ())]
        path_records: list[dict[str, Any]] = []
        used_edge_ids: set[str] = set()
        used_node_ids: set[str] = {start_node_id, target_node_id}

        while queue and len(path_records) < max_paths:
            node_ids, edge_ids = queue.pop(0)
            if len(edge_ids) >= max_depth:
                continue
            for edge in adjacency.get(node_ids[-1], []):
                if edge.target_node_id in node_ids:
                    continue
                next_nodes = (*node_ids, edge.target_node_id)
                next_edges = (*edge_ids, edge.edge_id)
                if edge.target_node_id == target_node_id:
                    path_records.append(
                        {
                            "node_ids": next_nodes,
                            "edge_ids": next_edges,
                            "depth": len(next_edges),
                        }
                    )
                    used_edge_ids.update(next_edges)
                    used_node_ids.update(next_nodes)
                    if len(path_records) >= max_paths:
                        break
                elif len(next_edges) < max_depth:
                    queue.append((next_nodes, next_edges))

        edge_by_id = {state.edge_id: state for state in states}
        edges = [edge_by_id[value] for value in sorted(used_edge_ids)]
        nodes = [repository.get_node(value) for value in sorted(used_node_ids)]
        return self._result(
            "MULTI_HOP_PATHS",
            at,
            nodes=nodes,
            edges=edges,
            paths=path_records,
        )

    def actor_relationships(
        self,
        actor_a_ref: str,
        actor_b_ref: str,
        *,
        as_of: datetime | None = None,
        include_historical: bool = False,
    ) -> AdvancedQueryResult:
        repository, temporal = self._advanced()
        at = _normalize_time(as_of or utc_now())
        actor_a = repository.get_node_by_canonical("ACTOR", actor_a_ref)
        actor_b = repository.get_node_by_canonical("ACTOR", actor_b_ref)
        if actor_a is None or actor_b is None:
            raise ValueError("actor graph reference does not exist")
        states = temporal.snapshot_at(at, include_inactive=include_historical)
        edges = tuple(
            state
            for state in states
            if {state.source_node_id, state.target_node_id}
            == {actor_a.node_id, actor_b.node_id}
        )
        return self._result(
            "ACTOR_RELATIONSHIPS",
            at,
            nodes=(actor_a, actor_b),
            edges=edges,
        )

    def actor_events(
        self,
        actor_ref: str,
        *,
        as_of: datetime | None = None,
    ) -> AdvancedQueryResult:
        repository, temporal = self._advanced()
        at = _normalize_time(as_of or utc_now())
        actor = repository.get_node_by_canonical("ACTOR", actor_ref)
        if actor is None:
            raise ValueError("actor graph reference does not exist")
        states = temporal.snapshot_at(at, relation_classes={"PARTICIPATION"})
        edges: list[TemporalEdgeState] = []
        event_nodes = []
        for state in states:
            if actor.node_id not in {state.source_node_id, state.target_node_id}:
                continue
            other_id = (
                state.target_node_id
                if state.source_node_id == actor.node_id
                else state.source_node_id
            )
            other = repository.get_node(other_id)
            if other is not None and other.node_kind == "EVENT":
                edges.append(state)
                event_nodes.append(other)
        return self._result(
            "ACTOR_EVENTS",
            at,
            nodes=(actor, *event_nodes),
            edges=edges,
        )

    def relation_state(
        self,
        edge_id: str,
        *,
        at: datetime | None = None,
    ) -> AdvancedQueryResult:
        repository, temporal = self._advanced()
        requested = _normalize_time(at or utc_now())
        state = temporal.state_at(edge_id, requested)
        if state is None:
            raise ValueError("graph relationship does not exist at requested time")
        nodes = (
            repository.get_node(state.source_node_id),
            repository.get_node(state.target_node_id),
        )
        return self._result(
            "RELATION_STATE",
            requested,
            nodes=nodes,
            edges=(state,),
        )

    def advanced_causal_paths(
        self,
        start_node_id: str,
        *,
        max_depth: int = 5,
        as_of: datetime | None = None,
        max_paths: int = 100,
    ) -> AdvancedQueryResult:
        repository, temporal = self._advanced()
        at = _normalize_time(as_of or utc_now())
        paths = temporal.causal_paths(
            start_node_id,
            max_depth=max_depth,
            as_of=at,
            max_paths=max_paths,
        )
        edge_ids = {edge_id for path in paths for edge_id in path.edge_ids}
        node_ids = {node_id for path in paths for node_id in path.node_ids}
        states = {
            state.edge_id: state
            for state in temporal.snapshot_at(at, relation_classes={"CAUSAL", "INFLUENCE"})
        }
        return self._result(
            "CAUSAL_PATHS",
            at,
            nodes=(repository.get_node(value) for value in sorted(node_ids)),
            edges=(states[value] for value in sorted(edge_ids)),
            paths=(
                {
                    "node_ids": path.node_ids,
                    "edge_ids": path.edge_ids,
                    "relation_types": path.relation_types,
                    "depth": path.depth,
                }
                for path in paths
            ),
        )


__all__ = ["QueryResult", "AdvancedQueryResult", "IntelligenceQuery"]
