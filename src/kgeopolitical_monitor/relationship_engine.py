"""Relationship analysis engine baseline."""

from dataclasses import dataclass


@dataclass
class RelationshipSignal:
    source: str
    target: str
    relation_type: str
    strength: float


class RelationshipEngine:
    def score(self, relation: RelationshipSignal) -> float:
        return max(0.0, min(1.0, relation.strength))
