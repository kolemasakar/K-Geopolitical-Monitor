"""Offline bounded recovery acceptance tests; synthetic local data only."""
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, recovery_snapshot
from kgeopolitical_monitor.research_typed_spool_v1 import publish_typed_fixture
from kgeopolitical_monitor.research_recovery_pass_v1 import recovery_pass
from test_research_request_v1 import sample
from test_research_completion_v1 import processing, POLICY
import pytest

NOW = "2026-09-28T12:06:00Z"
DEADLINE = "2026-09-28T12:05:00Z"
KEY = ("ktrader", "req-01")


def test_reconciles_existing_artifact_before_deadline(tmp_path):
    result = processing(tmp_path)
    publish_typed_fixture(tmp_path, "ktrader", "req-01", result,
                          allowed_consumers=POLICY)
    report = recovery_pass(tmp_path, allowed_consumers=POLICY,
                           observed_at_utc=NOW, deadlines={KEY: DEADLINE})
    assert report["reconciled"] == [KEY]
    assert report["expired"] == []
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []


def test_explicit_deadline_expires_unpublished(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    report = recovery_pass(tmp_path, allowed_consumers=POLICY,
                           observed_at_utc=NOW, deadlines={KEY: DEADLINE})
    assert report["expired"] == [KEY]
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []


def test_no_deadline_keeps_pending(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    report = recovery_pass(tmp_path, allowed_consumers=POLICY,
                           observed_at_utc=NOW)
    assert report["pending"] == [KEY]


def test_bounded_zero_work(tmp_path):
    report = recovery_pass(tmp_path, allowed_consumers=POLICY,
                           observed_at_utc=NOW, max_items=1)
    assert report["reconciled"] == []
    assert report["remaining"] == 0


def test_invalid_bound_rejected(tmp_path):
    with pytest.raises(ValueError):
        recovery_pass(tmp_path, allowed_consumers=POLICY,
                      observed_at_utc=NOW, max_items=0)
