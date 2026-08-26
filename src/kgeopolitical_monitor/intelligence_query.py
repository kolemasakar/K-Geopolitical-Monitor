"""Explainable intelligence query baseline for the knowledge graph."""

from dataclasses import dataclass
from typing import Any


@dataclass
class QueryResult:
    query: str
    findings: list[Any]
    confidence: float = 0.0


class IntelligenceQuery:
    def __init__(self, graph=None, causal_engine=None):
        self.graph = graph
        self.causal_engine = causal_engine

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
