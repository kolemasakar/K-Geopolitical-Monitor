import sqlite3
from datetime import datetime, timezone

from kgeopolitical_monitor.live_end_to_end import (
    DETECTED,
    PARTLY_VERIFIED,
    LiveEndToEndProcessor,
    normalize_claim_title,
)
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


NOW = datetime(2026, 8, 26, 11, 30, tzinfo=timezone.utc)


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-e2e",
        created_at=NOW,
    )
    return runtime


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


def test_claim_title_normalization_is_strict_and_deterministic():
    assert normalize_claim_title("Ukraine: Security Agreement") == "ukraine security agreement"
    assert normalize_claim_title("UKRAINE security agreement") == "ukraine security agreement"
    assert normalize_claim_title("Ukraine security agreement signed") != "ukraine security agreement"


def test_same_original_origin_does_not_inflate_independence(tmp_path):
    runtime = _runtime(tmp_path)
    official = StaticAdapter(
        "consilium-test",
        "Consilium",
        "Official sources",
        "official",
        [
            {
                "item_id": "official-1",
                "title": "Ukraine security agreement",
                "url": "https://www.consilium.europa.eu/en/press/agreement/",
            }
        ],
    )
    discovery = StaticAdapter(
        "gdelt-test",
        "GDELT",
        "Structured data",
        "discovery-only",
        [
            {
                "item_id": "gdelt-1",
                "title": "Ukraine: security agreement",
                "url": "https://www.consilium.europa.eu/en/press/agreement/",
            }
        ],
    )
    report = LiveSourceCollector(runtime, [official, discovery]).collect("watch-e2e", NOW)

    result = LiveEndToEndProcessor(runtime).process_collection(
        report.collection_id,
        processed_at=NOW,
    )

    assert len(result.claims) == 1
    claim = result.claims[0]
    assert claim.verification_status == DETECTED
    assert claim.independent_origins == ("consilium.europa.eu",)
    assert len(claim.raw_item_ids) == 2
    assert claim.confidence == 0.92
    assert result.findings[0].evidence_refs[0] == f"claim:{claim.claim_id}"
    assert "independent_origins=1" in result.findings[0].explanation


def test_two_original_origins_reach_partly_verified(tmp_path):
    runtime = _runtime(tmp_path)
    official = StaticAdapter(
        "official-a",
        "Official A",
        "Official sources",
        "official",
        [
            {
                "item_id": "origin-a",
                "title": "Ukraine security agreement",
                "url": "https://official.example/statement",
            }
        ],
    )
    media = StaticAdapter(
        "media-b",
        "Media B",
        "International media",
        "medium",
        [
            {
                "item_id": "origin-b",
                "title": "Ukraine security agreement",
                "url": "https://media.example/report",
            }
        ],
    )
    report = LiveSourceCollector(runtime, [official, media]).collect("watch-e2e", NOW)

    result = LiveEndToEndProcessor(runtime).process_collection(
        report.collection_id,
        processed_at=NOW,
    )

    assert len(result.claims) == 1
    claim = result.claims[0]
    assert claim.verification_status == PARTLY_VERIFIED
    assert claim.independent_origins == ("media.example", "official.example")
    assert claim.confidence == 1.0
    assert result.findings[0].confidence == 1.0
    assert "verification_status=PARTLY_VERIFIED" in result.findings[0].explanation


def test_strict_grouping_does_not_fuzzy_merge_distinct_titles(tmp_path):
    runtime = _runtime(tmp_path)
    source = StaticAdapter(
        "source-a",
        "Source A",
        "Official sources",
        "official",
        [
            {
                "item_id": "item-a",
                "title": "Ukraine security agreement",
                "url": "https://a.example/one",
            },
            {
                "item_id": "item-b",
                "title": "Ukraine security agreement signed",
                "url": "https://a.example/two",
            },
        ],
    )
    report = LiveSourceCollector(runtime, [source]).collect("watch-e2e", NOW)

    result = LiveEndToEndProcessor(runtime).process_collection(
        report.collection_id,
        processed_at=NOW,
    )

    assert len(result.claims) == 2
    assert {claim.verification_status for claim in result.claims} == {DETECTED}


def test_reprocessing_same_collection_is_idempotent(tmp_path):
    runtime = _runtime(tmp_path)
    source = StaticAdapter(
        "source-a",
        "Source A",
        "Official sources",
        "official",
        [
            {
                "item_id": "item-a",
                "title": "Ukraine security agreement",
                "url": "https://a.example/one",
            }
        ],
    )
    report = LiveSourceCollector(runtime, [source]).collect("watch-e2e", NOW)
    processor = LiveEndToEndProcessor(runtime)

    first = processor.process_collection(report.collection_id, processed_at=NOW)
    second = processor.process_collection(report.collection_id, processed_at=NOW)

    assert second.analysis_run_id == first.analysis_run_id
    assert second.monitoring_run_id == first.monitoring_run_id
    assert [claim.claim_id for claim in second.claims] == [claim.claim_id for claim in first.claims]
    assert [finding.finding_id for finding in second.findings] == [
        finding.finding_id for finding in first.findings
    ]

    with sqlite3.connect(runtime.database_path) as connection:
        analysis_count = connection.execute(
            "SELECT COUNT(*) FROM live_analysis_runs WHERE collection_id = ?",
            (report.collection_id,),
        ).fetchone()[0]
        run_count = connection.execute(
            "SELECT COUNT(*) FROM monitoring_runs WHERE run_id = ?",
            (first.monitoring_run_id,),
        ).fetchone()[0]
    assert analysis_count == 1
    assert run_count == 1
