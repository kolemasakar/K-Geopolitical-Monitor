"""Synthetic request-correlated lifecycle tests."""
import pytest
from kgeopolitical_monitor.research_lifecycle_v1 import SyntheticResearchJob
from test_research_request_v1 import sample


def evidence():
    return [{"record_id": "ev-1", "kind": "CLAIM_EVENT",
             "published_at_utc": "2026-09-01T08:00:00Z",
             "available_at_utc": "2026-09-02T08:00:00Z",
             "summary": "Synthetic event"}]


def processing():
    job = SyntheticResearchJob(sample())
    job.transition("ACCEPTED")
    job.transition("PROCESSING")
    return job


def test_correlated_historical_result():
    job = processing()
    result = job.complete_fixture(evidence(), generated_at_utc="2026-09-28T12:00:00Z",
                                  snapshot_id="synthetic-snapshot", coverage="COMPLETE",
                                  source_health="HEALTHY")
    assert result["request_id"] == "req-01"
    assert result["research_status"] == "COMPLETE"


def test_idempotent_retry():
    job = processing()
    assert job.retry(sample()) is job


def test_idempotency_conflict():
    job = processing()
    other = sample()
    other["symbols"] = ["AAPL"]
    with pytest.raises(ValueError):
        job.retry(other)


def test_no_lookahead():
    job = processing()
    future = evidence()
    future[0]["available_at_utc"] = "2026-09-04T00:00:00Z"
    with pytest.raises(ValueError):
        job.complete_fixture(future, generated_at_utc="2026-09-28T12:00:00Z",
                             snapshot_id="synthetic-snapshot", coverage="COMPLETE",
                             source_health="HEALTHY")
    assert job.status == "PROCESSING"


def test_partial_not_empty_proof():
    job = processing()
    result = job.complete_fixture([], generated_at_utc="2026-09-28T12:00:00Z",
                                  snapshot_id="synthetic-snapshot", coverage="UNMEASURED",
                                  source_health="UNMEASURED")
    assert result["research_status"] == "PARTIAL"
    assert result["records"] == []


def test_terminal_transition_rejected():
    job = processing()
    job.transition("FAILED")
    with pytest.raises(ValueError):
        job.transition("PROCESSING")


def test_unapproved_field_rejected():
    job = processing()
    item = evidence()[0]
    item["private_token"] = "synthetic"
    with pytest.raises(ValueError):
        job.complete_fixture([item], generated_at_utc="2026-09-28T12:00:00Z",
                             snapshot_id="synthetic-snapshot", coverage="COMPLETE",
                             source_health="HEALTHY")
