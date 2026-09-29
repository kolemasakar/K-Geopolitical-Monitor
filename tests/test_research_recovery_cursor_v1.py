from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request, recover_registered
from kgeopolitical_monitor.research_recovery_pass_v1 import recovery_pass
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY
import pytest

NOW = "2026-09-28T12:06:00Z"
A = "2026-09-28T12:01:00Z"


def test_cursor_advances_past_stalled_first_request(tmp_path):
    original, _ = typed()
    for identifier in ("req-01", "req-02", "req-03"):
        accept_request(tmp_path, dict(original, request_id=identifier),
                       allowed_consumers=POLICY, accepted_at_utc=A)
    first = recover_registered(tmp_path, allowed_consumers=POLICY,
                               observed_at_utc=NOW, max_items=1)
    assert first["pending"] == [("ktrader", "req-01")]
    assert first["remaining"] == 2
    second = recover_registered(tmp_path, allowed_consumers=POLICY,
                                observed_at_utc=NOW, max_items=1,
                                after_key=first["next_cursor"])
    assert second["pending"] == [("ktrader", "req-02")]
    third = recover_registered(tmp_path, allowed_consumers=POLICY,
                               observed_at_utc=NOW, max_items=1,
                               after_key=second["next_cursor"])
    assert third["pending"] == [("ktrader", "req-03")]
    wrapped = recover_registered(tmp_path, allowed_consumers=POLICY,
                                 observed_at_utc=NOW, max_items=1,
                                 after_key=third["next_cursor"])
    assert wrapped["pending"] == [("ktrader", "req-01")]


def test_cursor_invalid_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="cursor"):
        recovery_pass(tmp_path, allowed_consumers=POLICY,
                      observed_at_utc=NOW, after_key="req-01")
