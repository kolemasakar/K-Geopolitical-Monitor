from dataclasses import dataclass
from typing import Any

@dataclass
class QueryResult:
    query: str
    findings: list[Any]
    confidence: float = 0.0


class IntelligenceQuery:
    def __init__(self, graph=None):
        self.graph = graph

    def find_entity(self, entity_id):
        if self.graph is None:
            return None
        return self.graph.nodes.get(entity_id)

    def query(self, text: str) -> QueryResult:
        return QueryResult(query=text, findings=[], confidence=0.0)
