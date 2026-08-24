"""Adaptive weighting model for information sources."""

from dataclasses import dataclass


@dataclass
class SourceWeight:
    source_id: str
    reliability: float = 0.5
    verification_accuracy: float = 0.5
    independence: float = 0.5

    def calculate_weight(self) -> float:
        score = (
            self.reliability * 0.4
            + self.verification_accuracy * 0.4
            + self.independence * 0.2
        )
        return max(0.0, min(1.0, score))


class AdaptiveSourceWeighting:
    def update(self, source: SourceWeight, verification_result: float) -> SourceWeight:
        source.verification_accuracy = (
            source.verification_accuracy * 0.8 + verification_result * 0.2
        )
        return source
