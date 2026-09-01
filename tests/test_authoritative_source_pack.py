from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.authoritative_source_pack import (
    AUTHORITATIVE_SOURCE_PACK_VERSION,
    build_governed_source_pack_collector,
    build_source_pack_adapters,
    install_source_pack_governance,
    source_pack_by_id,
    source_pack_specs,
)
from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_portfolio import SourcePortfolioService


NOW = datetime(2026, 9, 1, 15, 30, tzinfo=timezone.utc)
FIXTURES = Path(__file__).parent / "fixtures" / "p12_3"


class PackFixtureTransport:
    def __init__(self, *, fail_host=None):
        self.fail_host = fail_host
        self.urls = []

    def get(self, url, *, headers=None):
        self.urls.append(url)
        if self.fail_host and self.fail_host in url:
            raise RuntimeError(f"fixture failure for {self.fail_host}")
        if "gov.uk" in url:
            return HttpResponse(
                body=(FIXTURES / "authoritative.atom.xml").read_bytes(),
                content_type="application/atom+xml",
            )
        return HttpResponse(
            body=(FIXTURES / "authoritative.rss.xml").read_bytes(),
            content_type="application/rss+xml",
        )


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "P12.3 watch",
        "Ukraine security",
        60,
        watch_id="watch-p123",
        created_at=NOW,
    )
    return runtime


def test_pack_is_materially_broader_public_free_and_unique():
    specs = source_pack_specs()
    assert AUTHORITATIVE_SOURCE_PACK_VERSION == "P12.3-1.1"
    assert len(specs) == 4
    assert len({spec.source_id for spec in specs}) == 4
    assert len({spec.publisher_name for spec in specs}) == 4
    assert all(spec.feed_url.startswith("https://") for spec in specs)
    assert all(spec.access_mode == "PUBLIC_ANONYMOUS" for spec in specs)
    assert all(spec.cost_mode == "FREE" for spec in specs)
    assert all(spec.data_classification == "PUBLIC" for spec in specs)
    assert all(spec.availability_state in {"ACTIVE", "DEGRADED"} for spec in specs)


def test_pack_contains_priority_institutions_and_explicit_origin_boundary():
    by_id = source_pack_by_id()
    assert set(by_id) == {
        "eu-commission-press-corner",
        "eu-parliament-press-releases",
        "uk-government-news-communications",
        "osce-latest-news",
    }
    assert by_id["osce-latest-news"].publisher_name.startswith("Organization for Security")
    assert by_id["eu-parliament-press-releases"].availability_state == "DEGRADED"
    assert {
        spec.source_id
        for spec in by_id.values()
        if spec.availability_state == "ACTIVE"
    } == {
        "eu-commission-press-corner",
        "uk-government-news-communications",
        "osce-latest-news",
    }
    for spec in by_id.values():
        assert spec.establishes_independence is False
        assert spec.changes_verification_state is False
        assert spec.changes_coverage_confidence is False
        assert "not independent-origin credit" in spec.independence_constraints


def test_pack_adapters_match_specs_deterministically():
    transport = PackFixtureTransport()
    specs = source_pack_specs()
    adapters = build_source_pack_adapters(transport, max_entries=25)
    assert len(adapters) == len(specs)
    for spec, adapter in zip(specs, adapters, strict=True):
        assert adapter.source_id == spec.source_id
        assert adapter.source_name == spec.source_name
        assert adapter.source_class == spec.source_class
        assert adapter.adapter_id == spec.adapter_id
        assert adapter.adapter_version == spec.adapter_version
        assert adapter.request_base_url == spec.feed_url


def test_governance_install_is_explicit_approved_free_and_idempotent(tmp_path):
    runtime = _runtime(tmp_path)
    first = install_source_pack_governance(runtime, reviewed_at=NOW)
    second = install_source_pack_governance(runtime, reviewed_at=NOW)

    assert len(first) == 4
    assert [record.portfolio_entry_id for record in first] == [
        record.portfolio_entry_id for record in second
    ]
    assert all(record.portfolio_version == 1 for record in first)
    assert all(record.review_status == "APPROVED" for record in first)
    assert {record.source_id: record.availability_state for record in first} == {
        spec.source_id: spec.availability_state for spec in source_pack_specs()
    }
    assert all(record.cost_mode == "FREE" for record in first)
    assert all(record.paid_provider_approved is False for record in first)


def test_governance_install_creates_no_parallel_source_identity(tmp_path):
    runtime = _runtime(tmp_path)
    install_source_pack_governance(runtime, reviewed_at=NOW)
    service = SourcePortfolioService(runtime)

    for spec in source_pack_specs():
        current = service.current(spec.source_id)
        assert current is not None
        assert current.source_name == spec.source_name
        assert current.publisher_name == spec.publisher_name
        assert current.adapter_id == spec.adapter_id
        assert current.outbound_domains == (spec.outbound_domain,)
        assert current.availability_state == spec.availability_state
        assert current.activates_collection is False
        assert current.establishes_independence is False
        assert current.changes_verification_state is False
        assert current.changes_coverage_confidence is False


def test_governance_drift_fails_closed_instead_of_silent_supersession(tmp_path):
    runtime = _runtime(tmp_path)
    install_source_pack_governance(runtime, reviewed_at=NOW)
    service = SourcePortfolioService(runtime)
    spec = source_pack_specs()[0]

    service.record_version(
        spec.source_id,
        source_name=spec.source_name,
        publisher_name=spec.publisher_name,
        source_class=spec.source_class,
        source_role=spec.source_role,
        region_scope=spec.region_scope,
        language_scope=spec.language_scope,
        access_mode="PUBLIC_ANONYMOUS",
        cost_mode="FREE",
        authentication_mode="NONE",
        expected_freshness_minutes=spec.expected_freshness_minutes,
        collection_cadence_minutes=spec.collection_cadence_minutes,
        adapter_id="manually-changed-adapter",
        adapter_version=spec.adapter_version,
        outbound_domains=(spec.outbound_domain,),
        outbound_protocols=("HTTPS",),
        availability_state=spec.availability_state,
        data_classification="PUBLIC",
        origin_characteristics=spec.origin_characteristics,
        independence_constraints=spec.independence_constraints,
        terms_notes=spec.terms_notes,
        owner="KGM owner",
        reviewer="KGM owner",
        review_status="APPROVED",
        reviewed_at=NOW,
        created_at=NOW,
    )

    with pytest.raises(RuntimeError, match="portfolio drift requires explicit review"):
        install_source_pack_governance(runtime, reviewed_at=NOW)


def test_pack_requires_explicit_governance_before_collector(tmp_path):
    runtime = _runtime(tmp_path)
    with pytest.raises(RuntimeError, match="no source-portfolio record"):
        build_governed_source_pack_collector(runtime, PackFixtureTransport())


def test_pack_collects_deterministic_rss_and_atom_fixtures(tmp_path):
    runtime = _runtime(tmp_path)
    install_source_pack_governance(runtime, reviewed_at=NOW)
    transport = PackFixtureTransport()
    collector = build_governed_source_pack_collector(runtime, transport, max_entries=10)

    report = collector.collect("watch-p123", NOW)
    assert report.status == "COMPLETED"
    assert report.source_success_count == 4
    assert report.source_failure_count == 0
    assert report.item_count == 4
    attempts = collector.audit.attempts(report.collection_id)
    assert len(attempts) == 4
    assert all(attempt.status == "SUCCESS" for attempt in attempts)


def test_source_specific_failure_is_visible_and_isolated(tmp_path):
    runtime = _runtime(tmp_path)
    install_source_pack_governance(runtime, reviewed_at=NOW)
    collector = build_governed_source_pack_collector(
        runtime,
        PackFixtureTransport(fail_host="feeds.osce.org"),
        max_entries=10,
    )

    report = collector.collect("watch-p123", NOW)
    assert report.status == "PARTIAL"
    assert report.source_success_count == 3
    assert report.source_failure_count == 1
    assert report.item_count == 3
    attempts = {attempt.source_id: attempt for attempt in collector.audit.attempts(report.collection_id)}
    assert attempts["osce-latest-news"].status == "FAILED"
    assert "fixture failure" in attempts["osce-latest-news"].error
    assert sum(attempt.status == "SUCCESS" for attempt in attempts.values()) == 3


def test_same_fixture_publication_urls_do_not_imply_shared_or_independent_origin(tmp_path):
    runtime = _runtime(tmp_path)
    install_source_pack_governance(runtime, reviewed_at=NOW)
    collector = build_governed_source_pack_collector(runtime, PackFixtureTransport())
    report = collector.collect("watch-p123", NOW)

    assert report.item_count == 4
    service = SourcePortfolioService(runtime)
    assert all(
        service.current(spec.source_id).establishes_independence is False
        for spec in source_pack_specs()
    )
