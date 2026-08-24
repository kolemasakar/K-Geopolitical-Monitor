"""Forecast preparation layer baseline.

Builds structured inputs from verified events for probabilistic forecasting.
"""

from dataclasses import dataclass
from enum import Enum


class ForecastHorizon(str, Enum):
    SHORT = "short_term"
    MEDIUM = "medium_term"
    LONG = "long_term"
    GLOBAL = "global_evolutionary"


@dataclass
class ForecastSignal:
    event_id: str
    momentum: float
    influence: float
    confidence: float
    horizon: ForecastHorizon


class ForecastPreparation:
    def prepare(self, event_id, momentum, influence, confidence, horizon):
        return ForecastSignal(
            event_id=event_id,
            momentum=momentum,
            influence=influence,
            confidence=confidence,
            horizon=horizon,
        )
