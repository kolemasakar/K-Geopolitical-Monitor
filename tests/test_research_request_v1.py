"""Synthetic request-driven schema and no-lookahead acceptance tests."""
import pytest
from kgeopolitical_monitor.research_request_v1 import validate_request, historically_available


def sample():
    return {"schema_version": "kgm.research.request.v1",
            "request_id": "req-01", "consumer_id": "ktrader",
            "requested_at_utc": "2026-09-28T12:00:00Z",
            "mode": "HISTORICAL_AS_OF", "symbols": ["EURUSD", "BTCUSDT"],
            "period_start_utc": "2026-09-01T00:00:00Z",
            "period_end_utc": "2026-09-02T00:00:00Z",
            "as_of_utc": "2026-09-03T00:00:00Z",
            "max_results": 20, "policy_version": "review-v1"}


def test_valid_historical_request():
    assert validate_request(sample())["request_id"] == "req-01"


def test_missing_as_of_rejected():
    req = sample()
    del req["as_of_utc"]
    with pytest.raises(ValueError):
        validate_request(req)


def test_hindsight_window_rejected():
    req = sample()
    req["period_end_utc"] = "2026-09-04T00:00:00Z"
    with pytest.raises(ValueError):
        validate_request(req)


def test_unbounded_symbols_rejected():
    req = sample()
    req["symbols"] = ["SYM" + str(n) for n in range(21)]
    with pytest.raises(ValueError):
        validate_request(req)


def test_unapproved_request_field_rejected():
    req = sample()
    req["private_path"] = "/synthetic"
    with pytest.raises(ValueError):
        validate_request(req)


def test_historical_evidence_dual_cutoff():
    evidence = {"published_at_utc": "2026-09-02T00:00:00Z",
                "available_at_utc": "2026-09-03T00:00:00Z"}
    assert historically_available(evidence, "2026-09-03T00:00:00Z")
    assert not historically_available(evidence, "2026-09-02T23:59:59Z")


def test_missing_ingestion_rejected():
    assert not historically_available(
        {"published_at_utc": "2026-09-02T00:00:00Z"},
        "2026-09-03T00:00:00Z")


def test_valid_current_request():
    req = sample()
    req["mode"] = "CURRENT"
    del req["as_of_utc"]
    assert validate_request(req)["mode"] == "CURRENT"
