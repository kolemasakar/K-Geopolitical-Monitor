"""Knowledge Graph Core baseline.

Provides entities, nodes and graph relationships for intelligence analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class KnowledgeNode:
    node_id: str
    node_type: str
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class KnowledgeEdge:
    source: str
    target: str
    relation: str
    confidence: float = 0.0


class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []

    def add_node(self, node: KnowledgeNode):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: KnowledgeEdge):
        self.edges.append(edge)
