from src.kgeopolitical_monitor.pattern_learning import PatternLearner


def test_pattern_detection():
    patterns = PatternLearner().detect([])
    assert len(patterns) == 1
    assert patterns[0].confidence >= 0
