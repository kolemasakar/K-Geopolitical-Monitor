from kgeopolitical_monitor.forecast_calibration import calibrate_probability


def test_probability_calibration_bounds():
    result = calibrate_probability(0.8, 1.1)
    assert 0 <= result.calibrated_probability <= 1
