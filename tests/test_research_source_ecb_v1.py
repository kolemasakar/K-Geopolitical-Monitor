from kgeopolitical_monitor.research_source_ecb_v1 import fetch, FEED_URL
from test_research_request_v1 import sample

RSS=b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
<item><title>ECB monetary policy decision</title>
<link>https://www.ecb.europa.eu/press/pr/date/2026/html/test.en.html</link>
<pubDate>Wed, 02 Sep 2026 12:00:00 +0200</pubDate></item>
</channel></rss>"""

def current():
    r=sample(); r["mode"]="CURRENT"; r.pop("as_of_utc")
    r["period_start_utc"]="2026-09-01T00:00:00Z"
    r["period_end_utc"]="2026-09-03T00:00:00Z"
    return r

def test_ecb_fixture_normalizes_official_rss():
    items=fetch(current(),observed_at_utc="2026-09-02T12:30:00Z",
                http_get=lambda _:RSS)
    assert len(items)==1
    x=items[0]
    assert x["source_id"]=="ecb-press"
    assert x["origin_group"]=="ecb"
    assert x["published_at_utc"]=="2026-09-02T10:00:00Z"
    assert x["public_url"].startswith("https://www.ecb.europa.eu/")

def test_ecb_query_filter_is_bounded_and_deterministic():
    assert fetch(current(),observed_at_utc="2026-09-02T12:30:00Z",
                 http_get=lambda _:RSS,query="monetary policy")
    assert fetch(current(),observed_at_utc="2026-09-02T12:30:00Z",
                 http_get=lambda _:RSS,query="earthquake")==[]

def test_ecb_transport_failure_is_explicit():
    items=fetch(current(),observed_at_utc="2026-09-02T12:30:00Z",
                http_get=lambda _:(_ for _ in ()).throw(TimeoutError()))
    assert items[0]["status"]=="UNAVAILABLE"
    assert items[0]["error_code"]=="TRANSPORT_UNAVAILABLE"

def test_ecb_historical_live_retrieval_cannot_backdate():
    req=sample()
    req["period_start_utc"]="2026-09-01T00:00:00Z"
    req["period_end_utc"]="2026-09-02T11:00:00Z"
    req["as_of_utc"]="2026-09-02T11:00:00Z"
    items=fetch(req,observed_at_utc="2026-09-02T12:30:00Z",http_get=lambda _:RSS)
    assert items[0]["status"]=="INVALID"
    assert items[0]["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"

def test_feed_url_is_official_https():
    assert FEED_URL=="https://www.ecb.europa.eu/rss/press.html"
