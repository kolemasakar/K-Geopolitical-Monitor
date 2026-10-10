"""Synthetic deadline expiry and recovery boundaries."""
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, recovery_snapshot
from kgeopolitical_monitor.research_expiry_v1 import expire_stale
from kgeopolitical_monitor.research_typed_spool_v1 import publish_typed_fixture
from test_research_request_v1 import sample
from test_research_completion_v1 import processing, POLICY
from test_research_typed_result_v1 import typed

DEADLINE = "2026-09-28T12:05:00Z"
AFTER = "2026-09-28T12:06:00Z"


def test_expire_unfinished_and_idempotent(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    first = expire_stale(tmp_path, "ktrader", "req-01",
                         allowed_consumers=POLICY, deadline_utc=DEADLINE,
                         observed_at_utc=AFTER)
    assert first["status"] == "EXPIRED"
    assert expire_stale(tmp_path, "ktrader", "req-01",
                        allowed_consumers=POLICY, deadline_utc=DEADLINE,
                        observed_at_utc=AFTER) == first
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []


def test_not_expired_before_deadline(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    with pytest.raises(ValueError):
        expire_stale(tmp_path, "ktrader", "req-01",
                     allowed_consumers=POLICY, deadline_utc=DEADLINE,
                     observed_at_utc="2026-09-28T12:04:00Z")


def test_published_result_must_reconcile_first(tmp_path):
    result = processing(tmp_path)
    publish_typed_fixture(tmp_path, "ktrader", "req-01", result,
                          allowed_consumers=POLICY)
    with pytest.raises(ValueError):
        expire_stale(tmp_path, "ktrader", "req-01",
                     allowed_consumers=POLICY, deadline_utc=DEADLINE,
                     observed_at_utc=AFTER)
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "PROCESSING"


def test_revoked_policy_blocks_expiry(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    with pytest.raises(PermissionError):
        expire_stale(tmp_path, "ktrader", "req-01",
                     allowed_consumers={"ktrader": "review-v2"},
                     deadline_utc=DEADLINE, observed_at_utc=AFTER)
