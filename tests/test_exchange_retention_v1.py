"""Synthetic retention policy safety tests."""
from datetime import datetime, timezone
import pytest
from kgeopolitical_monitor.exchange_retention_v1 import plan_retention, require_safe_retention, SnapshotRequired


def rows():
    return [{"sequence": 1, "created_utc": "2026-09-01T00:00:00Z"},
            {"sequence": 2, "created_utc": "2026-09-02T00:00:00Z"},
            {"sequence": 3, "created_utc": "2026-09-27T00:00:00Z"}]


def plan(cursors):
    return plan_retention(rows(), now_utc=datetime(2026, 9, 28, tzinfo=timezone.utc),
                          retention_days=7, acknowledged_sequences=cursors)


def test_block_unacknowledged_consumer():
    result = plan({"trader": 1, "other": 3})
    assert result["eligible_through"] == 2
    assert result["blocked_consumers"] == ["trader"]
    assert result["deletion_authorized"] is False
    with pytest.raises(SnapshotRequired):
        require_safe_retention(result, snapshot_approved=True)


def test_checkpoint_still_requires_approval():
    result = plan({"trader": 2, "other": 3})
    assert result["blocked_consumers"] == []
    with pytest.raises(SnapshotRequired):
        require_safe_retention(result)
    assert require_safe_retention(result, snapshot_approved=True)["deletion_authorized"] is False


def test_reject_missing_consumer_registry():
    with pytest.raises(ValueError):
        plan({})


def test_reject_cursor_ahead():
    with pytest.raises(ValueError):
        plan({"trader": 4})


def test_reject_ledger_gap():
    bad = rows()
    bad[1]["sequence"] = 4
    with pytest.raises(ValueError):
        plan_retention(bad, now_utc=datetime(2026, 9, 28, tzinfo=timezone.utc),
                       retention_days=7, acknowledged_sequences={"trader": 1})


def test_no_expired_batches():
    result = plan_retention(rows(), now_utc=datetime(2026, 9, 28, tzinfo=timezone.utc),
                            retention_days=60, acknowledged_sequences={"trader": 0})
    assert result["eligible_through"] == 0
    assert result["blocked_consumers"] == []
