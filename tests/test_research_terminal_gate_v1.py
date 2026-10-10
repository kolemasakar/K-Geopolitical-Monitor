"""Canonical lifecycle must not bypass typed immutable completion."""
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, advance, recovery_snapshot
from test_research_request_v1 import sample

POLICY = {"ktrader": "review-v1"}


@pytest.mark.parametrize("terminal", ["COMPLETE", "PARTIAL"])
def test_direct_success_terminal_is_denied(tmp_path, terminal):
    req = sample()
    admit(tmp_path, req, allowed_consumers=POLICY)
    advance(tmp_path, "ktrader", "req-01", "ACCEPTED",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:01:00Z")
    advance(tmp_path, "ktrader", "req-01", "PROCESSING",
            allowed_consumers=POLICY, at_utc="2026-09-28T12:02:00Z")
    with pytest.raises(ValueError, match="typed terminal completion required"):
        advance(tmp_path, "ktrader", "req-01", terminal,
                allowed_consumers=POLICY, at_utc="2026-09-28T12:03:00Z")
    assert recovery_snapshot(tmp_path, allowed_consumers=POLICY)[0]["status"] == "PROCESSING"
