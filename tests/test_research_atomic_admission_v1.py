import json
import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request, recover_registered
from kgeopolitical_monitor.research_durable_lifecycle_v1 import recovery_snapshot
from kgeopolitical_monitor.research_deadline_registry_v1 import registered_deadlines
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

def test_atomic_deadline_survives_restart(tmp_path):
    request, _ = typed()
    saved = accept_request(tmp_path, request, allowed_consumers=POLICY,
                           accepted_at_utc="2026-09-28T12:01:00Z",
                           deadline_utc="2026-09-28T12:05:00Z")
    assert saved["deadline_utc"] == "2026-09-28T12:05:00Z"
    assert not list((tmp_path / "inbox").glob("*.deadline.json"))
    assert registered_deadlines(tmp_path, allowed_consumers=POLICY)
    report = recover_registered(tmp_path, allowed_consumers=POLICY,
                                observed_at_utc="2026-09-28T12:06:00Z")
    assert report["expired"] == [("ktrader", "req-01")]

def test_atomic_deadline_conflict(tmp_path):
    request, _ = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY,
                   accepted_at_utc="2026-09-28T12:01:00Z",
                   deadline_utc="2026-09-28T12:05:00Z")
    with pytest.raises(ValueError):
        accept_request(tmp_path, request, allowed_consumers=POLICY,
                       accepted_at_utc="2026-09-28T12:01:00Z",
                       deadline_utc="2026-09-28T12:07:00Z")


def test_embedded_deadline_mutation_fails_closed(tmp_path):
    request, _ = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY,
                   accepted_at_utc="2026-09-28T12:01:00Z",
                   deadline_utc="2026-09-28T12:05:00Z")
    target = tmp_path / "inbox" / "ktrader--req-01.json"
    saved = json.loads(target.read_text())
    saved["deadline_utc"] = "2026-09-28T12:09:00Z"
    target.write_text(json.dumps(saved))
    with pytest.raises(ValueError, match="deadline digest mismatch"):
        recovery_snapshot(tmp_path, allowed_consumers=POLICY)


def test_orphan_deadline_digest_fails_closed(tmp_path):
    request, _ = typed()
    accept_request(tmp_path, request, allowed_consumers=POLICY,
                   accepted_at_utc="2026-09-28T12:01:00Z")
    target = tmp_path / "inbox" / "ktrader--req-01.json"
    saved = json.loads(target.read_text())
    saved["deadline_digest"] = "0" * 64
    target.write_text(json.dumps(saved))
    with pytest.raises(ValueError, match="orphan deadline digest"):
        recovery_snapshot(tmp_path, allowed_consumers=POLICY)
