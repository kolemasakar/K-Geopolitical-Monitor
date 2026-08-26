from datetime import datetime

from kgeopolitical_monitor.domain import Event, RawItem, Source


def test_m0_object_flow():
    source = Source(source_id="src-1", name="test-source")
    raw = RawItem(
        item_id="raw-1",
        source_id=source.source_id,
        collected_at=datetime(2026, 8, 26, 0, 0, 0),
    )
    event = Event(event_id="event-1", title="test event")

    assert source.source_id == raw.source_id
    assert raw.item_id == "raw-1"
    assert event.event_id == "event-1"
    assert event.title == "test event"
