from kgeopolitical_monitor.research_source_nato_v1 import fetch, build_query, SEARCH_ENDPOINT
from test_research_request_v1 import sample

PAYLOAD={"pages":[
 {"title":"NATO exercise","description":"NATO begins a deterrence exercise.",
  "pageDate":"02 September 2026","link":"/en/news-and-events/articles/news/2026/09/02/test"}
]}

def current():
    r=sample(); r["mode"]="CURRENT"; r.pop("as_of_utc")
    r["period_start_utc"]="2026-09-01T00:00:00Z"
    r["period_end_utc"]="2026-09-03T00:00:00Z"
    return r

def test_nato_query_is_official_and_bounded():
    u=build_query(current(),theme="deterrence-and-defence")
    assert u.startswith(SEARCH_ENDPOINT+"?")
    assert "pageSize=20" in u
    assert "nato%3Atheme%2Fdeterrence-and-defence" in u

def test_nato_fixture_normalizes():
    items=fetch(current(),observed_at_utc="2026-09-02T12:30:00Z",
                http_get=lambda _:PAYLOAD)
    assert len(items)==1
    x=items[0]
    assert x["source_id"]=="nato-news"
    assert x["origin_group"]=="nato"
    assert x["public_url"].startswith("https://www.nato.int/")
    assert x["published_at_utc"]=="2026-09-02T12:30:00Z"

def test_nato_transport_failure_explicit():
    items=fetch(current(),observed_at_utc="2026-09-02T12:30:00Z",
                http_get=lambda _:(_ for _ in ()).throw(TimeoutError()))
    assert items[0]["status"]=="UNAVAILABLE"
    assert items[0]["error_code"]=="TRANSPORT_UNAVAILABLE"

def test_nato_theme_is_allowlisted():
    import pytest
    with pytest.raises(ValueError,match="theme"):
        build_query(current(),theme="arbitrary")

def test_nato_historical_live_retrieval_cannot_backdate():
    req=sample()
    req["period_start_utc"]="2026-09-01T00:00:00Z"
    req["period_end_utc"]="2026-09-02T23:00:00Z"
    req["as_of_utc"]="2026-09-02T23:00:00Z"
    items=fetch(req,observed_at_utc="2026-09-03T00:00:00Z",http_get=lambda _:PAYLOAD)
    assert items[0]["status"]=="INVALID"
    assert items[0]["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"
