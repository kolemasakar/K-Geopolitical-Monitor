from kgeopolitical_monitor.domain import Event


def test_event_import_available():
    assert Event is not None
