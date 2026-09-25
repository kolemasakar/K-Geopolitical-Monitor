"""P23.4 UKSL bounded pilot regression: no CSV-row inflation."""
import csv
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.p22_3_b1_source_pack import (
    B1_REPOSITORY_ACTIVE_SOURCE_IDS,
    UkSanctionsCsvAdapter,
    b1_by_id,
    build_b1_adapters,
)

NOW = datetime(2026, 9, 25, tzinfo=timezone.utc)
HEADER = b"Unique ID,Name 6,Regime Name\n"


class CapturedTransport:
    def __init__(self, body: bytes):
        self.body = body
        self.calls = []

    def get(self, url, *, headers=None):
        self.calls.append((url, dict(headers or {})))
        return HttpResponse(body=self.body, content_type="text/csv")


def _fetch(body: bytes, *, max_entries: int = 100):
    transport = CapturedTransport(body)
    adapter = UkSanctionsCsvAdapter(
        transport, b1_by_id()["uk-sanctions-list-en"], max_entries=max_entries
    )
    items = adapter.fetch(SimpleNamespace(query="unused"), NOW)
    return transport, items


def test_csv_alias_rows_do_not_inflate_distinct_designations():
    body = (HEADER + b"A001,First Alias,Regime\n"
            + b"A001,Second Alias,Regime\n"
            + b"A001,First Alias,Regime\n"
            + b"A002,Another Entry,Regime\n")
    transport, items = _fetch(body)
    assert len(items) == 2
    assert {i.metadata["unique_id"] for i in items} == {"A001", "A002"}
    assert len({i.item_id for i in items}) == 2
    assert transport.calls[0][1]["Range"] == "bytes=0-1499999"


def test_bounded_range_ignores_unterminated_tail():
    body = (HEADER + b"A001,Complete Entry,Regime\n"
            + b"A002,Next Complete Entry,Regime\n"
            + b"A003,Incomplete Entry")
    _, items = _fetch(body)
    assert len(items) == 2
    assert {i.metadata["unique_id"] for i in items} == {"A001", "A002"}


def test_bounded_csv_strict_parse_fails_closed_on_unclosed_quoted_record():
    body = (HEADER + b"A001,Complete Entry,Regime\n"
            + b'A002,"Unclosed quoted name\n')
    with pytest.raises(csv.Error):
        _fetch(body)


def test_empty_selection_remains_rollback_and_no_source_activation():
    assert "uk-sanctions-list-en" not in B1_REPOSITORY_ACTIVE_SOURCE_IDS
    assert build_b1_adapters(CapturedTransport(b""), enabled_source_ids=[]) == []
