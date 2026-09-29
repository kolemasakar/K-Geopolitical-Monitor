"""Acceptance tests for the canonical synthetic typed durable workflow."""
import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import (
    accept_request, begin_processing, publish_and_complete, recover_pending)
from kgeopolitical_monitor.research_durable_lifecycle_v1 import recovery_snapshot
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY


def test_complete_end_to_end(tmp_path):
    request, result = typed()
    accepted = accept_request(tmp_path, request, allowed_consumers=POLICY,
                              accepted_at_utc="2026-09-28T12:01:00Z")
    assert accepted["status"] == "ACCEPTED"
    processing = begin_processing(tmp_path, "ktrader", "req-01",
                                  allowed_consumers=POLICY,
                                  at_utc="2026-09-28T12:02:00Z")
    assert processing["attempts"] == 1
    artifact = publish_and_complete(tmp_path, "ktrader", "req-01", result,
                                    allowed_consumers=POLICY,
                                    at_utc="2026-09-28T12:04:00Z")
    assert artifact["result"]["research_status"] == "COMPLETE"
    assert recover_pending(tmp_path, allowed_consumers=POLICY,
                           observed_at_utc="2026-09-28T12:06:00Z")["reconciled"] == []
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []


def test_accept_idempotent(tmp_path):
    request, _ = typed()
    first = accept_request(tmp_path, request, allowed_consumers=POLICY,
                           accepted_at_utc="2026-09-28T12:01:00Z")
    second = accept_request(tmp_path, request, allowed_consumers=POLICY,
                            accepted_at_utc="2026-09-28T12:02:00Z")
    assert first == second


def test_quota_enforced(tmp_path):
    request, _ = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY,
                   max_pending_per_consumer=1,
                   accepted_at_utc="2026-09-28T12:01:00Z")
    changed = dict(request, request_id="req-02")
    with pytest.raises(ValueError):
        accept_request(tmp_path, changed, allowed_consumers=POLICY,
                       max_pending_per_consumer=1,
                       accepted_at_utc="2026-09-28T12:02:00Z")
