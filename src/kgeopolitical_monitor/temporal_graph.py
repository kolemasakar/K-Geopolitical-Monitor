from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class TemporalRelation:
    source: str
    target: str
    relation: str
    timestamp: datetime
    weight: float = 1.0


class TemporalGraphAnalyzer:
    def __init__(self):
        self.relations: List[TemporalRelation] = []

    def add_relation(self, relation: TemporalRelation):
        self.relations.append(relation)

    def history(self, entity: str) -> List[TemporalRelation]:
        return [r for r in self.relations if r.source == entity or r.target == entity]

    def influence_change(self, entity: str) -> float:
        values = [r.weight for r in self.history(entity)]
        if len(values) < 2:
            return 0.0
        return values[-1] - values[0]
