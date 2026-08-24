from kgeopolitical_monitor.correlation_engine import calculate_correlation


def test_correlation_score():
    score = calculate_correlation(0.8, 0.7, 0.9)
    assert round(score.total, 2) == 0.8
