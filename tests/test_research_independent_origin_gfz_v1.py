from kgeopolitical_monitor.research_source_gfz_v1 import build_query, fetch
from kgeopolitical_monitor.research_event_association_v1 import associate_earthquakes
from kgeopolitical_monitor.research_origin_assessment_v1 import assess_origin_groups
from test_research_request_v1 import sample

def current():
    r=sample(); r["mode"]="CURRENT"; r.pop("as_of_utc"); return r

def test_gfz_query_is_https_and_bounded():
    u=build_query(current(),min_magnitude=4.5)
    assert u.startswith("https://geofon.gfz-potsdam.de/")
    assert "minmagnitude=4.5" in u and "limit=20" in u

def test_gfz_fixture_normalizes_structured_origin():
    text="#EventID|Time|Latitude|Longitude|Depth/km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|MagAuthor|EventLocationName|EventType\n"
    text+="gfz2026x|2026-09-02T11:00:05.00|10.02|20.03|12.0|||GFZ|gfz2026x|mb|5.1||Test Region|earthquake\n"
    items=fetch(current(),observed_at_utc="2026-09-28T12:02:00Z",http_get=lambda _:text)
    item=items[0]
    assert item["source_id"]=="gfz-geofon"
    assert item["origin_group"]=="gfz-geofon"
    assert item["event_parameters"]["kind"]=="EARTHQUAKE"
    assert item["claim_signature"]=="mag-51"

def test_conservative_association_accepts_close_independent_origins():
    a={"event_parameters":{"kind":"EARTHQUAKE","origin_utc":"2026-09-02T11:00:00Z",
       "latitude":10.0,"longitude":20.0,"magnitude":5.0},"origin_group":"usgs-neic"}
    b={"event_parameters":{"kind":"EARTHQUAKE","origin_utc":"2026-09-02T11:00:05Z",
       "latitude":10.02,"longitude":20.03,"magnitude":5.1},"origin_group":"gfz-geofon"}
    match=associate_earthquakes(a,b,max_seconds=30,max_km=50)
    assert match["match"] is True
    origin=assess_origin_groups([a,b])
    assert origin["assessment"]=="DISTINCT_ORIGIN"
    assert origin["independent_origin_credit"] is True

def test_conservative_association_rejects_distant_event():
    a={"event_parameters":{"kind":"EARTHQUAKE","origin_utc":"2026-09-02T11:00:00Z",
       "latitude":10.0,"longitude":20.0,"magnitude":5.0}}
    b={"event_parameters":{"kind":"EARTHQUAKE","origin_utc":"2026-09-02T11:00:10Z",
       "latitude":12.0,"longitude":20.0,"magnitude":5.0}}
    assert associate_earthquakes(a,b,max_seconds=30,max_km=50)["match"] is False
