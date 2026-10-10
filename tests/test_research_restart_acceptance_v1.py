"""Canonical restart/fault acceptance for the synthetic research workflow."""
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, advance, recovery_snapshot
from kgeopolitical_monitor.research_completion_v1 import complete_or_reconcile
from kgeopolitical_monitor.research_typed_spool_v1 import publish_typed_fixture
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

def test_restart_after_admission_recovers_received(tmp_path):
    req, _ = typed()
    admit(tmp_path, req, allowed_consumers=POLICY)
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == [{
        "consumer_id": "ktrader", "request_id": "req-01",
        "status": "RECEIVED", "attempts": 0,
    }]

def test_restart_after_accept_recovers_accepted(tmp_path):
    req, _ = typed()
    admit(tmp_path, req, allowed_consumers=POLICY)
    advance(tmp_path, "ktrader", "req-01", "ACCEPTED",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:01:00Z")
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "ACCEPTED"

def test_restart_after_processing_preserves_attempt(tmp_path):
    req, _ = typed()
    admit(tmp_path, req, allowed_consumers=POLICY)
    advance(tmp_path, "ktrader", "req-01", "ACCEPTED",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:01:00Z")
    advance(tmp_path, "ktrader", "req-01", "PROCESSING",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:02:00Z")
    recovered = recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]
    assert (recovered["status"], recovered["attempts"]) == ("PROCESSING", 1)

def test_restart_after_artifact_reconciles_exactly_once(tmp_path):
    req, result = typed()
    admit(tmp_path, req, allowed_consumers=POLICY)
    advance(tmp_path, "ktrader", "req-01", "ACCEPTED",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:01:00Z")
    advance(tmp_path, "ktrader", "req-01", "PROCESSING",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:02:00Z")
    artifact = publish_typed_fixture(tmp_path, "ktrader", "req-01", result,
                                     allowed_consumers=POLICY)
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "PROCESSING"
    first = complete_or_reconcile(tmp_path, "ktrader", "req-01",
                                  allowed_consumers=POLICY,
                                  at_utc="2026-09-28T12:04:00Z")
    second = complete_or_reconcile(tmp_path, "ktrader", "req-01",
                                   allowed_consumers=POLICY)
    assert first == second == artifact
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []

def test_restart_without_artifact_cannot_invent_terminal(tmp_path):
    req, _ = typed()
    admit(tmp_path, req, allowed_consumers=POLICY)
    advance(tmp_path, "ktrader", "req-01", "ACCEPTED",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:01:00Z")
    advance(tmp_path, "ktrader", "req-01", "PROCESSING",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:02:00Z")
    with pytest.raises(ValueError, match="result not yet published"):
        complete_or_reconcile(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY,
                              at_utc="2026-09-28T12:04:00Z")
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "PROCESSING"
