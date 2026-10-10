import pytest
from kgeopolitical_monitor.research_source_cooldown_v1 import record_cooldown,check_cooldown
from kgeopolitical_monitor.research_source_gdacs_v1 import build_query,fetch
from kgeopolitical_monitor.research_source_adapter_v1 import normalize_observations
from test_research_request_v1 import sample

def current():
 r=sample();r["mode"]="CURRENT";r.pop("as_of_utc");return r

def test_cooldown_blocks_until_expiry(tmp_path):
 tmp_path.mkdir(exist_ok=True)
 record_cooldown(tmp_path,"gdelt-doc-v2",until_utc="2026-09-28T13:00:00Z",reason="RATE_LIMITED")
 assert check_cooldown(tmp_path,"gdelt-doc-v2",observed_at_utc="2026-09-28T12:30:00Z")
 assert check_cooldown(tmp_path,"gdelt-doc-v2",observed_at_utc="2026-09-28T13:00:00Z") is None

def test_gdacs_query_is_https_and_bounded_window():
 u=build_query(current())
 assert u.startswith("https://www.gdacs.org/") and "fromdate=2026-09-01" in u and "todate=2026-09-02" in u

def test_gdacs_fixture_normalizes():
 req=current()
 payload={"features":[{"properties":{"eventid":123,"eventtype":"EQ","name":"M5 earthquake","fromdate":"2026-09-02T11:00:00Z"}}]}
 items=fetch(req,observed_at_utc="2026-09-28T12:01:00Z",http_get=lambda _:payload)
 assert normalize_observations(req,items)[0]["source_id"]=="gdacs-events"

def test_gdacs_historical_availability_not_backdated():
 req=sample(); payload={"features":[{"properties":{"eventid":123,"eventtype":"EQ","name":"M5 earthquake","fromdate":"2026-09-02T11:00:00Z"}}]}
 items=fetch(req,observed_at_utc="2026-09-28T12:01:00Z",http_get=lambda _:payload)
 assert items[0]["status"]=="INVALID"

def test_gdacs_transport_failure_explicit():
 items=fetch(current(),observed_at_utc="2026-09-28T12:01:00Z",http_get=lambda _:(_ for _ in ()).throw(TimeoutError()))
 assert items[0]["status"]=="UNAVAILABLE"

def test_gdacs_live_timestamp_shape_normalizes_to_z():
 req=current()
 payload={"features":[{"properties":{"eventid":1104199,"eventtype":"FL","name":"Flood in Spain",
          "fromdate":"2026-09-28T01:00:00","datemodified":"2026-10-07T10:45:49"}}]}
 items=fetch(req,observed_at_utc="2026-10-07T20:00:00Z",http_get=lambda _:payload)
 assert items[0]["published_at_utc"]=="2026-10-07T10:45:49Z"
