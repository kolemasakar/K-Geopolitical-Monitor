"""Synthetic AU article fixtures. No claims about independently verified events."""
import pytest
from kgeopolitical_monitor.research_source_african_union_v1 import fetch
from test_research_request_v1 import sample

URL="https://au.int/en/pressreleases/20261011/auc-chairperson-statement-tragic-loss-migrant-lives-coast-djibouti"
TITLE="Statement of the Chairperson of the AU Commission on the Tragic Loss of Migrant Lives off the Coast of Djibouti"
HTML=("<html><head><title>AU</title></head><body><h1>"+TITLE+"</h1>"
      "<div class='date'>Oct 11, 2026</div><div class='field'>"
      "<p>The AU Commission Chairperson issued an official statement.</p>"
      "</div></body></html>")

def current():
    r=sample()
    r["mode"]="CURRENT"
    r.pop("as_of_utc")
    r["period_start_utc"]="2026-10-10T00:00:00Z"
    r["period_end_utc"]="2026-10-13T23:59:59Z"
    return r

def test_official_article_day_anchor_and_origin():
    x=fetch(current(),observed_at_utc="2026-10-13T12:00:00Z",
            http_get=lambda _: HTML,public_url=URL)[0]
    assert x["status"]=="SUCCESS"
    assert x["source_id"]=="african-union-press"
    assert x["origin_group"]=="african-union"
    assert x["published_at_utc"]=="2026-10-11T00:00:00Z"
    assert x["available_at_utc"]=="2026-10-13T12:00:00Z"
    assert TITLE in x["summary"]
    assert "verification" not in x
    assert "event_identity" not in x

@pytest.mark.parametrize("bad_url",[
    "https://unofficial.example/en/pressreleases/20261011/example",
    "http://au.int/en/pressreleases/20261011/example",
    "https://au.int.evil.example/en/pressreleases/20261011/example",
    "https://au.int:8443/en/pressreleases/20261011/example",
    "https://attacker@au.int/en/pressreleases/20261011/example",
    URL+"#fragment",
])
def test_external_or_malformed_provenance_denied(bad_url):
    with pytest.raises(ValueError):
        fetch(current(),observed_at_utc="2026-10-13T12:00:00Z",
              http_get=lambda _: HTML,public_url=bad_url)

@pytest.mark.parametrize("bad_html",[
    "<html><body>No article heading. Oct 11, 2026</body></html>",
    "<html><body><h1>"+TITLE+"</h1>Oct 12, 2026</body></html>",
    "<html><body><h1>Short</h1>Oct 11, 2026</body></html>",
])
def test_missing_title_or_disagreeing_day_fails_closed(bad_html):
    with pytest.raises(ValueError):
        fetch(current(),observed_at_utc="2026-10-13T12:00:00Z",
              http_get=lambda _: bad_html,public_url=URL)

def test_transport_timeout_explicit_unavailable_not_zero_events():
    x=fetch(current(),observed_at_utc="2026-10-13T12:00:00Z",
            http_get=lambda _: (_ for _ in ()).throw(TimeoutError()),
            public_url=URL)[0]
    assert x["status"]=="UNAVAILABLE"
    assert x["error_code"]=="TRANSPORT_UNAVAILABLE"
    assert x["published_at_utc"] is None

def test_historical_backdating_denied():
    r=current();r["mode"]="HISTORICAL_AS_OF"
    r["as_of_utc"]="2026-10-11T23:00:00Z"
    r["requested_at_utc"]="2026-10-13T12:00:00Z"
    r["period_end_utc"]="2026-10-11T23:00:00Z"
    x=fetch(r,observed_at_utc="2026-10-13T12:00:00Z",
            http_get=lambda _: HTML,public_url=URL)[0]
    assert x["status"]=="INVALID"
    assert x["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"

def test_excessive_body_rejected():
    with pytest.raises(ValueError,match="exceeds bound"):
        fetch(current(),observed_at_utc="2026-10-13T12:00:00Z",
              http_get=lambda _: HTML+"z"*2_100_000,public_url=URL)
