"""Baseline pattern learning module.

Detects reusable relationships between events, sources and outcomes.
"""

from dataclasses import dataclass
from enum import Enum


class PatternType(str, Enum):
    EVENT_REACTION = "event_reaction"
    SOURCE_ACCURACY = "source_accuracy"
    FACTOR_OUTCOME = "factor_outcome"
    ENTITY_INTERACTION = "entity_interaction"


@dataclass
class Pattern:
    pattern_type: PatternType
    description: str
    confidence: float


class PatternLearner:
    def detect(self, observations):
        return [
            Pattern(
                pattern_type=PatternType.EVENT_REACTION,
                description="baseline event sequence pattern",
                confidence=0.5,
            )
        ]
