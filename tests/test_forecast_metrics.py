import pytest

from kgeopolitical_monitor.forecast_metrics import calculate_brier_score, calculate_calibration_error


def test_brier_score():
    assert calculate_brier_score(0.8, 1.0) == pytest.approx(0.04)


def test_calibration_error():
    assert calculate_calibration_error(0.7, 0.5) == pytest.approx(0.2)
