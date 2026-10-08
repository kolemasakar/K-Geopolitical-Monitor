"""Synthetic typed response contract; historical and forecast negative cases."""
import copy
import pytest
from kgeopolitical_monitor.research_typed_result_v1 import validate_typed_result
from test_research_request_v1 import sample


def typed():
    req = sample()
    result = {"schema_version": "kgm.research.result.v1",
              "request_id": "req-01", "consumer_id": "ktrader",
              "result_id": "synthetic-1", "generated_at_utc": "2026-09-28T12:00:00Z",
              "producer_snapshot_id": "synthetic", "policy_version": "review-v1",
              "research_status": "COMPLETE", "coverage": "COMPLETE",
              "source_health": "HEALTHY",
              "records": [{"record_id": "e1", "kind": "CLAIM_EVENT",
                           "summary": "Synthetic source-backed event",
                           "verification": "DISPUTED",
                           "evidence": [{"source_id": "synthetic-source",
                                         "public_url": "https://example.org/synthetic",
                                         "published_at_utc": "2026-09-01T00:00:00Z",
                                         "available_at_utc": "2026-09-02T00:00:00Z"}],
                           "contradictions": ["conflicting-source"],
                           "revision_of": None, "forecast": None}]}
    return req, result


def test_disputed_event_provenance():
    req, result = typed()
    assert validate_typed_result(req, result) is result


def test_no_future_evidence():
    req, result = typed()
    result["records"][0]["evidence"][0]["available_at_utc"] = "2026-09-04T00:00:00Z"
    with pytest.raises(ValueError):
        validate_typed_result(req, result)


def test_false_complete_denied():
    req, result = typed()
    result["coverage"] = "UNMEASURED"
    with pytest.raises(ValueError):
        validate_typed_result(req, result)


def test_forecast_must_be_typed():
    req, result = typed()
    result["records"][0]["kind"] = "FORECAST_VERSION"
    with pytest.raises(ValueError):
        validate_typed_result(req, result)
    result["records"][0]["forecast"] = {"assumptions": "Synthetic assumptions",
                                        "scenario": "Synthetic scenario",
                                        "uncertainty": "Unmeasured"}
    assert validate_typed_result(req, result)


def test_duplicate_record_denied():
    req, result = typed()
    result["records"].append(copy.deepcopy(result["records"][0]))
    with pytest.raises(ValueError):
        validate_typed_result(req, result)


def test_cross_consumer_denied():
    req, result = typed()
    result["consumer_id"] = "other"
    with pytest.raises(ValueError):
        validate_typed_result(req, result)


def test_empty_unmeasured_partial():
    req, result = typed()
    result["records"] = []
    result["coverage"] = "UNMEASURED"
    result["source_health"] = "UNMEASURED"
    result["research_status"] = "PARTIAL"
    assert validate_typed_result(req, result)


def _v2():
    req,result=typed()
    result["schema_version"]="kgm.research.result.v2"
    result["corroboration"]=[{
        "corroboration_id":"corr-1",
        "members":[
            {"source_id":"source-a","observation_id":"a1","origin_group":"origin-a","claim_signature":"mag-50"},
            {"source_id":"source-b","observation_id":"b1","origin_group":"origin-b","claim_signature":"mag-50"}],
        "source_ids":["source-a","source-b"],
        "max_delta_seconds":2.0,"max_distance_km":10.0,
        "claim_relation":"AGREES","origin_assessment":"DISTINCT_ORIGIN",
        "origin_groups":["origin-a","origin-b"],"independent_origin_credit":True,
        "ambiguous":False,"factual_verification_credit":False}]
    return req,result

def test_v2_corroboration_is_typed_and_does_not_auto_verify():
    req,result=_v2()
    assert validate_typed_result(req,result) is result
    result["corroboration"][0]["factual_verification_credit"]=True
    with pytest.raises(ValueError,match="cannot auto-verify"):
        validate_typed_result(req,result)

def test_v2_ambiguous_corroboration_cannot_keep_origin_credit():
    req,result=_v2()
    result["corroboration"][0]["ambiguous"]=True
    with pytest.raises(ValueError,match="ambiguous corroboration credit denied"):
        validate_typed_result(req,result)
