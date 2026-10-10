"""Fail-closed separation of minimal legacy and canonical durable spool formats."""
import pytest
from kgeopolitical_monitor.research_spool_v1 import submit
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, recovery_snapshot
from test_research_request_v1 import sample

POLICY = {"ktrader": "review-v1"}


def test_canonical_recovery_rejects_legacy_minimal_record(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    with pytest.raises(ValueError, match="noncanonical"):
        recovery_snapshot(tmp_path, allowed_consumers=POLICY)


def test_canonical_admission_rejects_mixed_spool(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    second = sample()
    second["request_id"] = "req-02"
    with pytest.raises(ValueError, match="noncanonical"):
        admit(tmp_path, second, allowed_consumers=POLICY)
    assert not (tmp_path / "inbox" / "ktrader--req-02.json").exists()


def test_canonical_retry_rejects_legacy_same_id(tmp_path):
    submit(tmp_path, sample(), allowed_consumers=POLICY)
    with pytest.raises(ValueError, match="noncanonical"):
        admit(tmp_path, sample(), allowed_consumers=POLICY)
