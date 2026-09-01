from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.local_language_discovery_pack import (
    INITIAL_LANGUAGE_SLICE,
    LANGUAGE_SLICE_GAP_STATEMENT,
    LOCAL_LANGUAGE_DISCOVERY_PACK_VERSION,
    build_governed_local_language_collector,
    build_local_language_adapter,
    build_local_language_adapters,
    install_local_language_governance,
    local_language_by_id,
    local_language_specs,
)
from kgeopolitical_monitor.operational_monitoring import MonitoringWatch, OperationalMonitoringRuntime
from kgeopolitical_monitor.source_portfolio import SourcePortfolioService


NOW = datetime(2026, 9, 1, 16, 0, tzinfo=timezone.utc)
FIXTURES = Path(__file__).parent / "fixtures" / "p12_4"


class LocalLanguageFixtureTransport:
    def __init__(self, *, fail_host=None):
        self.fail_host = fail_host
        self.urls = []

    def get(self, url, *, headers=None):
        self.urls.append(url)
        if self.fail_host and self.fail_host in url:
            raise RuntimeError(f"fixture failure for {self.fail_host}")
        if "pravda.com.ua" in url:
            fixture = "uk.rss.xml"
        elif "meduza.io" in url:
            fixture = "ru.rss.xml"
        elif "rmf24.pl" in url:
            fixture = "pl.rss.xml"
        elif "haberturk.com" in url:
            fixture = "tr.rss.xml"
        else:
            raise AssertionError(f"unexpected fixture URL: {url}")
        return HttpResponse(
            body=(FIXTURES / fixture).read_bytes(),
            content_type="application/rss+xml",
        )


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "P12.4 broad discovery",
        "Ukraine",
        60,
        watch_id="watch-p124",
        created_at=NOW,
    )
    return runtime


def test_pack_has_exact_initial_language_slice_and_public_free_sources():
    specs = local_language_specs()
    assert LOCAL_LANGUAGE_DISCOVERY_PACK_VERSION == "P12.4-1.0"
    assert tuple(sorted(spec.content_language for spec in specs)) == INITIAL_LANGUAGE_SLICE
    assert len(specs) == 4
    assert len({spec.source_id for spec in specs}) == 4
    assert len({spec.publisher_name for spec in specs}) == 4
    assert all(spec.feed_url.startswith("https://") for spec in specs)
    assert all(spec.access_mode == "PUBLIC_ANONYMOUS" for spec in specs)
    assert all(spec.cost_mode == "FREE" for spec in specs)
    assert all(spec.data_classification == "PUBLIC" for spec in specs)
    assert all(spec.source_role == "MEDIA" for spec in specs)


def test_pack_has_native_query_terms_and_explicit_non_global_gap():
    by_id = local_language_by_id()
    assert by_id["ukrainska-pravda-uk"].native_query_term == "Україна"
    assert by_id["meduza-ru"].native_query_term == "Украина"
    assert by_id["rmf24-pl"].native_query_term == "Ukraina"
    assert by_id["haberturk-tr"].native_query_term == "Ukrayna"
    assert "only uk/ru/pl/tr" in LANGUAGE_SLICE_GAP_STATEMENT
    assert "GLOBAL is not implied" in LANGUAGE_SLICE_GAP_STATEMENT


def test_pack_preserves_translation_and_origin_boundaries():
    for spec in local_language_specs():
        assert spec.creates_translation is False
        assert spec.establishes_independence is False
        assert spec.changes_verification_state is False
        assert spec.changes_coverage_confidence is False
        assert "underlying origin" in spec.origin_characteristics
        assert "not independent-origin credit" in spec.independence_constraints


def test_adapters_preserve_original_unicode_and_language_metadata():
    transport = LocalLanguageFixtureTransport()
    expected_titles = {
        "uk": "Україна посилює дипломатичну координацію",
        "ru": "Украина обсуждает новые меры безопасности",
        "pl": "Ukraina omawia nowe działania dyplomatyczne",
        "tr": "Ukrayna yeni diplomatik adımları değerlendiriyor",
    }
    for spec in local_language_specs():
        adapter = build_local_language_adapter(
            transport,
            spec,
            max_entries=10,
            query_filter=True,
        )
        watch = MonitoringWatch(
            watch_id=f"native-{spec.content_language}",
            name=f"native {spec.content_language}",
            query=spec.native_query_term,
            cadence_minutes=60,
            created_at=NOW,
        )
        items = adapter.fetch(watch, NOW)
        assert len(items) == 1
        item = items[0]
        assert item.title == expected_titles[spec.content_language]
        assert item.metadata["content_language"] == spec.content_language
        assert item.metadata["native_query_term"] == spec.native_query_term
        assert item.metadata["translation_state"] == "ORIGINAL_NOT_TRANSLATED"
        assert item.metadata["discovery_role"] == "MEDIA"
        assert item.metadata["region_scope"] == list(spec.region_scope)


def test_broad_discovery_adapters_do_not_depend_on_english_watch_equivalence():
    transport = LocalLanguageFixtureTransport()
    adapters = build_local_language_adapters(transport, max_entries=10)
    watch = MonitoringWatch(
        watch_id="english-watch",
        name="English watch",
        query="Ukraine security",
        cadence_minutes=60,
        created_at=NOW,
    )
    assert [len(adapter.fetch(watch, NOW)) for adapter in adapters] == [1, 1, 1, 1]


def test_governance_install_is_approved_free_idempotent_and_language_scoped(tmp_path):
    runtime = _runtime(tmp_path)
    first = install_local_language_governance(runtime, reviewed_at=NOW)
    second = install_local_language_governance(runtime, reviewed_at=NOW)

    assert len(first) == 4
    assert [record.portfolio_entry_id for record in first] == [
        record.portfolio_entry_id for record in second
    ]
    assert all(record.review_status == "APPROVED" for record in first)
    assert all(record.cost_mode == "FREE" for record in first)
    assert all(record.paid_provider_approved is False for record in first)
    assert {record.language_scope[0] for record in first} == set(INITIAL_LANGUAGE_SLICE)


def test_governance_drift_fails_closed(tmp_path):
    runtime = _runtime(tmp_path)
    install_local_language_governance(runtime, reviewed_at=NOW)
    service = SourcePortfolioService(runtime)
    spec = local_language_specs()[0]

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
        adapter_id="manual-drift",
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
        install_local_language_governance(runtime, reviewed_at=NOW)


def test_pack_requires_explicit_governance_before_collection(tmp_path):
    runtime = _runtime(tmp_path)
    with pytest.raises(RuntimeError, match="no source-portfolio record"):
        build_governed_local_language_collector(runtime, LocalLanguageFixtureTransport())


def test_broad_discovery_collection_is_deterministic(tmp_path):
    runtime = _runtime(tmp_path)
    install_local_language_governance(runtime, reviewed_at=NOW)
    collector = build_governed_local_language_collector(
        runtime,
        LocalLanguageFixtureTransport(),
        max_entries=10,
    )

    report = collector.collect("watch-p124", NOW)
    assert report.status == "COMPLETED"
    assert report.source_success_count == 4
    assert report.source_failure_count == 0
    assert report.item_count == 4
    attempts = collector.audit.attempts(report.collection_id)
    assert len(attempts) == 4
    assert all(attempt.status == "SUCCESS" for attempt in attempts)


def test_source_failure_is_visible_and_isolated(tmp_path):
    runtime = _runtime(tmp_path)
    install_local_language_governance(runtime, reviewed_at=NOW)
    collector = build_governed_local_language_collector(
        runtime,
        LocalLanguageFixtureTransport(fail_host="meduza.io"),
        max_entries=10,
    )

    report = collector.collect("watch-p124", NOW)
    assert report.status == "PARTIAL"
    assert report.source_success_count == 3
    assert report.source_failure_count == 1
    assert report.item_count == 3
    attempts = {attempt.source_id: attempt for attempt in collector.audit.attempts(report.collection_id)}
    assert attempts["meduza-ru"].status == "FAILED"
    assert "fixture failure" in attempts["meduza-ru"].error
    assert sum(attempt.status == "SUCCESS" for attempt in attempts.values()) == 3
