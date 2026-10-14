"""Durable KGM-only fixture lifecycle and quota tests."""
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, advance, recovery_snapshot
from test_research_request_v1 import sample

POLICY = {"ktrader": "review-v1"}


def test_restart_recovery_and_terminal(tmp_path):
    req = sample()
    admit(tmp_path, req, allowed_consumers=POLICY)
    advance(tmp_path, "ktrader", "req-01", "ACCEPTED", allowed_consumers=POLICY,
            at_utc="2026-09-28T12:01:00Z")
    processing = advance(tmp_path, "ktrader", "req-01", "PROCESSING",
                         allowed_consumers=POLICY, at_utc="2026-09-28T12:02:00Z")
    assert processing["attempts"] == 1
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "PROCESSING"
    with pytest.raises(ValueError, match="typed terminal completion required"):
        advance(tmp_path, "ktrader", "req-01", "PARTIAL", allowed_consumers=POLICY,
                at_utc="2026-09-28T12:03:00Z")
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "PROCESSING"


def test_pending_quota_and_idempotent_retry(tmp_path):
    req = sample()
    first = admit(tmp_path, req, allowed_consumers=POLICY, max_pending_per_consumer=1)
    assert admit(tmp_path, req, allowed_consumers=POLICY, max_pending_per_consumer=1) == first
    other = sample()
    other["request_id"] = "req-02"
    with pytest.raises(ValueError):
        admit(tmp_path, other, allowed_consumers=POLICY, max_pending_per_consumer=1)
    advance(tmp_path, "ktrader", "req-01", "EXPIRED", allowed_consumers=POLICY,
            at_utc="2026-09-28T12:01:00Z")
    assert admit(tmp_path, other, allowed_consumers=POLICY, max_pending_per_consumer=1)


def test_conflicting_request_id(tmp_path):
    req = sample()
    admit(tmp_path, req, allowed_consumers=POLICY)
    req["symbols"] = ["AAPL"]
    with pytest.raises(ValueError):
        admit(tmp_path, req, allowed_consumers=POLICY)


def test_illegal_transition_and_time_reversal(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    with pytest.raises(ValueError):
        advance(tmp_path, "ktrader", "req-01", "COMPLETE",
                allowed_consumers=POLICY, at_utc="2026-09-28T12:01:00Z")
    with pytest.raises(ValueError):
        advance(tmp_path, "ktrader", "req-01", "ACCEPTED",
                allowed_consumers=POLICY, at_utc="2026-09-28T11:00:00Z")


def test_revoked_policy_recovery_and_transition(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    assert recovery_snapshot(tmp_path, allowed_consumers={"ktrader": "review-v2"}) == []
    with pytest.raises(PermissionError):
        advance(tmp_path, "ktrader", "req-01", "ACCEPTED",
                allowed_consumers={"ktrader": "review-v2"},
                at_utc="2026-09-28T12:01:00Z")


def test_corrupted_stored_request_rejected(tmp_path):
    import json
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    path = tmp_path / "inbox" / "ktrader--req-01.json"
    saved = json.loads(path.read_text())
    saved["request"]["symbols"] = ["AAPL"]
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        recovery_snapshot(tmp_path, allowed_consumers=POLICY)
