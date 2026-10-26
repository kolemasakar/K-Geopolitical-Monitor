import json
from types import SimpleNamespace
import pytest

from kgeopolitical_monitor.p5_owner_source_probe import probe_sources


RSS = b'<rss version="2.0"><channel><item><title>Example</title></item></channel></rss>'
GDELT = b'{"articles":[{"title":"Sample"}]}'


class FakeTransport:
    def __init__(self, fail=None):
        self.urls = []
        self.fail = fail
    def get(self, url, *, headers=None):
        self.urls.append(url)
        if self.fail is not None and self.fail in url:
            raise RuntimeError("synthetic source refused")
        return SimpleNamespace(body=GDELT if "gdeltproject" in url else RSS)


def test_public_probe_three_fixed_hosts_and_parse_only():
    transport = FakeTransport()
    report = probe_sources(transport=transport, term="earthquake")
    assert report["success_count"] == 3
    assert report["failure_count"] == 0
    assert len(transport.urls) == 3
    assert transport.urls[0] == "https://www.gdacs.org/xml/rss.xml"
    assert transport.urls[1] == "https://www.consilium.europa.eu/en/rss/pressreleases.ashx"
    assert "mode=artlist" in transport.urls[2]
    assert all(x["item_count"] == 1 for x in report["source_results"])
    assert not report["raw_data_persisted"]
    assert not report["provenance_validated"]
    assert not report["report_sent"]


def test_public_probe_partial_failure_is_reported_without_claiming_pass():
    transport = FakeTransport("gdeltproject")
    report = probe_sources(transport=transport)
    assert report["success_count"] == 2
    assert report["failure_count"] == 1
    assert report["source_results"][2]["error_class"] == "RuntimeError"


def test_public_probe_invalid_xml_fails_as_structured_source_failure():
    class InvalidXML(FakeTransport):
        def get(self, url, *, headers=None):
            resp = super().get(url, headers=headers)
            if "gdacs.org" in url:
                return SimpleNamespace(body=b"bad")
            return resp
    report = probe_sources(transport=InvalidXML())
    assert report["source_results"][0]["result"] == "FAILED"
    assert report["source_results"][1]["result"] == "PARSE_OK"


@pytest.mark.parametrize("term", ["", "x"*81, "x\nbad"])
def test_public_probe_rejects_invalid_term_without_request(term):
    transport = FakeTransport()
    with pytest.raises(ValueError):
        probe_sources(transport=transport, term=term)
    assert transport.urls == []


def test_owner_workflow_requires_manual_explicit_confirmation():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1] /
          ".github/workflows/p5-4-owner-public-source-probe.yml").read_text()
    assert "workflow_dispatch:" in text
    assert "authorize_public_fetch" in text
    assert "inputs.authorize_public_fetch == 'YES'" in text
    assert "github.actor == 'kolemasakar'" in text
    assert "pull_request:" not in text
    assert "push:" not in text
