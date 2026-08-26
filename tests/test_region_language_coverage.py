from datetime import datetime, timezone

from kgeopolitical_monitor.live_end_to_end import (
    PARTLY_VERIFIED,
    LiveEndToEndProcessor,
)
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.region_language_coverage import (
    RegionLanguageCoverageService,
    normalize_language_code,
    normalize_region_code,
)


NOW = datetime(2026, 8, 26, 13, 0, tzinfo=timezone.utc)


class StaticAdapter:
    def __init__(self, source_id, source_name, source_class, reliability, items):
        self.source_id = source_id
        self.source_name = source_name
        self.source_class = source_class
        self.reliability = reliability
        self._items = items

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=item["item_id"],
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title=item["title"],
                summary=item.get("summary", item["title"]),
                original_url=item["url"],
                collected_at=collected_at,
                metadata=item.get("metadata", {}),
                reliability=self.reliability,
            )
            for item in self._items
        ]


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Ukraine regional coverage",
        "Ukraine",
        60,
        watch_id="watch-region",
        created_at=NOW,
    )
    return runtime


def _service(runtime):
    service = RegionLanguageCoverageService(runtime)
    service.register_region("ua", "Ukraine", region_group="Europe", created_at=NOW)
    service.register_region("eu", "European Union", region_group="Europe", created_at=NOW)
    service.register_language("uk", "Ukrainian", created_at=NOW)
    service.register_language("en", "English", created_at=NOW)
    return service


def _collect(runtime, watch_id="watch-region", *, suffix="a", two_origins=False):
    adapters = [
        StaticAdapter(
            f"official-{suffix}",
            f"Official {suffix}",
            "Official sources",
            "official",
            [
                {
                    "item_id": f"official-{suffix}",
                    "title": "Ukraine security agreement",
                    "url": f"https://official.example/{suffix}",
                }
            ],
        )
    ]
    if two_origins:
        adapters.append(
            StaticAdapter(
                f"media-{suffix}",
                f"Media {suffix}",
                "International media",
                "medium",
                [
                    {
                        "item_id": f"media-{suffix}",
                        "title": "Ukraine: security agreement",
                        "url": f"https://media.example/{suffix}",
                    }
                ],
            )
        )
    return LiveSourceCollector(runtime, adapters).collect(watch_id, NOW)


def test_region_and_language_codes_are_normalized_and_scope_persists(tmp_path):
    runtime = _runtime(tmp_path)
    service = _service(runtime)

    assert normalize_region_code("middle east") == "MIDDLE_EAST"
    assert normalize_language_code("EN_us") == "en-us"

    scope = service.configure_watch_scope(
        "watch-region",
        [("ua", "uk"), ("EU", "EN"), ("ua", "uk")],
        configured_at=NOW,
    )

    assert [(item.region_code, item.language_code) for item in scope] == [
        ("EU", "en"),
        ("UA", "uk"),
    ]
    assert service.get_region("ua").region_group == "Europe"
    assert service.get_language("EN").language_code == "en"


def test_coverage_report_exposes_missing_then_complete_scope(tmp_path):
    runtime = _runtime(tmp_path)
    service = _service(runtime)
    service.configure_watch_scope(
        "watch-region",
        [("UA", "uk"), ("UA", "en")],
        configured_at=NOW,
    )
    collection = _collect(runtime, suffix="coverage")
    assert collection.item_count == 1

    service.tag_observation(
        "watch-region",
        "official-coverage",
        "UA",
        "uk",
        attribution_type="SOURCE_METADATA",
        confidence=0.95,
        original_language=True,
        tagged_at=NOW,
    )
    partial = service.generate_coverage_report("watch-region", created_at=NOW)

    assert partial.required_scopes == ("UA:en", "UA:uk")
    assert partial.observed_scopes == ("UA:uk",)
    assert partial.missing_scopes == ("UA:en",)
    assert partial.coverage_ratio == 0.5

    service.tag_observation(
        "watch-region",
        "official-coverage",
        "UA",
        "en",
        attribution_type="TRANSLATION",
        confidence=0.8,
        original_language=False,
        tagged_at=NOW,
    )
    complete = service.generate_coverage_report("watch-region", created_at=NOW)

    assert complete.missing_scopes == ()
    assert complete.coverage_ratio == 1.0
    assert complete.observed_regions == ("UA",)
    assert complete.observed_languages == ("en", "uk")


def test_region_language_attribution_does_not_change_m8_verification(tmp_path):
    runtime = _runtime(tmp_path)
    service = _service(runtime)
    service.configure_watch_scope(
        "watch-region",
        [("UA", "uk"), ("EU", "en")],
        configured_at=NOW,
    )
    collection = _collect(runtime, suffix="verify", two_origins=True)
    processor = LiveEndToEndProcessor(runtime)
    before = processor.process_collection(collection.collection_id, processed_at=NOW)

    assert len(before.claims) == 1
    claim_before = before.claims[0]
    assert claim_before.verification_status == PARTLY_VERIFIED

    service.tag_observation(
        "watch-region",
        "official-verify",
        "UA",
        "uk",
        attribution_type="DECLARED",
        confidence=1.0,
        original_language=True,
        tagged_at=NOW,
    )
    service.tag_observation(
        "watch-region",
        "official-verify",
        "EU",
        "en",
        attribution_type="TRANSLATION",
        confidence=1.0,
        original_language=False,
        tagged_at=NOW,
    )
    service.tag_observation(
        "watch-region",
        "media-verify",
        "EU",
        "en",
        attribution_type="SOURCE_METADATA",
        confidence=0.9,
        original_language=True,
        tagged_at=NOW,
    )

    after = processor.process_collection(collection.collection_id, processed_at=NOW)
    claim_after = after.claims[0]

    assert claim_after.claim_id == claim_before.claim_id
    assert claim_after.verification_status == claim_before.verification_status
    assert claim_after.confidence == claim_before.confidence
    assert claim_after.independent_origins == claim_before.independent_origins


def test_watch_scoped_attribution_does_not_leak_between_watches(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    for watch_id in ("watch-a", "watch-b"):
        runtime.create_watch(
            watch_id,
            "Ukraine",
            60,
            watch_id=watch_id,
            created_at=NOW,
        )

    service = _service(runtime)
    service.configure_watch_scope("watch-a", [("UA", "uk")], configured_at=NOW)
    service.configure_watch_scope("watch-b", [("UA", "uk")], configured_at=NOW)

    shared = StaticAdapter(
        "official-shared",
        "Official Shared",
        "Official sources",
        "official",
        [
            {
                "item_id": "shared-item",
                "title": "Ukraine update",
                "url": "https://official.example/shared",
            }
        ],
    )
    LiveSourceCollector(runtime, [shared]).collect("watch-a", NOW)
    LiveSourceCollector(runtime, [shared]).collect("watch-b", NOW)

    service.tag_observation(
        "watch-a",
        "shared-item",
        "UA",
        "uk",
        tagged_at=NOW,
    )

    report_a = service.generate_coverage_report("watch-a", created_at=NOW)
    report_b = service.generate_coverage_report("watch-b", created_at=NOW)

    assert report_a.coverage_ratio == 1.0
    assert report_b.coverage_ratio == 0.0
    assert report_b.missing_scopes == ("UA:uk",)
    assert service.attributions("watch-b") == ()


def test_region_language_state_survives_runtime_restart(tmp_path):
    runtime = _runtime(tmp_path)
    service = _service(runtime)
    service.configure_watch_scope("watch-region", [("UA", "uk")], configured_at=NOW)
    _collect(runtime, suffix="restart")
    attribution = service.tag_observation(
        "watch-region",
        "official-restart",
        "UA",
        "uk",
        confidence=0.9,
        tagged_at=NOW,
    )
    report = service.generate_coverage_report("watch-region", created_at=NOW)

    restarted_runtime = OperationalMonitoringRuntime(tmp_path / "project")
    restarted = RegionLanguageCoverageService(restarted_runtime)

    assert restarted.watch_scope("watch-region") == service.watch_scope("watch-region")
    assert restarted.attributions("watch-region") == (attribution,)
    assert restarted.get_coverage_report(report.report_id) == report
    assert restarted.database_path == runtime.database_path


def test_attribution_fails_closed_for_unknown_scope_or_wrong_watch(tmp_path):
    runtime = _runtime(tmp_path)
    service = _service(runtime)
    _collect(runtime, suffix="guard")

    try:
        service.tag_observation(
            "watch-region",
            "official-guard",
            "UNKNOWN",
            "uk",
            tagged_at=NOW,
        )
    except ValueError as exc:
        assert "unknown region" in str(exc)
    else:
        raise AssertionError("unknown region attribution must fail")

    runtime.create_watch(
        "Other watch",
        "Other",
        60,
        watch_id="watch-other",
        created_at=NOW,
    )
    try:
        service.tag_observation(
            "watch-other",
            "official-guard",
            "UA",
            "uk",
            tagged_at=NOW,
        )
    except ValueError as exc:
        assert str(exc) == "raw item is not associated with watch"
    else:
        raise AssertionError("cross-watch attribution must fail")
