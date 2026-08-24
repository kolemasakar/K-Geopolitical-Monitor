from kgeopolitical_monitor.domain import Source, RawItem, Event


def test_m0_object_flow():
    source = Source(id="src-1", name="test-source")
    raw = RawItem(id="raw-1", source_id=source.id, content="test item")
    event = Event(id="event-1", title="test event")

    assert source.id == raw.source_id
    assert event.title == "test event"
