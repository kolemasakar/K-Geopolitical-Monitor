from datetime import datetime, timezone
from types import SimpleNamespace
import socket
import ssl
from urllib.error import URLError
import pytest

from kgeopolitical_monitor.on_demand_source_policy import (
    RestrictedSourcePolicy, RestrictedSourceTransport,
)
from kgeopolitical_monitor.p5_probe_diagnostics import classify_attempt
from kgeopolitical_monitor.p5_public_source_probe import _ConsiliumMetadataTransport


class FakeResponse:
    def __init__(self, size):
        self.size = size
        self.headers = {"Content-Type": "application/xml"}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, limit):
        return b"x" * min(self.size, limit)


def test_only_gdacs_gets_dedicated_raised_cap(monkeypatch):
    transport = RestrictedSourceTransport(RestrictedSourcePolicy(
        max_requests=3, max_bytes_per_response=512_000,
        gdacs_max_bytes_per_response=1_500_000))
    monkeypatch.setattr(transport._opener, "open", lambda req, timeout: FakeResponse(600_000))
    gdacs = transport.get("https://www.gdacs.org/xml/rss.xml")
    assert len(gdacs.body) == 600_000
    with pytest.raises(RuntimeError, match="exceeds configured bound"):
        transport.get("https://www.consilium.europa.eu/en/rss/pressreleases.ashx")
    assert transport.calls == 2


def test_dedicated_cap_never_unbounded():
    with pytest.raises(ValueError):
        RestrictedSourcePolicy(gdacs_max_bytes_per_response=2_000_001)
    with pytest.raises(ValueError):
        RestrictedSourcePolicy(gdacs_max_bytes_per_response=512)


@pytest.mark.parametrize("reason,expected", [
    (socket.gaierror("dns failure private"), "NETWORK_DNS_FAILURE"),
    (socket.timeout("timed out private"), "NETWORK_TIMEOUT"),
    (ssl.SSLError("tls private"), "NETWORK_TLS_FAILURE"),
    (ConnectionRefusedError("connect private"), "NETWORK_CONNECT_FAILURE"),
])
def test_safe_network_error_categories(monkeypatch, reason, expected):
    transport = RestrictedSourceTransport(RestrictedSourcePolicy())
    def fail(req, timeout):
        raise URLError(reason)
    monkeypatch.setattr(transport._opener, "open", fail)
    with pytest.raises(RuntimeError) as info:
        transport.get("https://www.gdacs.org/xml/rss.xml")
    assert "private" not in str(info.value)
    result = classify_attempt(status="FAILED", item_count=0, error=str(info.value))
    assert result["diagnostic"] == expected
    assert "private" not in repr(result)


def test_consilium_feed_metadata_counts_before_and_after_filter():
    class Stub:
        def get(self, url, *, headers=None):
            return SimpleNamespace(
                body=(b'<rss><channel>'
                      b'<item><title>Ukraine joint statement</title><description>Official</description></item>'
                      b'<item><title>Energy meeting</title><description>Other</description></item>'
                      b'</channel></rss>'),
                content_type="text/xml")
    t = _ConsiliumMetadataTransport(Stub(), "Ukraine")
    t.get("https://www.consilium.europa.eu/en/rss/pressreleases.ashx")
    assert t.total_entries == 2
    assert t.matching_entries == 1


def test_consilium_non_xml_has_unknown_counts():
    class Stub:
        def get(self, url, *, headers=None):
            return SimpleNamespace(body=b"broken", content_type="text/xml")
    t = _ConsiliumMetadataTransport(Stub(), "Ukraine")
    t.get("https://www.consilium.europa.eu/en/rss/pressreleases.ashx")
    assert t.total_entries is None
