from kgeopolitical_monitor.source_drift_detection import SourceDriftDetector


def test_detect_drift():
    result = SourceDriftDetector().detect(0.9, 0.5)
    assert result.detected is True
    assert result.drift_score == 0.4
