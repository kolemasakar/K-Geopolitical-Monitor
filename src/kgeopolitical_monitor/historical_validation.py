"""Historical validation baseline for forecast evaluation."""

from dataclasses import dataclass


@dataclass
class ForecastOutcome:
    forecast_id: str
    predicted_probability: float
    observed: bool


class HistoricalValidator:
    def evaluate(self, outcomes: list[ForecastOutcome]) -> dict:
        if not outcomes:
            return {"accuracy": 0.0, "count": 0}

        correct = sum(
            (o.predicted_probability >= 0.5) == o.observed
            for o in outcomes
        )
        return {
            "accuracy": correct / len(outcomes),
            "count": len(outcomes),
        }
