"""Forecast probability calibration baseline."""

from dataclasses import dataclass


@dataclass
class CalibrationResult:
    calibrated_probability: float
    adjustment: float


def calibrate_probability(probability: float, historical_factor: float = 1.0) -> CalibrationResult:
    value = max(0.0, min(1.0, probability * historical_factor))
    return CalibrationResult(value, value - probability)
