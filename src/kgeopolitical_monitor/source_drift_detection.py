"""Source drift detection baseline module.

Detects changes in source reliability patterns over time.
"""

from dataclasses import dataclass


@dataclass
class DriftSignal:
    source_id: str
    drift_score: float
    detected: bool


class SourceDriftDetector:
    def detect(self, historical_score: float, current_score: float) -> DriftSignal:
        drift = abs(current_score - historical_score)
        return DriftSignal(
            source_id="unknown",
            drift_score=drift,
            detected=drift > 0.2,
        )
