from kgeopolitical_monitor.source_discovery import DiscoveredSource, SourceDiscovery


def test_source_discovery_returns_candidates():
    result = SourceDiscovery().discover([
        DiscoveredSource("example", "social", "global")
    ])
    assert len(result) == 1
