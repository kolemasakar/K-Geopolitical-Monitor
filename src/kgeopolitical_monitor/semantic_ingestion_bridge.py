"""P22.5 canonical semantic ingestion bridge."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import sqlite3
from typing import Iterable, Mapping

from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time
from .semantic_claims import SemanticClaimService
from .semantic_evidence import SemanticEvidenceService
from .semantic_provenance import SemanticProvenanceService
from .semantic_verification import SemanticVerificationService

SEMANTIC_INGESTION_BRIDGE_VERSION = "P22.5-1.0"
BRIDGE_POLICY_ID = "p22-5-publication-attribution-policy"


def _stable(prefix: str, *parts: str) -> str:
    digest = sha256("\n".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class SemanticIngestionBridgeResult:
    analysis_run_id: str
    observed_raw_item_count: int
    created_claim_count: int
    existing_claim_count: int
    semantic_claim_version_count: int
    semantic_evidence_relation_count: int
    semantic_verification_decision_count: int
    verification_state_counts: dict[str, int]

    @property
    def creates_underlying_fact_claims(self) -> bool:
        return False

    @property
    def imports_legacy_verification(self) -> bool:
        return False

    @property
    def grants_independence(self) -> bool:
        return False


@dataclass(frozen=True)
class _ObservedItem:
    live_claim_id: str
    raw_item_id: str
    original_url: str
    source_id: str
    source_name: str
    title: str
    collected_at: str


class CanonicalSemanticIngestionBridge:
    """Fail-closed bridge from legacy live evidence to canonical P13 semantics."""

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        *,
        allowed_source_ids: Iterable[str],
        source_languages: Mapping[str, str],
    ):
        self.runtime = runtime
        self.database_path = runtime.database_path
        self.allowed_source_ids = frozenset(
            str(x).strip() for x in allowed_source_ids if str(x).strip()
        )
        self.source_languages = {
            str(k).strip(): str(v).strip() for k, v in source_languages.items()
        }
        if not self.allowed_source_ids:
            raise ValueError("allowed_source_ids must not be empty")
        missing = self.allowed_source_ids - set(self.source_languages)
        if missing:
            raise ValueError(f"missing source language(s): {sorted(missing)}")
        self.claims = SemanticClaimService(runtime)
        self.provenance = SemanticProvenanceService(runtime)
        self.evidence = SemanticEvidenceService(runtime)
        self.verification = SemanticVerificationService(runtime)

    def ingest_analysis_run(
        self,
        analysis_run_id: str,
        *,
        created_at: datetime,
    ) -> SemanticIngestionBridgeResult:
        run_id = str(analysis_run_id).strip()
        if not run_id:
            raise ValueError("analysis_run_id must not be empty")
        timestamp = _normalize_time(created_at)
        items = self._load_items(run_id)
        self._ensure_policy(timestamp)

        created = 0
        existing = 0
        for item in items:
            claim_id = _stable(
                "semantic-publication-claim", item.source_id, item.raw_item_id
            )
            current = self.claims.current(claim_id)
            if current is not None:
                self._assert_existing_complete(
                    current.semantic_claim_version_id, item
                )
                existing += 1
                continue
            self._ingest_item(claim_id, item, timestamp)
            created += 1

        counts = self._counts_for_items(items)
        return SemanticIngestionBridgeResult(
            analysis_run_id=run_id,
            observed_raw_item_count=len(items),
            created_claim_count=created,
            existing_claim_count=existing,
            semantic_claim_version_count=counts["claims"],
            semantic_evidence_relation_count=counts["evidence"],
            semantic_verification_decision_count=counts["decisions"],
            verification_state_counts=counts["states"],
        )
    def _load_items(self, analysis_run_id: str) -> tuple[_ObservedItem, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT c.claim_id,e.raw_item_id,e.original_url,i.source_id,s.name,
                       i.title,i.collected_at
                FROM live_analysis_claims c
                JOIN live_analysis_evidence e ON e.claim_id=c.claim_id
                JOIN raw_items i ON i.id=e.raw_item_id
                JOIN sources s ON s.id=i.source_id
                WHERE c.analysis_run_id=?
                ORDER BY e.raw_item_id,c.claim_id
                """,
                (analysis_run_id,),
            ).fetchall()
        if not rows:
            raise ValueError(
                "live analysis run has no evidence rows or does not exist"
            )

        by_raw: dict[str, _ObservedItem] = {}
        for row in rows:
            live_claim_id, raw_id, url, source_id, source_name, title, collected = (
                map(str, row)
            )
            if source_id not in self.allowed_source_ids:
                raise ValueError(
                    f"source is not authorized for semantic bridge: {source_id}"
                )
            candidate = _ObservedItem(
                live_claim_id=live_claim_id,
                raw_item_id=raw_id,
                original_url=url,
                source_id=source_id,
                source_name=source_name,
                title=title,
                collected_at=collected,
            )
            previous = by_raw.get(raw_id)
            if previous is not None and previous.live_claim_id != live_claim_id:
                raise RuntimeError(
                    "one raw item is linked to multiple legacy live claims"
                )
            by_raw[raw_id] = candidate
        return tuple(by_raw[key] for key in sorted(by_raw))

    def _ensure_policy(self, created_at: datetime):
        current = self.verification.policy_current(BRIDGE_POLICY_ID)
        if current is None:
            return self.verification.record_policy_version(
                BRIDGE_POLICY_ID,
                policy_name="P22.5 publication-attribution detection policy",
                created_at=created_at,
            )
        if current.review_status != "APPROVED":
            raise RuntimeError("P22.5 semantic bridge policy is not approved")
        return current

    def _ensure_entity(
        self,
        entity_id: str,
        *,
        created_at: datetime,
        **kwargs,
    ):
        current = self.provenance.entity_current(entity_id)
        if current is None:
            return self.provenance.record_entity_version(
                entity_id, created_at=created_at, **kwargs
            )
        expected = {
            "entity_kind": kwargs["entity_kind"],
            "canonical_name": kwargs["canonical_name"],
            "source_id": kwargs.get("source_id"),
            "raw_item_id": kwargs.get("raw_item_id"),
            "canonical_url": kwargs.get("canonical_url"),
            "language": kwargs.get("language"),
        }
        for name, value in expected.items():
            if getattr(current, name) != value:
                raise RuntimeError(
                    f"existing provenance entity conflicts on {name}: {entity_id}"
                )
        return current

    def _ingest_item(
        self,
        claim_id: str,
        item: _ObservedItem,
        created_at: datetime,
    ) -> None:
        language = self.source_languages[item.source_id]
        proposition = (
            f'{item.source_name} published material titled "{item.title}".'
        )
        claim = self.claims.record_version(
            claim_id,
            normalized_proposition=proposition,
            claimant_actor=item.source_name,
            subject_text=item.source_name,
            object_theme=item.title,
            event_action_type="PUBLICATION",
            polarity="AFFIRMATIVE",
            modality="ASSERTED",
            time_scope={"observed_collected_at": item.collected_at},
            location_scope={},
            quantity={},
            original_language=language,
            extraction_method="PUBLICATION_ATTRIBUTION_BRIDGE",
            extraction_version=SEMANTIC_INGESTION_BRIDGE_VERSION,
            extraction_confidence=0.99,
            created_at=created_at,
        )
        self.claims.link(
            claim.semantic_claim_version_id,
            target_type="RAW_ITEM",
            target_id=item.raw_item_id,
            created_at=created_at,
        )
        self.claims.link(
            claim.semantic_claim_version_id,
            target_type="LIVE_ANALYSIS_CLAIM",
            target_id=item.live_claim_id,
            created_at=created_at,
        )

        publisher = self._ensure_entity(
            _stable("semantic-publisher", item.source_id),
            entity_kind="PUBLISHER",
            canonical_name=item.source_name,
            source_id=item.source_id,
            language=language,
            metadata={"bridge_version": SEMANTIC_INGESTION_BRIDGE_VERSION},
            created_at=created_at,
        )
        publication = self._ensure_entity(
            _stable("semantic-publication", item.source_id, item.raw_item_id),
            entity_kind="PUBLICATION",
            canonical_name=item.title,
            source_id=item.source_id,
            raw_item_id=item.raw_item_id,
            canonical_url=item.original_url,
            language=language,
            metadata={"bridge_version": SEMANTIC_INGESTION_BRIDGE_VERSION},
            created_at=created_at,
        )
        unresolved = self._ensure_entity(
            _stable("semantic-underlying-origin", item.raw_item_id),
            entity_kind="UNKNOWN",
            canonical_name=f"Unresolved underlying origin for {item.raw_item_id}",
            metadata={"bridge_version": SEMANTIC_INGESTION_BRIDGE_VERSION},
            created_at=created_at,
        )

        for role, entity, state in (
            ("PUBLICATION", publication, "OBSERVED"),
            ("PUBLISHER", publisher, "OBSERVED"),
            ("UNDERLYING_ORIGIN", unresolved, "UNRESOLVED"),
        ):
            self.provenance.record_claim_role_version(
                _stable(
                    "semantic-claim-role",
                    claim.semantic_claim_version_id,
                    role,
                ),
                semantic_claim_version_id=claim.semantic_claim_version_id,
                provenance_entity_version_id=entity.provenance_entity_version_id,
                provenance_role=role,
                attribution_state=state,
                note=(
                    "P22.5 bridge preserves publication attribution and "
                    "unresolved underlying origin."
                ),
                created_at=created_at,
            )

        self.provenance.record_relation_version(
            _stable(
                "semantic-provenance-relation",
                publication.provenance_entity_version_id,
                publisher.provenance_entity_version_id,
            ),
            subject_entity_version_id=publication.provenance_entity_version_id,
            object_entity_version_id=publisher.provenance_entity_version_id,
            relation_type="PUBLISHED_BY",
            note=(
                "Direct publication-to-publisher relation observed by "
                "the P22.5 bridge."
            ),
            created_at=created_at,
        )
        self.evidence.record_relation_version(
            _stable(
                "semantic-evidence-relation",
                claim.semantic_claim_version_id,
                item.raw_item_id,
            ),
            semantic_claim_version_id=claim.semantic_claim_version_id,
            evidence_provenance_entity_version_id=(
                publication.provenance_entity_version_id
            ),
            raw_item_id=item.raw_item_id,
            relation_type="ATTRIBUTION_ONLY",
            assessment_method="PUBLICATION_ATTRIBUTION_BRIDGE",
            assessment_version=SEMANTIC_INGESTION_BRIDGE_VERSION,
            note=(
                "Supports only that the publisher published the material; "
                "not the underlying-world claim."
            ),
            created_at=created_at,
        )
        self.verification.record_confidence_version(
            claim.semantic_claim_version_id,
            evidence_sufficiency="LOW",
            provenance_independence="UNKNOWN",
            authority_proximity="MEDIUM",
            contradiction_resolution="UNKNOWN",
            temporal_freshness="UNKNOWN",
            extraction_certainty="HIGH",
            translation_certainty="HIGH",
            claim_specific_certainty="MEDIUM",
            coverage_limitation="LIMITED",
            assessment_method="PUBLICATION_ATTRIBUTION_BRIDGE",
            assessment_version=SEMANTIC_INGESTION_BRIDGE_VERSION,
            note=(
                "Attribution-only confidence profile; "
                "no underlying fact promotion."
            ),
            created_at=created_at,
        )
        self.verification.record_decision(
            claim.semantic_claim_version_id,
            policy_id=BRIDGE_POLICY_ID,
            verification_state="DETECTED",
            decision_code="INITIAL",
            rationale=(
                "Observed publication attribution only; "
                "underlying factual content is not verified."
            ),
            created_at=created_at,
        )

    def _assert_existing_complete(
        self,
        claim_version_id: str,
        item: _ObservedItem,
    ) -> None:
        links = {
            (link.target_type, link.target_id)
            for link in self.claims.links(claim_version_id)
        }
        required = {
            ("RAW_ITEM", item.raw_item_id),
            ("LIVE_ANALYSIS_CLAIM", item.live_claim_id),
        }
        if not required.issubset(links):
            raise RuntimeError(
                "existing bridge claim is incomplete: semantic links missing"
            )
        relations = self.evidence.relations_for_claim(claim_version_id)
        if not relations or any(
            relation.relation_type != "ATTRIBUTION_ONLY"
            for relation in relations
        ):
            raise RuntimeError(
                "existing bridge claim is incomplete or has non-attribution evidence"
            )
        decision = self.verification.decision_current(claim_version_id)
        if decision is None or decision.verification_state != "DETECTED":
            raise RuntimeError(
                "existing bridge claim is missing the fail-closed DETECTED decision"
            )

    def _counts_for_items(
        self,
        items: tuple[_ObservedItem, ...],
    ) -> dict[str, object]:
        raw_ids = tuple(item.raw_item_id for item in items)
        placeholders = ",".join("?" for _ in raw_ids)
        with sqlite3.connect(self.database_path) as connection:
            claim_rows = connection.execute(
                f"""
                SELECT DISTINCT v.semantic_claim_version_id
                FROM semantic_claim_versions v
                JOIN semantic_claim_links l
                  ON l.semantic_claim_version_id=v.semantic_claim_version_id
                WHERE l.target_type='RAW_ITEM'
                  AND l.target_id IN ({placeholders})
                  AND v.extraction_method='PUBLICATION_ATTRIBUTION_BRIDGE'
                """,
                raw_ids,
            ).fetchall()
            claim_ids = tuple(str(row[0]) for row in claim_rows)
            if not claim_ids:
                return {
                    "claims": 0,
                    "evidence": 0,
                    "decisions": 0,
                    "states": {},
                }
            cp = ",".join("?" for _ in claim_ids)
            evidence_count = connection.execute(
                f"""
                SELECT COUNT(*)
                FROM semantic_evidence_relation_versions
                WHERE semantic_claim_version_id IN ({cp})
                """,
                claim_ids,
            ).fetchone()[0]
            decision_rows = connection.execute(
                f"""
                SELECT verification_state,COUNT(*)
                FROM semantic_verification_decision_versions
                WHERE semantic_claim_version_id IN ({cp})
                GROUP BY verification_state
                """,
                claim_ids,
            ).fetchall()
        states = {
            str(state): int(count)
            for state, count in decision_rows
        }
        return {
            "claims": len(claim_ids),
            "evidence": int(evidence_count),
            "decisions": sum(states.values()),
            "states": states,
        }