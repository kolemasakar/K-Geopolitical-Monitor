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
            "error_code":None if status in {"SUCCESS","PARTIAL"} else "TIMEOUT",\n            "partial_reason":"COVERAGE_GAP" if status=="PARTIAL" else None}

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

def test_post_request_observation_is_valid_for_current_retrieval():
    req=sample(); req["mode"]="CURRENT"; req.pop("as_of_utc")
    item=obs(); item["observed_at_utc"]="2026-09-28T12:01:00Z"
    assert validate_source_observation(req,item)["observed_at_utc"]=="2026-09-28T12:01:00Z"

def test_historical_lookahead_fails_closed():
    req=sample(); req["mode"]="HISTORICAL_AS_OF"; req["as_of_utc"]="2026-09-28T11:45:00Z"
    req["period_end_utc"]="2026-09-28T11:40:00Z"
    item=obs(); item["available_at_utc"]="2026-09-28T11:50:00Z"
    with pytest.raises(ValueError,match="lookahead"): validate_source_observation(req,item)

def test_duplicate_observation_fails_closed():
    req=sample(); item=obs()
    with pytest.raises(ValueError,match="duplicate"): normalize_observations(req,[item,copy.deepcopy(item)])


def test_partial_requires_typed_reason():
    req=sample(); item=obs("PARTIAL"); item["partial_reason"]=None
    with pytest.raises(ValueError,match="typed partial reason"):
        validate_source_observation(req,item)

def test_partial_reason_rejected_on_success():
    req=sample(); item=obs(); item["partial_reason"]="COVERAGE_GAP"
    with pytest.raises(ValueError,match="non-partial"):
        validate_source_observation(req,item)

def test_same_publication_under_different_native_ids_is_duplicate_evidence():
    req=sample(); a=obs(); b=copy.deepcopy(a)
    b["observation_id"]="obs-02"; b["source_id"]="source-b"
    with pytest.raises(ValueError,match="duplicate evidence fingerprint"):
        normalize_observations(req,[a,b])

def test_https_provenance_rejects_credentials_and_fragments():
    req=sample()
    for url in ("https://user:pass@example.test/item","https://example.test/item#frag","https:///missing-host"):
        item=obs(); item["public_url"]=url
        with pytest.raises(ValueError,match="provenance"):
            validate_source_observation(req,item)
