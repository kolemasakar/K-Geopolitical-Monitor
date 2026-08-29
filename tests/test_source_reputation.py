from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_reputation import SourceReputationService


NOW = datetime(2026, 8, 29, 10, 0, tzinfo=timezone.utc)


class StaticAdapter:
    def __init__(self, source_id, url, reliability="official"):
        self.source_id = source_id
        self.source_name = source_id
        self.source_class = "Official sources"
        self.reliability = reliability
        self.url = url

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=f"item-{self.source_id}",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Shared event",
                summary="Shared event summary",
                original_url=self.url,
                collected_at=collected_at,
                reliability=self.reliability,
            )
        ]


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Reputation test",
        "shared event",
        60,
        watch_id="watch-reputation",
        created_at=NOW,
    )
    return runtime


def _collect(runtime, adapters):
    return LiveSourceCollector(runtime, adapters).collect("watch-reputation", NOW)


def test_source_reputation_history_is_append_only_and_current_is_latest(tmp_path):
    runtime = _runtime(tmp_path)
    _collect(runtime, [StaticAdapter("source-a", "https://a.example/story")])
    service = SourceReputationService(runtime)

    first = service.record_assessment(
        "source-a",
        status="ACTIVE",
        reliability_rating="MEDIUM",
        reason="Initial controlled assessment",
        evidence_refs=("review:1", "review:1", "sample:alpha"),
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
        review_due_at=NOW + timedelta(days=30),
    )
    second = service.record_assessment(
        "source-a",
        status="WATCH",
        reliability_rating="LOW",
        reason="Accuracy drift requires monitoring",
        evidence_refs=("review:2",),
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW + timedelta(days=1),
    )

    assert first.assessment_version == 1
    assert first.evidence_refs == ("review:1", "sample:alpha")
    assert second.assessment_version == 2
    assert second.supersedes_assessment_id == first.assessment_id
    assert service.history("source-a") == (first, second)
    assert service.current("source-a") == second
    assert service.current_all() == (second,)


def test_compromised_is_not_false_and_restoration_preserves_history(tmp_path):
    runtime = _runtime(tmp_path)
    _collect(runtime, [StaticAdapter("source-a", "https://a.example/story")])
    service = SourceReputationService(runtime)

    compromised = service.record_assessment(
        "source-a",
        status="COMPROMISED",
        reliability_rating="LOW",
        reason="Repeated documented false or manipulated publications",
        evidence_refs=("case:fake-1", "case:fake-2"),
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
    )
    restored = service.record_assessment(
        "source-a",
        status="RESTORED",
        reliability_rating="MEDIUM",
        reason="Sustained improved accuracy and correction behavior",
        evidence_refs=("review:restoration",),
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW + timedelta(days=90),
        restoration_of_assessment_id=compromised.assessment_id,
    )

    assert compromised.automatically_false is False
    assert compromised.changes_claim_truth is False
    assert compromised.changes_independent_origin_count is False
    assert compromised.can_describe_claim_or_narrative is True
    assert restored.restoration_of_assessment_id == compromised.assessment_id
    assert tuple(record.status for record in service.history("source-a")) == (
        "COMPROMISED",
        "RESTORED",
    )
    assert service.current("source-a") == restored


def test_restored_requires_same_source_adverse_assessment(tmp_path):
    runtime = _runtime(tmp_path)
    _collect(
        runtime,
        [
            StaticAdapter("source-a", "https://a.example/story"),
            StaticAdapter("source-b", "https://b.example/story"),
        ],
    )
    service = SourceReputationService(runtime)

    active = service.record_assessment(
        "source-a",
        status="ACTIVE",
        reliability_rating="MEDIUM",
        reason="Normal operation",
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
    )
    compromised_b = service.record_assessment(
        "source-b",
        status="COMPROMISED",
        reliability_rating="LOW",
        reason="Repeated false publications",
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
    )

    with pytest.raises(ValueError, match="adverse"):
        service.record_assessment(
            "source-a",
            status="RESTORED",
            reliability_rating="MEDIUM",
            reason="Invalid restoration",
            policy_name="KGM_SOURCE_REPUTATION",
            policy_version="1",
            assessed_at=NOW + timedelta(days=1),
            restoration_of_assessment_id=active.assessment_id,
        )

    with pytest.raises(ValueError, match="another source"):
        service.record_assessment(
            "source-a",
            status="RESTORED",
            reliability_rating="MEDIUM",
            reason="Invalid cross-source restoration",
            policy_name="KGM_SOURCE_REPUTATION",
            policy_version="1",
            assessed_at=NOW + timedelta(days=1),
            restoration_of_assessment_id=compromised_b.assessment_id,
        )


def test_reputation_layer_does_not_rewrite_legacy_source_reliability(tmp_path):
    runtime = _runtime(tmp_path)
    _collect(
        runtime,
        [StaticAdapter("source-a", "https://a.example/story", reliability="official")],
    )
    service = SourceReputationService(runtime)
    service.record_assessment(
        "source-a",
        status="COMPROMISED",
        reliability_rating="LOW",
        reason="Separate reputation assessment",
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
    )

    with sqlite3.connect(runtime.database_path) as connection:
        legacy = connection.execute(
            "SELECT reliability FROM sources WHERE id = 'source-a'"
        ).fetchone()[0]

    assert legacy == "official"


def test_source_reputation_does_not_change_m8_verification_or_origin_count(tmp_path):
    runtime = _runtime(tmp_path)
    collection = _collect(
        runtime,
        [
            StaticAdapter("source-a", "https://origin-a.example/story"),
            StaticAdapter("source-b", "https://origin-b.example/story"),
        ],
    )
    processor = LiveEndToEndProcessor(runtime)
    before = processor.process_collection(collection.collection_id, processed_at=NOW)

    reputation = SourceReputationService(runtime).record_assessment(
        "source-a",
        status="COMPROMISED",
        reliability_rating="LOW",
        reason="Reputation metadata must not mutate evidence truth",
        evidence_refs=("review:source-a",),
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
    )
    after = processor.process_collection(collection.collection_id, processed_at=NOW)

    assert reputation.changes_claim_truth is False
    assert after.claims == before.claims
    assert len(after.claims) == 1
    assert after.claims[0].independent_origins == (
        "origin-a.example",
        "origin-b.example",
    )


def test_reputation_history_survives_runtime_restart(tmp_path):
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Reputation test",
        "shared event",
        60,
        watch_id="watch-reputation",
        created_at=NOW,
    )
    _collect(runtime, [StaticAdapter("source-a", "https://a.example/story")])
    created = SourceReputationService(runtime).record_assessment(
        "source-a",
        status="WATCH",
        reliability_rating="LOW",
        reason="Review after source drift",
        evidence_refs=("review:drift",),
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
    )

    restarted = OperationalMonitoringRuntime(project_root)
    reloaded = SourceReputationService(restarted).current("source-a")

    assert reloaded == created
    assert restarted.database_path == runtime.database_path


def test_unknown_source_and_invalid_review_time_fail_closed(tmp_path):
    runtime = _runtime(tmp_path)
    service = SourceReputationService(runtime)

    with pytest.raises(ValueError, match="source does not exist"):
        service.record_assessment(
            "missing-source",
            status="ACTIVE",
            reliability_rating="UNKNOWN",
            reason="No such source",
            policy_name="KGM_SOURCE_REPUTATION",
            policy_version="1",
            assessed_at=NOW,
        )

    _collect(runtime, [StaticAdapter("source-a", "https://a.example/story")])
    with pytest.raises(ValueError, match="reviewed_at"):
        service.record_assessment(
            "source-a",
            status="ACTIVE",
            reliability_rating="MEDIUM",
            reason="Invalid review clock",
            policy_name="KGM_SOURCE_REPUTATION",
            policy_version="1",
            assessed_at=NOW,
            reviewed_at=NOW - timedelta(seconds=1),
        )
