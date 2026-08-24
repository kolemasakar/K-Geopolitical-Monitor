from kgeopolitical_monitor.source_evolution import SourceEvolutionEngine, SourceProfile


def test_source_reliability_update():
    source = SourceProfile(name="test", reliability=0.4)
    result = SourceEvolutionEngine().update_reliability(source, 0.8)
    assert result.reliability == 0.6
