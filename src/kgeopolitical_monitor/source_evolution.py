"""Adaptive source evolution baseline."""

from dataclasses import dataclass


@dataclass
class SourceProfile:
    name: str
    reliability: float = 0.5
    relevance: float = 0.5
    active: bool = True


class SourceEvolutionEngine:
    def update_reliability(self, source: SourceProfile, evidence_score: float) -> SourceProfile:
        source.reliability = max(0.0, min(1.0, (source.reliability + evidence_score) / 2))
        return source
