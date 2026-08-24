from kgeopolitical_monitor.confidence_engine import ConfidenceEngine


def test_confidence_engine_limits_score():
    engine = ConfidenceEngine()
    score = engine.calculate(5, 1.0, 1.0, 0.0)
    assert 0.0 <= score <= 1.0


def test_contradiction_reduces_score():
    engine = ConfidenceEngine()
    assert engine.calculate(3, 0.8, 0.8, 0.5) < engine.calculate(3, 0.8, 0.8, 0.0)
