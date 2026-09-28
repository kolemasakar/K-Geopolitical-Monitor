"""Standalone KGM-side synthetic request -> fixture -> correlated response tests."""
import json
import pytest
from kgeopolitical_monitor.research_spool_v1 import submit, process_fixture, retrieve
from test_research_request_v1 import sample


POLICY = {"ktrader": "review-v1", "researcher": "review-v1"}


def fixture():
    return [{"record_id": "ev-1", "kind": "CLAIM_EVENT",
             "published_at_utc": "2026-09-01T08:00:00Z",
             "available_at_utc": "2026-09-02T08:00:00Z",
             "summary": "Synthetic event"}]


def process(root):
    return process_fixture(root, "ktrader", "req-01", allowed_consumers=POLICY,
                           evidence=fixture(), generated_at_utc="2026-09-28T12:00:00Z",
                           snapshot_id="synthetic", coverage="COMPLETE",
                           source_health="HEALTHY")


def test_durable_request_result_roundtrip(tmp_path):
    req = sample()
    first = submit(tmp_path, req, allowed_consumers=POLICY)
    assert first == submit(tmp_path, req, allowed_consumers=POLICY)
    artifact = process(tmp_path)
    assert process(tmp_path) == artifact
    assert retrieve(tmp_path, "ktrader", "req-01", allowed_consumers=POLICY) == artifact
    assert artifact["result"]["request_id"] == req["request_id"]


def test_conflicting_retry_rejected(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    other = sample()
    other["symbols"] = ["AAPL"]
    with pytest.raises(ValueError):
        submit(tmp_path, other, allowed_consumers=POLICY)


def test_unapproved_consumer_rejected(tmp_path):
    with pytest.raises(PermissionError):
        submit(tmp_path, sample(), allowed_consumers={})


def test_cross_consumer_result_denied(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    process(tmp_path)
    with pytest.raises(ValueError):
        retrieve(tmp_path, "researcher", "req-01", allowed_consumers=POLICY)


def test_tampered_result_denied(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    process(tmp_path)
    path = tmp_path / "outbox" / "ktrader" / "req-01.json"
    obj = json.loads(path.read_text())
    obj["result"]["records"][0]["summary"] = "Tampered"
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError):
        retrieve(tmp_path, "ktrader", "req-01", allowed_consumers=POLICY)


def test_historical_future_fixture_rejected(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    item = fixture()
    item[0]["available_at_utc"] = "2026-09-04T00:00:00Z"
    with pytest.raises(ValueError):
        process_fixture(tmp_path, "ktrader", "req-01", allowed_consumers=POLICY,
                        evidence=item, generated_at_utc="2026-09-28T12:00:00Z",
                        snapshot_id="synthetic", coverage="COMPLETE",
                        source_health="HEALTHY")
    assert not (tmp_path / "outbox" / "ktrader" / "req-01.json").exists()


def test_revoked_policy_blocks_processing(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    with pytest.raises(PermissionError):
        process_fixture(tmp_path, "ktrader", "req-01",
                        allowed_consumers={"ktrader": "review-v2"},
                        evidence=fixture(), generated_at_utc="2026-09-28T12:00:00Z",
                        snapshot_id="synthetic", coverage="COMPLETE",
                        source_health="HEALTHY")


def test_incomplete_coverage_explicit_partial(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    artifact = process_fixture(tmp_path, "ktrader", "req-01",
                               allowed_consumers=POLICY, evidence=[],
                               generated_at_utc="2026-09-28T12:00:00Z",
                               snapshot_id="synthetic", coverage="UNMEASURED",
                               source_health="UNMEASURED")
    assert artifact["result"]["research_status"] == "PARTIAL"
    assert artifact["result"]["records"] == []


def test_tampered_stored_request_denied(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    path = tmp_path / "inbox" / "ktrader--req-01.json"
    obj = json.loads(path.read_text())
    obj["request"]["symbols"] = ["AAPL"]
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError):
        submit(tmp_path, sample(), allowed_consumers=POLICY)
    with pytest.raises(ValueError):
        process(tmp_path)


def test_existing_corrupt_result_not_replayed(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    process(tmp_path)
    path = tmp_path / "outbox" / "ktrader" / "req-01.json"
    obj = json.loads(path.read_text())
    obj["result"]["coverage"] = "PARTIAL"
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError):
        process(tmp_path)


def test_policy_revocation_blocks_retrieval(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    process(tmp_path)
    with pytest.raises(ValueError):
        retrieve(tmp_path, "ktrader", "req-01",
                 allowed_consumers={"ktrader": "review-v2"})
