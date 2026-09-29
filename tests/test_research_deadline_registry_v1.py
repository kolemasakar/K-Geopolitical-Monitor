"""Durable deadline registry and mixed offline recovery acceptance."""
import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import (
    accept_request, begin_processing, register_request_deadline, recover_registered)
from kgeopolitical_monitor.research_typed_spool_v1 import publish_typed_fixture
from kgeopolitical_monitor.research_deadline_registry_v1 import registered_deadlines
from kgeopolitical_monitor.research_durable_lifecycle_v1 import recovery_snapshot
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

A = "2026-09-28T12:01:00Z"
B = "2026-09-28T12:02:00Z"
DEADLINE = "2026-09-28T12:05:00Z"
NOW = "2026-09-28T12:06:00Z"


def test_deadline_survives_recovery_and_expires(tmp_path):
    request, _ = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY, accepted_at_utc=A)
    register_request_deadline(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY, deadline_utc=DEADLINE)
    assert registered_deadlines(tmp_path, allowed_consumers=POLICY) == {
        ("ktrader", "req-01"): DEADLINE}
    assert recover_registered(tmp_path, allowed_consumers=POLICY,
                              observed_at_utc=NOW)["expired"] == [("ktrader", "req-01")]
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []


def test_mixed_workload_recovers_before_expiring(tmp_path):
    request, result = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY, accepted_at_utc=A)
    begin_processing(tmp_path, "ktrader", "req-01",
                     allowed_consumers=POLICY, at_utc=B)
    register_request_deadline(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY, deadline_utc=DEADLINE)
    publish_typed_fixture(tmp_path, "ktrader", "req-01", result,
                          allowed_consumers=POLICY)
    second = dict(request, request_id="req-02")
    accept_request(tmp_path, second, allowed_consumers=POLICY, accepted_at_utc=A)
    register_request_deadline(tmp_path, "ktrader", "req-02",
                              allowed_consumers=POLICY, deadline_utc=DEADLINE)
    report = recover_registered(tmp_path, allowed_consumers=POLICY,
                                observed_at_utc=NOW)
    assert report["reconciled"] == [("ktrader", "req-01")]
    assert report["expired"] == [("ktrader", "req-02")]
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []


def test_conflicting_deadline_rejected(tmp_path):
    request, _ = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY, accepted_at_utc=A)
    register_request_deadline(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY, deadline_utc=DEADLINE)
    with pytest.raises(ValueError):
        register_request_deadline(tmp_path, "ktrader", "req-01",
                                  allowed_consumers=POLICY,
                                  deadline_utc="2026-09-28T12:07:00Z")


def test_deadline_does_not_consume_request_quota(tmp_path):
    request, _ = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY,
                   max_pending_per_consumer=2, accepted_at_utc=A)
    register_request_deadline(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY, deadline_utc=DEADLINE)
    accept_request(tmp_path, dict(request, request_id="req-02"),
                   allowed_consumers=POLICY, max_pending_per_consumer=2,
                   accepted_at_utc=A)
    assert len(recovery_snapshot(tmp_path, allowed_consumers=POLICY)) == 2
