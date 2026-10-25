import io
from email.message import Message

import pytest

from kgeopolitical_monitor.on_demand_source_policy import (
    RestrictedSourcePolicy, RestrictedSourceTransport, validate_source_url,
)


class SyntheticResponse:
    def __init__(self, payload=b"OK"):
        self.payload = payload
        self.headers = Message()
        self.headers["Content-Type"] = "application/octet-stream"
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, limit):
        return self.payload[:limit]


def test_exact_allowlist():
    for url in (
        "https://api.gdeltproject.org/api/v2/doc/doc?mode=artlist",
        "https://www.consilium.europa.eu/en/rss/pressreleases.ashx",
    ):
        validate_source_url(url)


@pytest.mark.parametrize("url", [
    "http://api.gdeltproject.org/api/v2/doc/doc",
    "https://api.gdeltproject.org.evil.test/api/v2/doc/doc",
    "https://api.gdeltproject.org:444/api/v2/doc/doc",
    "https://user:pass@api.gdeltproject.org/api/v2/doc/doc",
    "https://api.gdeltproject.org/admin",
    "https://127.0.0.1/api/v2/doc/doc",
    "file:///etc/passwd",
    "https://www.consilium.europa.eu/en/rss/pressreleases.ashx#frag",
 ])
def test_unapproved_hosts_paths_schemes_rejected(url):
    with pytest.raises(ValueError):
        validate_source_url(url)


def test_one_shot_budget_and_size(monkeypatch):
    transport = RestrictedSourceTransport(RestrictedSourcePolicy(max_requests=1, max_bytes_per_response=4))
    calls = []
    def fake_open(req, timeout):
        calls.append(req.full_url)
        return SyntheticResponse(b"DATA")
    monkeypatch.setattr(transport._opener, "open", fake_open)
    url = "https://api.gdeltproject.org/api/v2/doc/doc?q=x"
    assert transport.get(url).body == b"DATA"
    with pytest.raises(RuntimeError, match="budget"):
        transport.get(url)
    assert len(calls) == 1


def test_fail_closed_oversize_and_no_auth(monkeypatch):
    transport = RestrictedSourceTransport(RestrictedSourcePolicy(max_requests=2, max_bytes_per_response=4))
    monkeypatch.setattr(transport._opener, "open", lambda req,timeout: SyntheticResponse(b"123456"))
    url = "https://www.consilium.europa.eu/en/rss/pressreleases.ashx"
    with pytest.raises(ValueError, match="credential"):
        transport.get(url,headers={"Cookie":"sensitive"})
    assert transport.calls == 0
    with pytest.raises(RuntimeError, match="exceeds"):
        transport.get(url)
    assert transport.calls == 1


def test_redirect_handler_refuses():
    transport = RestrictedSourceTransport(RestrictedSourcePolicy())
    handler = next(h for h in transport._opener.handlers
                   if h.__class__.__name__ == "_NoRedirect")
    with pytest.raises(RuntimeError, match="redirect"):
        handler.redirect_request(None,None,302,"found",{},"https://bad.test/")
