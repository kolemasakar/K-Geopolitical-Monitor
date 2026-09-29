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
