"""Failure injection and stale-key tests for the owner-only durable cursor."""
import json
import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request
from kgeopolitical_monitor.research_durable_cursor_v1 import recover_durable
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

NOW = "2026-09-28T12:06:00Z"
A = "2026-09-28T12:01:00Z"


def _admit(root, name):
    request, _ = typed()
    accept_request(root, dict(request, request_id=name),
                   allowed_consumers=POLICY, accepted_at_utc=A)


def test_cursor_write_failure_preserves_previous_cursor(tmp_path, monkeypatch):
    _admit(tmp_path, "req-01")
    _admit(tmp_path, "req-02")
    first = recover_durable(tmp_path, allowed_consumers=POLICY,
                            observed_at_utc=NOW, max_items=1)
    assert first["pending"] == [("ktrader", "req-01")]
    cursor = tmp_path / ".research-recovery-cursor.json"
    previous = cursor.read_bytes()
    import kgeopolitical_monitor.research_durable_cursor_v1 as module
    def injected_failure(*args, **kwargs):
        raise OSError("synthetic cursor write failure")
    monkeypatch.setattr(module, "_atomic", injected_failure)
    with pytest.raises(OSError, match="synthetic"):
        recover_durable(tmp_path, allowed_consumers=POLICY,
                        observed_at_utc=NOW, max_items=1)
    assert cursor.read_bytes() == previous


def test_stale_cursor_after_pending_queue_changes(tmp_path):
    _admit(tmp_path, "req-02")
    first = recover_durable(tmp_path, allowed_consumers=POLICY,
                            observed_at_utc=NOW, max_items=1)
    assert first["next_cursor"] == ("ktrader", "req-02")
    _admit(tmp_path, "req-01")
    second = recover_durable(tmp_path, allowed_consumers=POLICY,
                             observed_at_utc=NOW, max_items=1)
    assert second["pending"] == [("ktrader", "req-01")]


def test_corrupted_cursor_does_not_get_overwritten(tmp_path):
    _admit(tmp_path, "req-01")
    cursor = tmp_path / ".research-recovery-cursor.json"
    cursor.write_text('{"version":1,"after_key":["ktrader"]}')
    before = cursor.read_bytes()
    with pytest.raises(ValueError):
        recover_durable(tmp_path, allowed_consumers=POLICY,
                        observed_at_utc=NOW, max_items=1)
    assert cursor.read_bytes() == before
