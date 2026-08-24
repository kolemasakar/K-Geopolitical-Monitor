from kgeopolitical_monitor.source_lifecycle import SourceLifecycleManager, SourceState


def test_source_lifecycle():
    manager = SourceLifecycleManager()
    assert manager.transition(SourceState.DISCOVERED, "activate") == SourceState.ACTIVE
    assert manager.transition(SourceState.ACTIVE, "degrade") == SourceState.DEGRADED
