"""Knowledge graph persistence baseline layer."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class KnowledgeSnapshot:
    version: int
    nodes: Dict[str, dict] = field(default_factory=dict)
    edges: List[dict] = field(default_factory=list)


class KnowledgeRepository:
    def __init__(self):
        self.snapshots = []

    def save(self, snapshot: KnowledgeSnapshot):
        self.snapshots.append(snapshot)
        return snapshot.version

    def latest(self):
        return self.snapshots[-1] if self.snapshots else None
