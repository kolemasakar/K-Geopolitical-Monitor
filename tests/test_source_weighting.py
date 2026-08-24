from kgeopolitical_monitor.source_weighting import AdaptiveSourceWeighting, SourceWeight


def test_weight_calculation():
    source = SourceWeight("test", 0.8, 0.9, 0.7)
    assert 0 < source.calculate_weight() <= 1


def test_weight_update():
    source = SourceWeight("test", verification_accuracy=0.5)
    AdaptiveSourceWeighting().update(source, 1.0)
    assert source.verification_accuracy > 0.5
