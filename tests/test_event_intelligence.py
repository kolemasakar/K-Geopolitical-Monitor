from kgeopolitical_monitor.event_intelligence import Event, Relationship


def test_event_creation():
    event = Event('1', 'Test event', 0.8)
    assert event.confidence == 0.8


def test_relationship_creation():
    rel = Relationship('A', 'B', 'related')
    assert rel.relation_type == 'related'
