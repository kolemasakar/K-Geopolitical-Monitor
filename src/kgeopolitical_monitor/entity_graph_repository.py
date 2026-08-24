"""Entity graph persistence baseline."""

from dataclasses import dataclass


@dataclass
class EntityRelation:
    source_entity: str
    target_entity: str
    relation_type: str
    confidence: float = 0.0


class EntityGraphRepository:
    def __init__(self):
        self.relations = []

    def add_relation(self, relation: EntityRelation):
        self.relations.append(relation)

    def list_relations(self):
        return self.relations
