import copy
import pytest
from kgeopolitical_monitor.research_source_adapter_v1 import validate_source_observation, normalize_observations
from test_research_request_v1 import sample

def obs(status="SUCCESS"):
    return {"schema_version":"kgm.source.observation.v1","request_id":"req-01",
            "source_id":"source-a","observation_id":"obs-01","status":status,
            "observed_at_utc":"2026-09-28T11:59:00Z",
            "published_at_utc":"2026-09-02T11:00:00Z" if status in {"SUCCESS","PARTIAL"} else None,
            "available_at_utc":"2026-09-02T11:30:00Z" if status in {"SUCCESS","PARTIAL"} else None,
            "public_url":"https://example.test/item" if status in {"SUCCESS","PARTIAL"} else None,
            "summary":"deterministic evidence" if status in {"SUCCESS","PARTIAL"} else None,
            "error_code":None if status in {"SUCCESS","PARTIAL"} else "TIMEOUT"}

def test_success_and_partial_validate():
    req=sample()
    assert validate_source_observation(req,obs())["status"]=="SUCCESS"
    assert validate_source_observation(req,obs("PARTIAL"))["status"]=="PARTIAL"

def test_unavailable_requires_explicit_error():
    req=sample(); item=obs("UNAVAILABLE")
    assert validate_source_observation(req,item)["error_code"]=="TIMEOUT"
    item["error_code"]=None
    with pytest.raises(ValueError): validate_source_observation(req,item)

def test_failed_source_cannot_carry_evidence():
    req=sample(); item=obs("INVALID"); item["summary"]="bad"
    with pytest.raises(ValueError): validate_source_observation(req,item)

def test_future_observation_fails_closed():
    req=sample(); item=obs(); item["observed_at_utc"]="2026-09-28T12:01:00Z"
    with pytest.raises(ValueError,match="after request"): validate_source_observation(req,item)

def test_historical_lookahead_fails_closed():
    req=sample(); req["mode"]="HISTORICAL_AS_OF"; req["as_of_utc"]="2026-09-28T11:45:00Z"
    req["period_end_utc"]="2026-09-28T11:40:00Z"
    item=obs(); item["available_at_utc"]="2026-09-28T11:50:00Z"
    with pytest.raises(ValueError,match="lookahead"): validate_source_observation(req,item)

def test_duplicate_observation_fails_closed():
    req=sample(); item=obs()
    with pytest.raises(ValueError,match="duplicate"): normalize_observations(req,[item,copy.deepcopy(item)])
