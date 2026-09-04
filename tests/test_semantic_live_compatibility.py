from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.reproducibility import ReproducibilityInstrumentedCollector
from kgeopolitical_monitor.semantic_claims import SemanticClaimService
from kgeopolitical_monitor.semantic_live_compatibility import SemanticLiveCompatibilityService
from kgeopolitical_monitor.semantic_verification import SemanticVerificationService


NOW = datetime(2026, 9, 4, 9, 15, tzinfo=timezone.utc)
QUERY = "Ukraine security compatibility test"


class StaticAdapter:
    adapter_version = "p13.6-test-1.0"

    def __init__(self, source_id, source_name, source_class, reliability, url):
        self.source_id = source_id
        self.source_name = source_name
        self.source_class = source_class
        self.reliability = reliability
        self.url = url

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=f"item-{self.source_id}",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Ukraine security compatibility event",
                summary="Deterministic compatibility fixture",
                original_url=self.url,
                collected_at=collected_at,
                metadata={"language": "en"},
                reliability=self.reliability,
            )
        ]


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "P13.6 compatibility watch",
        QUERY,
        60,
        watch_id="watch-p13-6",
        created_at=NOW,
    )
    return runtime


def _adapters(two=True):
    result = [
        StaticAdapter(
            "official-a",
            "Official A",
            "Official sources",
            "official",
            "https://official.example/statement",
        )
    ]
    if two:
        result.append(
            StaticAdapter(
                "media-b",
                "Media B",
                "International media",
                "medium",
                "https://media.example/report",
            )
        )
    return result


def _legacy_analysis(runtime, *, instrumented=False, two=True):
    base = LiveSourceCollector(runtime, _adapters(two=two))
    collector = ReproducibilityInstrumentedCollector(base) if instrumented else base
    report = collector.collect("watch-p13-6", NOW)
    analysis = LiveEndToEndProcessor(runtime).process_collection(report.collection_id, processed_at=NOW)
    assert len(analysis.claims) == 1
    return report, analysis, analysis.claims[0]


def _semantic_claim(runtime, semantic_id, proposition="The compatibility event occurred"):
    return SemanticClaimService(runtime).record_version(
        semantic_id,
        normalized_proposition=proposition,
        claimant_actor="Actor",
        subject_text="Actor",
        object_theme="compatibility event",
        event_action_type="OCCURRENCE",
        polarity="AFFIRMATIVE",
        modality="ASSERTED",
        time_scope={"date": "2026-09-04"},
        location_scope={"country": "Ukraine"},
        quantity={},
        original_language="en",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.0",
        extraction_confidence=0.95,
        created_at=NOW,
    )


def _link(runtime, semantic_version_id, live_claim_id):
    return SemanticClaimService(runtime).link(
        semantic_version_id,
        target_type="LIVE_ANALYSIS_CLAIM",
        target_id=live_claim_id,
        created_at=NOW,
    )


def _detected_decision(runtime, semantic_version_id):
    verification = SemanticVerificationService(runtime)
    verification.record_policy_version(
        "p13-6-policy",
        policy_name="P13.6 compatibility policy",
        created_at=NOW,
    )
    verification.record_confidence_version(
        semantic_version_id,
        evidence_sufficiency="LOW",
        provenance_independence="UNKNOWN",
        authority_proximity="LOW",
        contradiction_resolution="UNKNOWN",
        temporal_freshness="MEDIUM",
        extraction_certainty="MEDIUM",
        translation_certainty="UNKNOWN",
        claim_specific_certainty="LOW",
        coverage_limitation="LIMITED",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        note="Compatibility projection fixture",
        created_at=NOW,
    )
    return verification.record_decision(
        semantic_version_id,
        policy_id="p13-6-policy",
        verification_state="DETECTED",
        decision_code="INITIAL",
        rationale="Canonical semantic state remains detected",
        created_at=NOW,
    )


def test_unlinked_legacy_partly_verified_never_becomes_semantic_truth(tmp_path):
    runtime = _runtime(tmp_path)
    _, _, legacy_claim = _legacy_analysis(runtime, two=True)
    assert legacy_claim.verification_status == "PARTLY_VERIFIED"
    assert legacy_claim.confidence == 1.0

    projection = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)

    assert projection.compatibility_state == "UNLINKED"
    assert projection.semantic_verification_state is None
    assert projection.legacy.legacy_verification_status == "PARTLY_VERIFIED"
    assert projection.legacy.legacy_confidence == 1.0
    assert projection.legacy.legacy_independent_origin_count == 2
    assert projection.legacy_status_promoted is False
    assert projection.legacy_confidence_promoted is False
    assert projection.legacy_origin_count_establishes_independence is False
    assert projection.legacy.determines_semantic_verification is False
    assert projection.legacy.establishes_semantic_independence is False


def test_current_explicit_link_without_p13_5_decision_is_not_promoted(tmp_path):
    runtime = _runtime(tmp_path)
    _, _, legacy_claim = _legacy_analysis(runtime, two=True)
    semantic = _semantic_claim(runtime, "semantic-linked")
    _link(runtime, semantic.semantic_claim_version_id, legacy_claim.claim_id)

    projection = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)

    assert projection.compatibility_state == "LINKED_NO_DECISION"
    assert projection.semantic_claim_version_id == semantic.semantic_claim_version_id
    assert projection.semantic_verification_state is None
    assert projection.has_canonical_semantic_decision is False


def test_p13_5_decision_overrides_no_legacy_field_and_is_the_only_semantic_state(tmp_path):
    runtime = _runtime(tmp_path)
    _, _, legacy_claim = _legacy_analysis(runtime, two=True)
    semantic = _semantic_claim(runtime, "semantic-decided")
    _link(runtime, semantic.semantic_claim_version_id, legacy_claim.claim_id)
    decision = _detected_decision(runtime, semantic.semantic_claim_version_id)

    projection = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)

    assert legacy_claim.verification_status == "PARTLY_VERIFIED"
    assert projection.compatibility_state == "LINKED_WITH_DECISION"
    assert projection.semantic_decision == decision
    assert projection.semantic_verification_state == "DETECTED"
    assert SemanticLiveCompatibilityService(runtime).semantic_state(legacy_claim.claim_id) == "DETECTED"
    assert projection.legacy_status_promoted is False
    assert projection.legacy_confidence_promoted is False


def test_multiple_current_semantic_links_fail_closed_as_ambiguous(tmp_path):
    runtime = _runtime(tmp_path)
    _, _, legacy_claim = _legacy_analysis(runtime, two=False)
    first = _semantic_claim(runtime, "semantic-a", "First semantic proposition")
    second = _semantic_claim(runtime, "semantic-b", "Second semantic proposition")
    _link(runtime, first.semantic_claim_version_id, legacy_claim.claim_id)
    _link(runtime, second.semantic_claim_version_id, legacy_claim.claim_id)
    _detected_decision(runtime, first.semantic_claim_version_id)

    projection = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)

    assert projection.compatibility_state == "AMBIGUOUS_CURRENT_LINKS"
    assert set(projection.current_semantic_claim_version_ids) == {
        first.semantic_claim_version_id,
        second.semantic_claim_version_id,
    }
    assert projection.semantic_claim_version_id is None
    assert projection.semantic_verification_state is None


def test_superseded_link_without_current_replacement_link_is_stale(tmp_path):
    runtime = _runtime(tmp_path)
    _, _, legacy_claim = _legacy_analysis(runtime, two=False)
    claims = SemanticClaimService(runtime)
    first = _semantic_claim(runtime, "semantic-versioned", "Initial semantic proposition")
    _link(runtime, first.semantic_claim_version_id, legacy_claim.claim_id)
    second = claims.record_version(
        "semantic-versioned",
        normalized_proposition="Revised semantic proposition",
        claimant_actor="Actor",
        subject_text="Actor",
        object_theme="compatibility event",
        event_action_type="OCCURRENCE",
        polarity="AFFIRMATIVE",
        modality="ASSERTED",
        time_scope={"date": "2026-09-04"},
        location_scope={"country": "Ukraine"},
        quantity={},
        original_language="en",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.1",
        extraction_confidence=0.97,
        created_at=NOW,
    )
    _detected_decision(runtime, first.semantic_claim_version_id)

    projection = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)

    assert second.semantic_claim_version_id not in projection.historical_semantic_claim_version_ids
    assert projection.historical_semantic_claim_version_ids == (first.semantic_claim_version_id,)
    assert projection.current_semantic_claim_version_ids == ()
    assert projection.compatibility_state == "STALE_LINK"
    assert projection.semantic_verification_state is None


def test_uninstrumented_collection_does_not_fabricate_reproducibility(tmp_path):
    runtime = _runtime(tmp_path)
    _, _, legacy_claim = _legacy_analysis(runtime, instrumented=False, two=False)

    projection = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)

    assert projection.reproducibility_state == "NOT_INSTRUMENTED"
    assert projection.research_run_id is None
    assert projection.exact_query_snapshot is None
    assert projection.research_cutoff is None
    assert projection.instrumentation_version is None


def test_instrumented_collection_exposes_only_persisted_e6_metadata(tmp_path):
    runtime = _runtime(tmp_path)
    report, _, legacy_claim = _legacy_analysis(runtime, instrumented=True, two=False)

    projection = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)

    assert projection.reproducibility_state == "INSTRUMENTED_COMPLETED"
    assert projection.research_run_id is not None
    assert projection.exact_query_snapshot == QUERY
    assert projection.research_cutoff == NOW.isoformat()
    assert projection.instrumentation_version == "E6-1.0"
    projected = SemanticLiveCompatibilityService(runtime).project_collection(report.collection_id)
    assert projected == (projection,)


def test_projection_is_restart_deterministic_and_does_not_mutate_legacy_rows(tmp_path):
    runtime = _runtime(tmp_path)
    _, analysis, legacy_claim = _legacy_analysis(runtime, two=True)
    semantic = _semantic_claim(runtime, "semantic-restart")
    _link(runtime, semantic.semantic_claim_version_id, legacy_claim.claim_id)
    _detected_decision(runtime, semantic.semantic_claim_version_id)

    with sqlite3.connect(runtime.database_path) as connection:
        before_claim = connection.execute(
            "SELECT * FROM live_analysis_claims WHERE claim_id=?", (legacy_claim.claim_id,)
        ).fetchone()
        before_evidence = connection.execute(
            "SELECT * FROM live_analysis_evidence WHERE claim_id=? ORDER BY raw_item_id",
            (legacy_claim.claim_id,),
        ).fetchall()
        before_counts = (
            connection.execute("SELECT COUNT(*) FROM live_analysis_claims").fetchone()[0],
            connection.execute("SELECT COUNT(*) FROM live_analysis_evidence").fetchone()[0],
        )

    first = SemanticLiveCompatibilityService(runtime).project(legacy_claim.claim_id)
    second = SemanticLiveCompatibilityService(runtime).project_analysis_run(analysis.analysis_run_id)

    assert second == (first,)
    with sqlite3.connect(runtime.database_path) as connection:
        after_claim = connection.execute(
            "SELECT * FROM live_analysis_claims WHERE claim_id=?", (legacy_claim.claim_id,)
        ).fetchone()
        after_evidence = connection.execute(
            "SELECT * FROM live_analysis_evidence WHERE claim_id=? ORDER BY raw_item_id",
            (legacy_claim.claim_id,),
        ).fetchall()
        after_counts = (
            connection.execute("SELECT COUNT(*) FROM live_analysis_claims").fetchone()[0],
            connection.execute("SELECT COUNT(*) FROM live_analysis_evidence").fetchone()[0],
        )
    assert after_claim == before_claim
    assert after_evidence == before_evidence
    assert after_counts == before_counts


def test_projection_rejects_missing_targets_without_creating_state(tmp_path):
    runtime = _runtime(tmp_path)
    service = SemanticLiveCompatibilityService(runtime)

    with pytest.raises(ValueError, match="live analysis claim does not exist"):
        service.project("missing-live-claim")
    with pytest.raises(ValueError, match="collection has no live analysis run"):
        service.project_collection("missing-collection")
