from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.p22_3_b1_source_pack import (
    B1_REPOSITORY_ACTIVE_SOURCE_IDS,
    P23_1_B1_REMEDIATION_VERSION,
    P23_1_UKSL_RANGE_BYTES,
    UkSanctionsCsvAdapter,
    b1_by_id,
)

NOW = datetime(2026, 9, 20, 4, 30, tzinfo=timezone.utc)
FIX = Path(__file__).parent / "fixtures" / "p22_3_b1"


class CaptureTransport:
    def __init__(self, body: bytes):
        self.body = body
        self.calls = []

    def get(self, url, *, headers=None):
        self.calls.append((url, dict(headers or {})))
        return HttpResponse(body=self.body, content_type="application/octet-stream")


def test_uksl_remediation_uses_bounded_initial_range_and_skips_report_date_preamble():
    fixture = (FIX / "uk-sanctions.csv").read_bytes()
    body = b"Report Date: 20-Sep-2026\n" + fixture
    transport = CaptureTransport(body)
    spec = b1_by_id()["uk-sanctions-list-en"]
    adapter = UkSanctionsCsvAdapter(transport, spec, max_entries=2)

    items = adapter.fetch(type("Watch", (), {"query": "unused"})(), NOW)

    assert len(items) == 2
    assert transport.calls[0][1]["Range"] == f"bytes=0-{P23_1_UKSL_RANGE_BYTES - 1}"
    assert P23_1_UKSL_RANGE_BYTES == 1_500_000
    assert transport.calls[0][1]["User-Agent"].endswith(P23_1_B1_REMEDIATION_VERSION)
    assert all(item.metadata["acquisition_mode"] == "INITIAL_BYTE_RANGE" for item in items)
    assert all(item.metadata["range_bytes"] == P23_1_UKSL_RANGE_BYTES for item in items)
    assert all(item.metadata["unique_id"] for item in items)


def test_uksl_remediation_missing_canonical_header_fails_closed():
    transport = CaptureTransport(b"Report Date: 20-Sep-2026\nnot,a,uksl,header\n")
    spec = b1_by_id()["uk-sanctions-list-en"]
    adapter = UkSanctionsCsvAdapter(transport, spec, max_entries=2)

    with pytest.raises(ValueError, match="canonical CSV header not found"):
        adapter.fetch(type("Watch", (), {"query": "unused"})(), NOW)


def test_p23_1_readiness_does_not_activate_blocked_sources_or_allow_http_fallback():
    by_id = b1_by_id()
    assert "uk-sanctions-list-en" not in B1_REPOSITORY_ACTIVE_SOURCE_IDS
    assert "russian-government-news-ru" not in B1_REPOSITORY_ACTIVE_SOURCE_IDS
    assert by_id["russian-government-news-ru"].endpoint == "https://government.ru/news/"
    assert by_id["russian-government-news-ru"].outbound_domain == "government.ru"
