from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.semantic_claims import SemanticClaimService


NOW = datetime(2026, 9, 1, 20, 45, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _record(service, claim_id="semantic-claim-1", **overrides):
    values = dict(
        normalized_proposition="Russia announced a new measure affecting Ukraine",
        claimant_actor="Russian government",
        subject_text="Russia",
        object_theme="new measure affecting Ukraine",
        event_action_type="ANNOUNCEMENT",
        polarity="AFFIRMATIVE",
        modality="REPORTED",
        time_scope={"start": "2026-09-01"},
        location_scope={"country": "Ukraine"},
        quantity={"value": 1, "unit": "measure"},
        original_language="uk",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.0",
        extraction_confidence=0.91,
        created_at=NOW,
    )
    values.update(overrides)
    return service.record_version(claim_id, **values)


def test_structured_claim_preserves_unicode_and_separates_extraction_confidence(tmp_path):
    service = SemanticClaimService(_runtime(tmp_path))
    claim = _record(
        service,
        normalized_proposition="Україна повідомила про нове рішення",
        claimant_actor="Уряд України",
        object_theme="рішення щодо безпеки",
        original_language="uk-UA",
    )

    assert claim.normalized_proposition == "Україна повідомила про нове рішення"
    assert claim.claimant_actor == "Уряд України"
    assert claim.original_language == "uk-ua"
    assert claim.extraction_confidence == 0.91
    assert claim.factual_confidence is None
    assert claim.changes_verification_state is False
    assert claim.establishes_independence is False


def test_explicit_semantic_identity_is_not_inferred_from_same_text(tmp_path):
    service = SemanticClaimService(_runtime(tmp_path))
    first = _record(service, "claim-a", normalized_proposition="Same proposition text")
    second = _record(service, "claim-b", normalized_proposition="Same proposition text")

    assert first.semantic_claim_id != second.semantic_claim_id
    assert first.semantic_claim_version_id != second.semantic_claim_version_id


def test_semantic_claim_versions_are_immutable_and_supersede_in_order(tmp_path):
    runtime = _runtime(tmp_path)
    service = SemanticClaimService(runtime)
    first = _record(service)
    second = _record(
        service,
        normalized_proposition="Russia announced a revised measure affecting Ukraine",
        extraction_confidence=0.97,
    )

    assert first.semantic_version == 1
    assert second.semantic_version == 2
    assert second.supersedes_version_id == first.semantic_claim_version_id
    assert [item.semantic_version for item in service.history("semantic-claim-1")] == [1, 2]
    assert service.current("semantic-claim-1") == second

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE semantic_claim_versions SET normalized_proposition = 'changed' WHERE semantic_claim_version_id = ?",
                (first.semantic_claim_version_id,),
            )


def test_structured_dimensions_are_json_objects_and_deterministic(tmp_path):
    service = SemanticClaimService(_runtime(tmp_path))
    claim = _record(
        service,
        time_scope={"end": "2026-09-02", "start": "2026-09-01"},
        location_scope={"city": "Київ", "country": "Україна"},
        quantity={"max": 12, "min": 10, "unit": "units"},
    )

    assert claim.time_scope == {"end": "2026-09-02", "start": "2026-09-01"}
    assert claim.location_scope["city"] == "Київ"
    assert claim.quantity == {"max": 12, "min": 10, "unit": "units"}


def test_validation_fails_closed_without_creating_truth_semantics(tmp_path):
    service = SemanticClaimService(_runtime(tmp_path))
    with pytest.raises(ValueError, match="unsupported polarity"):
        _record(service, polarity="TRUE")
    with pytest.raises(ValueError, match="unsupported modality"):
        _record(service, modality="CERTAIN")
    with pytest.raises(ValueError, match="between 0 and 1"):
        _record(service, extraction_confidence=1.1)
    with pytest.raises(ValueError, match="language tag"):
        _record(service, original_language="not a language tag")
    with pytest.raises(ValueError, match="JSON-serializable"):
        _record(service, quantity={"bad": {1, 2}})


def test_links_connect_to_legacy_live_and_raw_without_becoming_evidence_relations(tmp_path):
    runtime = _runtime(tmp_path)
    service = SemanticClaimService(runtime)
    claim = _record(service)

    # Seed compatibility targets. Direct sqlite seed is intentional: P13.1 only
    # validates existence and does not change the semantics of these legacy rows.
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            "INSERT INTO claims(id, event_id, text, confidence) VALUES (?, ?, ?, ?)",
            ("legacy-1", "event-x", "legacy text", "LOW"),
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES (?, ?, ?, ?, ?)",
            ("raw-1", "source-x", "title", "content", NOW.isoformat()),
        )
        connection.execute(
            "INSERT INTO live_analysis_claims(claim_id, analysis_run_id, claim_key, title, verification_status, confidence, importance, independent_origin_count, source_class_count, origins_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("live-1", "run-x", "key", "title", "DETECTED", 0.2, 0.1, 1, 1, "[]"),
        )

    links = (
        service.link(claim.semantic_claim_version_id, target_type="LEGACY_CLAIM", target_id="legacy-1", created_at=NOW),
        service.link(claim.semantic_claim_version_id, target_type="LIVE_ANALYSIS_CLAIM", target_id="live-1", created_at=NOW),
        service.link(claim.semantic_claim_version_id, target_type="RAW_ITEM", target_id="raw-1", created_at=NOW),
    )

    assert all(link.is_evidence_relation is False for link in links)
    assert {link.target_type for link in service.links(claim.semantic_claim_version_id)} == {
        "LEGACY_CLAIM",
        "LIVE_ANALYSIS_CLAIM",
        "RAW_ITEM",
    }
    repeated = service.link(
        claim.semantic_claim_version_id,
        target_type="RAW_ITEM",
        target_id="raw-1",
        created_at=NOW,
    )
    assert repeated.link_id == links[2].link_id


def test_link_target_existence_and_type_fail_closed(tmp_path):
    service = SemanticClaimService(_runtime(tmp_path))
    claim = _record(service)

    with pytest.raises(ValueError, match="unsupported target_type"):
        service.link(claim.semantic_claim_version_id, target_type="EVIDENCE", target_id="x", created_at=NOW)
    with pytest.raises(ValueError, match="target does not exist"):
        service.link(claim.semantic_claim_version_id, target_type="RAW_ITEM", target_id="missing", created_at=NOW)


def test_schema_contains_no_p13_2_plus_truth_fields(tmp_path):
    runtime = _runtime(tmp_path)
    with sqlite3.connect(runtime.database_path) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(semantic_claim_versions)").fetchall()
        }
    forbidden = {
        "underlying_origin",
        "independence_state",
        "evidence_relation",
        "contradiction_state",
        "verification_state",
        "factual_confidence",
        "coverage_confidence",
    }
    assert forbidden.isdisjoint(columns)
