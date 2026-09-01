from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.provenance import SemanticProvenanceService
from kgeopolitical_monitor.semantic_claims import SemanticClaimService


NOW = datetime(2026, 9, 1, 21, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _claim(runtime, claim_id="claim-provenance-1"):
    return SemanticClaimService(runtime).record_version(
        claim_id,
        normalized_proposition="The government announced a new measure",
        claimant_actor="Government",
        subject_text="Government",
        object_theme="new measure",
        event_action_type="ANNOUNCEMENT",
        polarity="AFFIRMATIVE",
        modality="REPORTED",
        time_scope={"date": "2026-09-01"},
        location_scope={"country": "Example"},
        quantity={},
        original_language="en",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.0",
        extraction_confidence=0.95,
        created_at=NOW,
    )


def _seed_source_and_raw(runtime, source_id="reuters", raw_id="reuters-item"):
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            (source_id, "Reuters", "Media", "context-only"),
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES (?, ?, ?, ?, ?)",
            (raw_id, source_id, "Article", "Article content", NOW.isoformat()),
        )


def test_reuters_publication_citing_official_statement_has_explicit_provenance_chain(tmp_path):
    runtime = _runtime(tmp_path)
    _seed_source_and_raw(runtime)
    claim = _claim(runtime)
    service = SemanticProvenanceService(runtime)

    publication = service.record_entity_version(
        "publication-reuters-1",
        entity_kind="PUBLICATION",
        canonical_name="Reuters article",
        source_id="reuters",
        raw_item_id="reuters-item",
        canonical_url="https://www.reuters.com/world/example-article",
        language="en",
        metadata={"publisher_label": "Reuters"},
        created_at=NOW,
    )
    publisher = service.record_entity_version(
        "publisher-reuters",
        entity_kind="PUBLISHER",
        canonical_name="Reuters",
        canonical_url="https://www.reuters.com/",
        created_at=NOW,
    )
    statement = service.record_entity_version(
        "official-statement-1",
        entity_kind="OFFICIAL_STATEMENT",
        canonical_name="Official government statement",
        canonical_url="https://www.example.gov/statement/1",
        language="en",
        created_at=NOW,
    )

    publication_role = service.record_claim_role_version(
        "claim-role-publication-1",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        provenance_entity_version_id=publication.provenance_entity_version_id,
        provenance_role="PUBLICATION",
        attribution_state="OBSERVED",
        created_at=NOW,
    )
    underlying_role = service.record_claim_role_version(
        "claim-role-origin-1",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        provenance_entity_version_id=statement.provenance_entity_version_id,
        provenance_role="UNDERLYING_ORIGIN",
        attribution_state="ASSERTED",
        note="Reuters cites the government statement as the underlying source for this attributed claim",
        created_at=NOW,
    )
    published_by = service.record_relation_version(
        "relation-published-by-1",
        subject_entity_version_id=publication.provenance_entity_version_id,
        object_entity_version_id=publisher.provenance_entity_version_id,
        relation_type="PUBLISHED_BY",
        created_at=NOW,
    )
    cites = service.record_relation_version(
        "relation-cites-1",
        subject_entity_version_id=publication.provenance_entity_version_id,
        object_entity_version_id=statement.provenance_entity_version_id,
        relation_type="CITES",
        created_at=NOW,
    )

    assert publication_role.is_evidence_relation is False
    assert underlying_role.establishes_independence is False
    assert underlying_role.changes_verification_state is False
    assert published_by.establishes_independence is False
    assert cites.changes_verification_state is False
    assert {role.provenance_role for role in service.claim_roles(claim.semantic_claim_version_id)} == {
        "PUBLICATION",
        "UNDERLYING_ORIGIN",
    }
    assert service.relation_history("relation-cites-1")[0].relation_type == "CITES"


def test_entity_versions_are_append_only_and_preserve_traceability(tmp_path):
    runtime = _runtime(tmp_path)
    _seed_source_and_raw(runtime)
    service = SemanticProvenanceService(runtime)

    first = service.record_entity_version(
        "publication-1",
        entity_kind="PUBLICATION",
        canonical_name="Original publication label",
        source_id="reuters",
        raw_item_id="reuters-item",
        canonical_url="https://www.reuters.com/article/1",
        created_at=NOW,
    )
    second = service.record_entity_version(
        "publication-1",
        entity_kind="PUBLICATION",
        canonical_name="Corrected publication label",
        source_id="reuters",
        raw_item_id="reuters-item",
        canonical_url="https://www.reuters.com/article/1",
        created_at=NOW,
    )

    assert first.provenance_version == 1
    assert second.provenance_version == 2
    assert second.supersedes_version_id == first.provenance_entity_version_id
    assert [item.provenance_version for item in service.entity_history("publication-1")] == [1, 2]
    assert service.entity_current("publication-1") == second

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE semantic_provenance_entity_versions SET canonical_name='mutated' WHERE provenance_entity_version_id=?",
                (first.provenance_entity_version_id,),
            )


def test_source_and_raw_item_traceability_fail_closed(tmp_path):
    runtime = _runtime(tmp_path)
    _seed_source_and_raw(runtime, source_id="source-a", raw_id="raw-a")
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            ("source-b", "Other Publisher", "Media", "context-only"),
        )
    service = SemanticProvenanceService(runtime)

    with pytest.raises(ValueError, match="source_id does not exist"):
        service.record_entity_version(
            "bad-source",
            entity_kind="SOURCE_ENDPOINT",
            canonical_name="Missing source",
            source_id="missing",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="raw_item_id does not exist"):
        service.record_entity_version(
            "bad-raw",
            entity_kind="PUBLICATION",
            canonical_name="Missing raw",
            raw_item_id="missing",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="does not match raw_item source"):
        service.record_entity_version(
            "bad-mismatch",
            entity_kind="PUBLICATION",
            canonical_name="Mismatched publication",
            source_id="source-b",
            raw_item_id="raw-a",
            created_at=NOW,
        )


def test_unknown_and_mixed_underlying_origin_remain_explicit(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    service = SemanticProvenanceService(runtime)

    unknown = service.record_entity_version(
        "unknown-origin-1",
        entity_kind="UNKNOWN",
        canonical_name="Unresolved underlying origin",
        metadata={"reason": "publication does not identify the source"},
        created_at=NOW,
    )
    mixed = service.record_entity_version(
        "mixed-origin-1",
        entity_kind="MIXED",
        canonical_name="Mixed underlying origin",
        metadata={"reason": "multiple inseparable origin components"},
        created_at=NOW,
    )

    unresolved = service.record_claim_role_version(
        "origin-role-unknown",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        provenance_entity_version_id=unknown.provenance_entity_version_id,
        provenance_role="UNDERLYING_ORIGIN",
        attribution_state="UNRESOLVED",
        created_at=NOW,
    )
    mixed_role = service.record_claim_role_version(
        "origin-role-mixed",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        provenance_entity_version_id=mixed.provenance_entity_version_id,
        provenance_role="UNDERLYING_ORIGIN",
        attribution_state="MIXED",
        created_at=NOW,
    )

    assert unresolved.attribution_state == "UNRESOLVED"
    assert mixed_role.attribution_state == "MIXED"
    assert unresolved.establishes_independence is False

    with pytest.raises(ValueError, match="cannot claim concrete"):
        service.record_entity_version(
            "unknown-with-url",
            entity_kind="UNKNOWN",
            canonical_name="Unknown with fake precision",
            canonical_url="https://example.com/guessed-origin",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="UNKNOWN underlying origin must remain UNRESOLVED"):
        service.record_claim_role_version(
            "origin-role-bad",
            semantic_claim_version_id=claim.semantic_claim_version_id,
            provenance_entity_version_id=unknown.provenance_entity_version_id,
            provenance_role="UNDERLYING_ORIGIN",
            attribution_state="ASSERTED",
            created_at=NOW,
        )


def test_derivation_chain_tracks_syndication_repost_and_translation_without_independence(tmp_path):
    runtime = _runtime(tmp_path)
    service = SemanticProvenanceService(runtime)
    original = service.record_entity_version(
        "wire-original",
        entity_kind="WIRE_REPORT",
        canonical_name="Wire original",
        canonical_url="https://wire.example/report/1",
        language="en",
        created_at=NOW,
    )
    syndication = service.record_entity_version(
        "syndicated-publication",
        entity_kind="PUBLICATION",
        canonical_name="Syndicated publication",
        canonical_url="https://publisher.example/reprint/1",
        language="en",
        created_at=NOW,
    )
    translation = service.record_entity_version(
        "translated-publication",
        entity_kind="PUBLICATION",
        canonical_name="Translated repost",
        canonical_url="https://publisher.example/uk/reprint/1",
        language="uk",
        created_at=NOW,
    )

    syndicated = service.record_relation_version(
        "rel-syndicated",
        subject_entity_version_id=syndication.provenance_entity_version_id,
        object_entity_version_id=original.provenance_entity_version_id,
        relation_type="SYNDICATED_FROM",
        created_at=NOW,
    )
    translated = service.record_relation_version(
        "rel-translated",
        subject_entity_version_id=translation.provenance_entity_version_id,
        object_entity_version_id=syndication.provenance_entity_version_id,
        relation_type="TRANSLATED_FROM",
        created_at=NOW,
    )

    assert syndicated.establishes_independence is False
    assert translated.establishes_independence is False
    assert translated.changes_verification_state is False


def test_relation_and_claim_role_versions_supersede_without_mutation(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    service = SemanticProvenanceService(runtime)
    publication = service.record_entity_version(
        "publication-versioned",
        entity_kind="PUBLICATION",
        canonical_name="Publication",
        created_at=NOW,
    )
    publisher = service.record_entity_version(
        "publisher-versioned",
        entity_kind="PUBLISHER",
        canonical_name="Publisher",
        created_at=NOW,
    )

    role1 = service.record_claim_role_version(
        "role-versioned",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        provenance_entity_version_id=publication.provenance_entity_version_id,
        provenance_role="PUBLICATION",
        attribution_state="OBSERVED",
        note="first observation",
        created_at=NOW,
    )
    role2 = service.record_claim_role_version(
        "role-versioned",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        provenance_entity_version_id=publication.provenance_entity_version_id,
        provenance_role="PUBLICATION",
        attribution_state="OBSERVED",
        note="corrected note",
        created_at=NOW,
    )
    rel1 = service.record_relation_version(
        "relation-versioned",
        subject_entity_version_id=publication.provenance_entity_version_id,
        object_entity_version_id=publisher.provenance_entity_version_id,
        relation_type="PUBLISHED_BY",
        note="initial",
        created_at=NOW,
    )
    rel2 = service.record_relation_version(
        "relation-versioned",
        subject_entity_version_id=publication.provenance_entity_version_id,
        object_entity_version_id=publisher.provenance_entity_version_id,
        relation_type="PUBLISHED_BY",
        note="corrected",
        created_at=NOW,
    )

    assert role1.role_version == 1 and role2.role_version == 2
    assert role2.supersedes_role_version_id == role1.claim_provenance_role_version_id
    assert rel1.relation_version == 1 and rel2.relation_version == 2
    assert rel2.supersedes_relation_version_id == rel1.provenance_relation_version_id
    assert [item.relation_version for item in service.relation_history("relation-versioned")] == [1, 2]


def test_url_validation_rejects_credentials_and_sensitive_query_material(tmp_path):
    service = SemanticProvenanceService(_runtime(tmp_path))
    with pytest.raises(ValueError, match="HTTP or HTTPS"):
        service.record_entity_version(
            "bad-url-scheme",
            entity_kind="PUBLICATION",
            canonical_name="Bad URL",
            canonical_url="file:///tmp/item",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="credentials"):
        service.record_entity_version(
            "bad-url-userinfo",
            entity_kind="PUBLICATION",
            canonical_name="Bad URL",
            canonical_url="https://user:password@example.com/item",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="sensitive query credentials"):
        service.record_entity_version(
            "bad-url-token",
            entity_kind="PUBLICATION",
            canonical_name="Bad URL",
            canonical_url="https://example.com/item?access_token=secret",
            created_at=NOW,
        )


def test_p13_2_schema_contains_no_independence_evidence_contradiction_or_verification_fields(tmp_path):
    runtime = _runtime(tmp_path)
    tables = (
        "semantic_provenance_entity_versions",
        "semantic_claim_provenance_role_versions",
        "semantic_provenance_relation_versions",
    )
    forbidden = {
        "independence_state",
        "evidence_relation",
        "evidence_stance",
        "contradiction_state",
        "verification_state",
        "factual_confidence",
        "coverage_confidence",
    }
    with sqlite3.connect(runtime.database_path) as connection:
        for table in tables:
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
            assert forbidden.isdisjoint(columns)
