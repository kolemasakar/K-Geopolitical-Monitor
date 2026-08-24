"""Forecast evaluation metrics baseline."""

from dataclasses import dataclass


@dataclass
class ForecastMetricResult:
    accuracy: float
    calibration_error: float
    confidence_drift: float


def calculate_brier_score(predicted: float, outcome: float) -> float:
    return (predicted - outcome) ** 2


def calculate_calibration_error(predicted: float, actual: float) -> float:
    return abs(predicted - actual)
