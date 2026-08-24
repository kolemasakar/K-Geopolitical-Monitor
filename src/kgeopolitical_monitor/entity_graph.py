"""Entity graph baseline for M2 Event Intelligence Core."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Entity:
    id: str
    name: str
    entity_type: str


@dataclass
class EntityRelation:
    source_id: str
    target_id: str
    relation_type: str
    confidence: float = 0.5


@dataclass
class EntityGraph:
    entities: Dict[str, Entity] = field(default_factory=dict)
    relations: List[EntityRelation] = field(default_factory=list)

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def add_relation(self, relation: EntityRelation):
        self.relations.append(relation)
