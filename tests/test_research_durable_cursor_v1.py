import json
import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request
from kgeopolitical_monitor.research_durable_cursor_v1 import recover_durable
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

NOW = "2026-09-28T12:06:00Z"
A = "2026-09-28T12:01:00Z"


def _three(root):
    request, _ = typed()
    for identifier in ("req-01", "req-02", "req-03"):
        accept_request(root, dict(request, request_id=identifier),
                       allowed_consumers=POLICY, accepted_at_utc=A)


def test_cursor_survives_independent_calls_and_wraps(tmp_path):
    _three(tmp_path)
    keys = []
    for _ in range(4):
        report = recover_durable(tmp_path, allowed_consumers=POLICY,
                                 observed_at_utc=NOW, max_items=1)
        keys.append(report["pending"][0])
    assert keys == [("ktrader", "req-01"), ("ktrader", "req-02"),
                    ("ktrader", "req-03"), ("ktrader", "req-01")]
    record = json.loads((tmp_path / ".research-recovery-cursor.json").read_text())
    assert record == {"version": 1, "after_key": ["ktrader", "req-01"]}


def test_corrupt_cursor_fails_closed(tmp_path):
    _three(tmp_path)
    (tmp_path / ".research-recovery-cursor.json").write_text('{"version":2,"after_key":null}')
    with pytest.raises(ValueError, match="cursor"):
        recover_durable(tmp_path, allowed_consumers=POLICY,
                        observed_at_utc=NOW, max_items=1)


def test_no_pending_preserves_last_cursor(tmp_path):
    report = recover_durable(tmp_path, allowed_consumers=POLICY,
                             observed_at_utc=NOW, max_items=1)
    assert report["next_cursor"] is None
    assert report["remaining"] == 0
