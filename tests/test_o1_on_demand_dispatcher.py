from datetime import datetime, timezone

import pytest

from kgeopolitical_monitor.on_demand_dispatcher import (
    OnDemandRequest, dispatch_offline_once,
)
from kgeopolitical_monitor.live_sources import LiveSourceItem


NOW = datetime(2026, 10, 25, 21, 0, tzinfo=timezone.utc)


class FixtureSource:
    offline_fixture_only = True
    source_class = "Official sources"

    def __init__(self, source_id, fail=False):
        self.source_id = source_id
        self.source_name = source_id
        self.fail = fail
        self.calls = 0

    def fetch(self, watch, collected_at):
        self.calls += 1
        if self.fail:
            raise ValueError("synthetic unavailable")
        return [LiveSourceItem(
            item_id="id-" + self.source_id,
            source_id=self.source_id,
            source_name=self.source_name,
            source_class=self.source_class,
            title="Synthetic event",
            summary="Synthetic event for offline verification",
            original_url="https://" + self.source_id + ".example/one",
            collected_at=collected_at,
            reliability="official",
        )]


def test_dispatcher_two_source_e2e_single_invocation(tmp_path, monkeypatch):
    sources = [FixtureSource("agency-a"), FixtureSource("agency-b")]
    out = dispatch_offline_once(OnDemandRequest("synthetic", NOW, "fixture01"), adapters=sources)
    assert out.request_id == "fixture01"
    assert out.status == "COMPLETED"
    assert out.collection_status == "COMPLETED"
    assert out.source_success_count == 2
    assert out.distinct_source_id_count == 2
    assert out.evidence_count == 2
    assert out.finding_count >= 1
    assert out.ephemeral_workspace_removed
    assert all(s.calls == 1 for s in sources)


def test_dispatcher_partial_failure():
    out = dispatch_offline_once(
        OnDemandRequest("synthetic", NOW),
        adapters=[FixtureSource("agency-a"), FixtureSource("agency-b", fail=True)],
    )
    assert out.status == "COMPLETED"
    assert out.collection_status == "PARTIAL"
    assert out.source_failure_count == 1
    assert out.distinct_source_id_count == 1


def test_dispatcher_total_failure_is_fail_closed():
    out = dispatch_offline_once(
        OnDemandRequest("synthetic", NOW),
        adapters=[FixtureSource("agency-a", True), FixtureSource("agency-b", True)],
    )
    assert out.status == "FAILED"
    assert out.collection_status == "FAILED"
    assert out.finding_count == 0
    assert out.evidence_count == 0


def test_dispatcher_does_not_accept_live_adapter():
    source = FixtureSource("agency-a")
    source.offline_fixture_only = False
    with pytest.raises(ValueError, match="forbidden"):
        dispatch_offline_once(OnDemandRequest("synthetic", NOW), adapters=[source])
    assert source.calls == 0


@pytest.mark.parametrize("text", ["", "x" * 257, "line\nreturn"])
def test_dispatcher_rejects_invalid_input(text):
    with pytest.raises(ValueError):
        OnDemandRequest(text, NOW)
