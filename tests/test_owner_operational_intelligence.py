from datetime import datetime, timedelta, timezone
import json
import sqlite3

from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.owner_operational_intelligence import (
    OWNER_OPERATIONAL_ACTIVATION,
    PHASE_14_GATE,
    OwnerOperationalIntelligenceReader,
)
from kgeopolitical_monitor.semantic_claims import SemanticClaimService
from kgeopolitical_monitor.semantic_verification import SemanticVerificationService
from kgeopolitical_monitor.strategic_alerts import StrategicAlertService


NOW = datetime(2026, 9, 4, 13, 0, tzinfo=timezone.utc)


class StaticAdapter:
    adapter_version = "p14-test-1.0"

    def __init__(self, source_id, url):
        self.source_id = source_id
        self.source_name = source_id
        self.source_class = "Official sources" if source_id == "official-a" else "International media"
        self.reliability = "official" if source_id == "official-a" else "medium"
        self.url = url

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=f"item-{self.source_id}",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Phase 14 operational intelligence event",
                summary="Deterministic owner-operational fixture",
                original_url=self.url,
                collected_at=collected_at,
                metadata={"language": "en"},
                reliability=self.reliability,
            )
        ]


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Phase 14 watch",
        "phase 14 operational intelligence",
        60,
        watch_id="watch-p14",
        created_at=NOW - timedelta(hours=1),
    )
    return runtime


def _legacy_claim(runtime, *, two_sources=True):
    adapters = [StaticAdapter("official-a", "https://official.example/statement")]
    if two_sources:
        adapters.append(StaticAdapter("media-b", "https://media.example/report"))
    report = LiveSourceCollector(runtime, adapters).collect("watch-p14", NOW)
    analysis = LiveEndToEndProcessor(runtime).process_collection(report.collection_id, processed_at=NOW)
    assert len(analysis.claims) == 1
    return analysis.claims[0]


def _insert_finding(runtime, live_claim_id, *, finding_id="finding-p14", importance=0.9, confidence=0.9):
    run = runtime.start_run(
        "watch-p14",
        run_id=f"run-{finding_id}",
        started_at=NOW - timedelta(minutes=2),
    )
    runtime.complete_run(
        run.run_id,
        result_count=1,
        completed_at=NOW - timedelta(minutes=1),
    )
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO operational_findings(
                finding_id, run_id, watch_id, title, summary,
                importance, confidence, evidence_refs, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                finding_id,
                run.run_id,
                "watch-p14",
                "Phase 14 finding",
                "Persisted finding for owner operational intelligence",
                importance,
                confidence,
                json.dumps([f"claim:{live_claim_id}"]),
                "Persisted deterministic explanation",
                NOW.isoformat(),
            ),
        )
    return finding_id


def _semantic_claim(runtime, semantic_id, proposition):
    return SemanticClaimService(runtime).record_version(
        semantic_id,
        normalized_proposition=proposition,
        claimant_actor="Actor",
        subject_text="Actor",
        object_theme="phase 14 event",
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
    SemanticClaimService(runtime).link(
        semantic_version_id,
        target_type="LIVE_ANALYSIS_CLAIM",
        target_id=live_claim_id,
        created_at=NOW,
    )


def _detected_decision(runtime, semantic_version_id):
    verification = SemanticVerificationService(runtime)
    verification.record_policy_version(
        "p14-policy",
        policy_name="Phase 14 semantic policy fixture",
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
        note="Phase 14 fixture",
        created_at=NOW,
    )
    return verification.record_decision(
        semantic_version_id,
        policy_id="p14-policy",
        verification_state="DETECTED",
        decision_code="INITIAL",
        rationale="Canonical semantic state remains DETECTED",
        created_at=NOW,
    )


def test_phase14_workspace_is_read_only_and_activation_blocked(tmp_path):
    runtime = _runtime(tmp_path)

    def counts():
        with sqlite3.connect(runtime.database_path) as connection:
            return {
                "watches": connection.execute("SELECT COUNT(*) FROM monitoring_watches").fetchone()[0],
                "runs": connection.execute("SELECT COUNT(*) FROM monitoring_runs").fetchone()[0],
                "alerts": connection.execute("SELECT COUNT(*) FROM strategic_alerts").fetchone()[0],
                "decisions": connection.execute(
                    "SELECT COUNT(*) FROM semantic_verification_decision_versions"
                ).fetchone()[0],
            }

    before = counts()
    snapshot = OwnerOperationalIntelligenceReader(runtime).workspace_snapshot(now=NOW)
    after = counts()

    assert snapshot["phase_14_gate"] == PHASE_14_GATE
    assert snapshot["phase_14_gate_state"] == "IMPLEMENTED_VALIDATION_PENDING"
    assert snapshot["owner_operational_activation"] == OWNER_OPERATIONAL_ACTIVATION
    assert snapshot["owner_execution_enabled"] is False
    assert snapshot["production_live"] == "NOT_OPERATIONAL"
    assert snapshot["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert after == before


def test_phase14_unlinked_legacy_verification_fails_closed(tmp_path):
    runtime = _runtime(tmp_path)
    legacy = _legacy_claim(runtime, two_sources=True)
    assert legacy.verification_status == "PARTLY_VERIFIED"
    finding_id = _insert_finding(runtime, legacy.claim_id)
    StrategicAlertService(runtime).configure_watch(
        "watch-p14",
        priority="HIGH",
        minimum_importance=0.5,
        minimum_confidence=0.5,
        minimum_verification_rank=1,
        configured_at=NOW,
    )

    reader = OwnerOperationalIntelligenceReader(runtime)
    finding = reader.recent_findings(limit=1)[0]
    evaluation = reader.dry_run_alert_qualification(finding_id)

    assert finding["legacy_live_verification_status"] == "PARTLY_VERIFIED"
    assert finding["legacy_fields_canonical"] is False
    assert finding["semantic_compatibility_state"] == "UNLINKED"
    assert finding["semantic_verification_state"] is None
    assert finding["canonical_verification_available"] is False
    assert evaluation["would_qualify_after_activation"] is False
    assert evaluation["reason"] == "NO_CANONICAL_SEMANTIC_DECISION"
    assert evaluation["legacy_verification_used_for_qualification"] is False
    with sqlite3.connect(runtime.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM strategic_alerts").fetchone()[0] == 0


def test_phase14_current_p13_5_decision_drives_dry_run_without_side_effect(tmp_path):
    runtime = _runtime(tmp_path)
    legacy = _legacy_claim(runtime, two_sources=True)
    finding_id = _insert_finding(runtime, legacy.claim_id)
    semantic = _semantic_claim(runtime, "semantic-p14", "The Phase 14 event occurred")
    _link(runtime, semantic.semantic_claim_version_id, legacy.claim_id)
    _detected_decision(runtime, semantic.semantic_claim_version_id)
    StrategicAlertService(runtime).configure_watch(
        "watch-p14",
        priority="CRITICAL",
        minimum_importance=0.5,
        minimum_confidence=0.5,
        minimum_verification_rank=0,
        configured_at=NOW,
    )

    reader = OwnerOperationalIntelligenceReader(runtime)
    evaluation = reader.dry_run_alert_qualification(finding_id)
    brief = reader.owner_brief(now=NOW)

    assert evaluation["semantic_compatibility_state"] == "LINKED_WITH_DECISION"
    assert evaluation["semantic_verification_state"] == "DETECTED"
    assert evaluation["canonical_verification_source"] == "P13.5_DECISION"
    assert evaluation["would_qualify_after_activation"] is True
    assert evaluation["reason"] == "QUALIFIES_IF_OWNER_ACTIVATES_PHASE_14"
    assert evaluation["activation_blocked"] is True
    assert evaluation["persisted_alert_created"] is False
    assert brief["verified_items"] == []
    assert brief["analysis_or_unresolved_items"][0]["semantic_verification_state"] == "DETECTED"
    with sqlite3.connect(runtime.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM strategic_alerts").fetchone()[0] == 0


def test_phase14_ambiguous_current_semantic_links_fail_closed(tmp_path):
    runtime = _runtime(tmp_path)
    legacy = _legacy_claim(runtime, two_sources=False)
    finding_id = _insert_finding(runtime, legacy.claim_id)
    first = _semantic_claim(runtime, "semantic-p14-a", "First Phase 14 proposition")
    second = _semantic_claim(runtime, "semantic-p14-b", "Second Phase 14 proposition")
    _link(runtime, first.semantic_claim_version_id, legacy.claim_id)
    _link(runtime, second.semantic_claim_version_id, legacy.claim_id)
    _detected_decision(runtime, first.semantic_claim_version_id)
    StrategicAlertService(runtime).configure_watch(
        "watch-p14",
        minimum_verification_rank=0,
        configured_at=NOW,
    )

    evaluation = OwnerOperationalIntelligenceReader(runtime).dry_run_alert_qualification(
        finding_id
    )

    assert evaluation["semantic_compatibility_state"] == "AMBIGUOUS_CURRENT_LINKS"
    assert evaluation["semantic_verification_state"] is None
    assert evaluation["would_qualify_after_activation"] is False
    assert evaluation["reason"] == "NO_CANONICAL_SEMANTIC_DECISION"


def test_phase14_watch_queue_exposes_persisted_priority_but_never_enables_execution(tmp_path):
    runtime = _runtime(tmp_path)
    StrategicAlertService(runtime).configure_watch(
        "watch-p14",
        priority="CRITICAL",
        minimum_importance=0.8,
        minimum_confidence=0.7,
        minimum_verification_rank=2,
        configured_at=NOW,
    )

    queue = OwnerOperationalIntelligenceReader(runtime).watch_queue(now=NOW)

    assert len(queue) == 1
    assert queue[0]["watch_id"] == "watch-p14"
    assert queue[0]["configured_priority"] == "CRITICAL"
    assert queue[0]["alert_policy"]["minimum_verification_rank"] == 2
    assert queue[0]["owner_execution_enabled"] is False
    assert queue[0]["owner_execution_state"] == OWNER_OPERATIONAL_ACTIVATION
