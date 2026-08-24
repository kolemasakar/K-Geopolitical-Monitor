"""Baseline probabilistic forecasting engine."""

from dataclasses import dataclass
from enum import Enum


class ScenarioType(str, Enum):
    BASELINE = "baseline"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ALTERNATIVE = "alternative"


@dataclass
class ForecastScenario:
    scenario: ScenarioType
    probability: float
    drivers: list[str]
    uncertainty_factors: list[str]


class ProbabilisticForecastEngine:
    def generate(self, scenarios: list[ForecastScenario]):
        total = sum(s.probability for s in scenarios)
        if total <= 0:
            return []
        return [
            {
                "scenario": s.scenario.value,
                "probability": s.probability / total,
                "drivers": s.drivers,
                "uncertainty_factors": s.uncertainty_factors,
            }
            for s in scenarios
        ]
