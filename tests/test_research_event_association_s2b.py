"""S2b bounded offline association acceptance: no factual verification or network."""
from kgeopolitical_monitor.research_event_association_v1 import associate_earthquakes

def observation(t, lat=54.4775, lon=162.5648, kind="EARTHQUAKE"):
    return {"event_parameters": {"kind":kind,"origin_utc":t,"latitude":lat,"longitude":lon}}

def test_same_event_matches_within_tolerance():
    a=observation("2026-10-07T18:15:04Z")
    b=observation("2026-10-07T18:15:06Z",54.58,162.231)
    x=associate_earthquakes(a,b,max_seconds=30,max_km=50)
    assert x["match"] is True
    assert x["reason"]=="MATCH"

def test_temporal_disagreement_fails_closed():
    x=associate_earthquakes(observation("2026-10-07T18:15:04Z"),observation("2026-10-07T18:17:04Z"))
    assert x["match"] is False and x["reason"]=="OUTSIDE_TOLERANCE"

def test_geographical_disagreement_fails_closed():
    x=associate_earthquakes(observation("2026-10-07T18:15:04Z"),observation("2026-10-07T18:15:05Z",0.0,0.0))
    assert x["match"] is False and x["reason"]=="OUTSIDE_TOLERANCE"

def test_missing_parameters_is_not_a_match():
    assert associate_earthquakes({},observation("2026-10-07T18:15:04Z"))=={"match":False,"reason":"MISSING_PARAMETERS"}

def test_unsupported_kind_is_not_a_match():
    assert associate_earthquakes(observation("2026-10-07T18:15:04Z",kind="DIPLOMATIC"),observation("2026-10-07T18:15:04Z"))=={"match":False,"reason":"UNSUPPORTED_KIND"}
