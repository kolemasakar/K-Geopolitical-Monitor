from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.p22_3_b1_source_pack import (
    B1_REPOSITORY_ACTIVE_SOURCE_IDS,
    build_b1_adapters,
    install_b1_governance,
)
from kgeopolitical_monitor.source_portfolio import SourcePortfolioService
from kgeopolitical_monitor.adapter_framework import validate_portfolio_for_adapter

NOW = datetime(2026, 9, 19, 15, 30, tzinfo=timezone.utc)
FIX = Path(__file__).parent / "fixtures" / "p22_3_b1"


class FixtureTransport:
    def get(self, url, *, headers=None):
        if "ofac.treasury.gov" in url:
            name, ctype = "ofac.html", "text/html"
        elif "whitehouse.gov" in url:
            name, ctype = "white-house.html", "text/html"
        elif "sanctionslist.fcdo.gov.uk" in url:
            name, ctype = "uk-sanctions.csv", "text/csv"
        else:
            name, ctype = "russian-government.html", "text/html"
        return HttpResponse(body=(FIX / name).read_bytes(), content_type=ctype)


def runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def test_b1_repository_activation_is_exactly_the_two_health_pass_sources(tmp_path):
    assert B1_REPOSITORY_ACTIVE_SOURCE_IDS == (
        "ofac-recent-actions-en",
        "white-house-briefings-en",
    )
    r = runtime(tmp_path)
    first = install_b1_governance(r, reviewed_at=NOW)
    second = install_b1_governance(r, reviewed_at=NOW)
    assert [x.source_id for x in first] == list(B1_REPOSITORY_ACTIVE_SOURCE_IDS)
    assert [x.portfolio_entry_id for x in first] == [x.portfolio_entry_id for x in second]
    assert all(x.availability_state == "ACTIVE" for x in first)
    assert all(x.access_mode == "PUBLIC_ANONYMOUS" and x.cost_mode == "FREE" for x in first)
    assert all(x.authentication_mode == "NONE" and x.data_classification == "PUBLIC" for x in first)
    assert all(x.review_status == "APPROVED" and x.paid_provider_approved is False for x in first)
    assert all(x.establishes_independence is False and x.changes_verification_state is False for x in first)


def test_b1_blocked_sources_cannot_be_repository_activated(tmp_path):
    r = runtime(tmp_path)
    for source_id in ("uk-sanctions-list-en", "russian-government-news-ru"):
        with pytest.raises(ValueError, match="not approved for repository activation"):
            install_b1_governance(r, reviewed_at=NOW, enabled_source_ids=[source_id])
    svc = SourcePortfolioService(r)
    assert svc.current("uk-sanctions-list-en") is None
    assert svc.current("russian-government-news-ru") is None


def test_b1_active_portfolio_records_match_their_adapters(tmp_path):
    r = runtime(tmp_path)
    records = {x.source_id: x for x in install_b1_governance(r, reviewed_at=NOW)}
    adapters = build_b1_adapters(FixtureTransport(), enabled_source_ids=B1_REPOSITORY_ACTIVE_SOURCE_IDS)
    for adapter in adapters:
        validate_portfolio_for_adapter(records[adapter.source_id], adapter)
