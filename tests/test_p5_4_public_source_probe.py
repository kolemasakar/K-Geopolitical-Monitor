import json
from datetime import datetime, timezone

import pytest

from kgeopolitical_monitor.on_demand_request_gate import authorize_public_probe, authorize_manual_request
from kgeopolitical_monitor.p5_public_source_probe import probe_public_once
from kgeopolitical_monitor.live_sources import HttpResponse

CTX = dict(repository="kolemasakar/K-Geopolitical-Monitor",
           actor="kolemasakar", ref="refs/heads/main",
           event_name="workflow_dispatch", mode="PUBLIC_SOURCE_READONLY",
           topic="Ukraine", request_id="p54-01")


class FakeThreeSourceTransport:
    def __init__(self):
        self.urls = []

    def get(self, url, *, headers=None):
        self.urls.append(url)
        if "gdacs.org" in url:
            return HttpResponse(body=b'<rss version="2.0"><channel></channel></rss>',
                                content_type="text/xml")
        if "consilium.europa.eu" in url:
            return HttpResponse(body=b'<rss version="2.0"><channel></channel></rss>',
                                content_type="text/xml")
        if "gdeltproject.org" in url:
            return HttpResponse(body=json.dumps({"articles":[]}).encode(),
                                content_type="application/json")
        raise AssertionError("unexpected endpoint")


def test_public_owner_authorization_separate_from_offline_gate():
    x = authorize_public_probe(**CTX)
    assert x.mode == "PUBLIC_SOURCE_READONLY"
    with pytest.raises(PermissionError):
        authorize_manual_request(**CTX)


@pytest.mark.parametrize("key,value", [
    ("actor","other"), ("repository","other/repo"),
    ("ref","refs/heads/feature"), ("event_name","push"),
    ("mode","LIVE_UNRESTRICTED")])
def test_reject_unapproved_public_execution(key,value):
    with pytest.raises(PermissionError):
        authorize_public_probe(**{**CTX,key:value})


def test_three_sources_probe_uses_only_ephemeral_db_and_never_claims_analysis():
    http = FakeThreeSourceTransport()
    result = probe_public_once(topic="Ukraine",transport=http)
    assert len(http.urls) == 3
    assert result["source_success_count"] == 3
    assert result["source_failure_count"] == 0
    assert result["item_count"] == 0
    assert result["collection_status"] == "COMPLETED"
    assert result["watch_persistence"] == "EPHEMERAL_ONLY"
    assert result["analysis"] == "NOT_EXECUTED"
    assert result["send"] == "NONE"
    assert all(x["status"] == "SUCCESS" for x in result["sources"])


def test_public_probe_failures_remain_explicit():
    class AllFail:
        def get(self,url,*,headers=None):
            raise RuntimeError("synthetic source denied")
    result = probe_public_once(topic="Ukraine",transport=AllFail())
    assert result["collection_status"] == "FAILED"
    assert result["source_failure_count"] == 3
    assert result["item_count"] == 0
    assert all(x["status"] == "FAILED" for x in result["sources"])


def test_workflow_never_automatically_calls_real_sources():
    from pathlib import Path
    workflow=(Path(__file__).resolve().parents[1]/".github/workflows/p5-4-owner-public-source-probe.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "PUBLIC_SOURCE_READONLY" in workflow
    assert "persist-credentials: false" in workflow
