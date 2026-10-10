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


def test_nato_generic_mapping_profile_attaches_on_strict_match():
    req=current()
    req["period_start_utc"]="2026-10-08T00:00:00Z"
    req["period_end_utc"]="2026-10-10T23:59:59Z"
    payload={"pages":[{"title":"NATO’s Deputy Secretary General visits Moldova",
        "description":"Radmila Shekerinska met Deputy Prime Minister and Minister of Foreign Affairs Mihai Popșoi in Chisinau.",
        "pageDate":"09 October 2026",
        "link":"/en/news-and-events/articles/news/2026/10/09/natos-deputy-secretary-general-visits-moldova"}]}
    event={"family":"DIPLOMATIC","event_date_utc":"2026-10-08T00:00:00Z",
           "action_key":"MEET","actor_keys":["moldova-dpm-mfa-mihai-popsoi","nato-dsg-radmila-shekerinska"],
           "target_keys":[],"subject_key":"nato-moldova-bilateral-meeting","location_key":"chisinau-moldova"}
    claim={"claim_type":"STATUS","value_keys":["meeting-held"],"unit_key":None}
    profile={"source_id":"nato-news","required_phrases":["radmila shekerinska","mihai popșoi"],
             "event_descriptor":event,"claim_descriptor":claim}
    items=fetch(req,observed_at_utc="2026-10-09T12:00:00Z",
                http_get=lambda _:payload,theme=None,search_text="Moldova",
                mapping_profile=profile)
    assert len(items)==1
    assert items[0]["event_descriptor"]==event
    assert items[0]["claim_descriptor"]==claim

def test_nato_none_theme_means_no_tag_filter():
    u=build_query(current(),theme=None,search_text="Moldova")
    assert "selectedTagsFilter=" in u
