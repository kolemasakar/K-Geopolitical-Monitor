"""Crash-boundary reconciliation tests, KGM-only synthetic fixtures."""
import copy
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, advance, recovery_snapshot
from kgeopolitical_monitor.research_typed_spool_v1 import publish_typed_fixture
from kgeopolitical_monitor.research_completion_v1 import complete_or_reconcile
from test_research_typed_result_v1 import typed

POLICY = {"ktrader": "review-v1"}
STAMP = "2026-09-28T12:04:00Z"


def processing(root):
    req, result = typed()
    admit(root, req, allowed_consumers=POLICY)
    advance(root, "ktrader", "req-01", "ACCEPTED", allowed_consumers=POLICY,
            at_utc="2026-09-28T12:01:00Z")
    advance(root, "ktrader", "req-01", "PROCESSING", allowed_consumers=POLICY,
            at_utc="2026-09-28T12:02:00Z")
    return result


def test_complete_typed_result_and_replay(tmp_path):
    result = processing(tmp_path)
    artifact = complete_or_reconcile(tmp_path, "ktrader", "req-01",
                                     allowed_consumers=POLICY, result=result, at_utc=STAMP)
    assert artifact["result"]["research_status"] == "COMPLETE"
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []
    assert complete_or_reconcile(tmp_path, "ktrader", "req-01",
                                 allowed_consumers=POLICY) == artifact


def test_crash_after_publication_reconciles(tmp_path):
    result = processing(tmp_path)
    artifact = publish_typed_fixture(tmp_path, "ktrader", "req-01", result,
                                     allowed_consumers=POLICY)
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "PROCESSING"
    assert complete_or_reconcile(tmp_path, "ktrader", "req-01",
                                 allowed_consumers=POLICY, at_utc=STAMP) == artifact
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []


def test_no_artifact_never_claim_complete(tmp_path):
    processing(tmp_path)
    with pytest.raises(ValueError):
        complete_or_reconcile(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY, at_utc=STAMP)
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)


def test_conflicting_replay_denied(tmp_path):
    result = processing(tmp_path)
    complete_or_reconcile(tmp_path, "ktrader", "req-01",
                          allowed_consumers=POLICY, result=result, at_utc=STAMP)
    changed = copy.deepcopy(result)
    changed["records"][0]["summary"] = "Changed"
    with pytest.raises(ValueError):
        complete_or_reconcile(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY, result=changed, at_utc=STAMP)


def test_revocation_blocks_reconciliation(tmp_path):
    result = processing(tmp_path)
    publish_typed_fixture(tmp_path, "ktrader", "req-01", result, allowed_consumers=POLICY)
    with pytest.raises(PermissionError):
        complete_or_reconcile(tmp_path, "ktrader", "req-01",
                              allowed_consumers={"ktrader": "review-v2"}, at_utc=STAMP)


def test_partial_reconciles_as_partial(tmp_path):
    result = processing(tmp_path)
    result["coverage"] = "UNMEASURED"
    result["source_health"] = "UNMEASURED"
    result["research_status"] = "PARTIAL"
    artifact = complete_or_reconcile(tmp_path, "ktrader", "req-01",
                                     allowed_consumers=POLICY, result=result, at_utc=STAMP)
    assert artifact["result"]["research_status"] == "PARTIAL"
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY) == []
