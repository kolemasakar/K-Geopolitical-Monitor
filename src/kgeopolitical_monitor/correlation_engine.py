"""Event correlation scoring baseline.

Combines temporal, entity and thematic relationships between verified events.
"""

from dataclasses import dataclass


@dataclass
class CorrelationScore:
    temporal: float
    entity: float
    thematic: float

    @property
    def total(self) -> float:
        return (self.temporal + self.entity + self.thematic) / 3


def calculate_correlation(temporal: float, entity: float, thematic: float) -> CorrelationScore:
    return CorrelationScore(temporal, entity, thematic)
