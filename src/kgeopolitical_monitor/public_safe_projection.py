"""Phase 17.2 public-safe projection and redaction.

This module projects an already P17.1-eligible canonical semantic claim into a
strictly allowlisted public-safe representation. It is read-only, local-only and
non-operational: it does not publish, expose an HTTP route, persist a new truth
record, or activate a provider.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re
from typing import Final, Iterable

from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime
from .publication_eligibility import PublicationEligibilityDecision


PUBLIC_SAFE_PROJECTION_VERSION: Final[str] = "KGM_PUBLIC_SAFE_PROJECTION_V1"
P17_2_GATE: Final[str] = "P17_2_PUBLIC_SAFE_PROJECTION_REDACTION_VALIDATED"
P17_2_MIGRATION: Final[str] = "NONE"

MAX_PROPOSITION_CHARS: Final[int] = 500
MAX_FIELD_CHARS: Final[int] = 180
MAX_PROVENANCE_NAME_CHARS: Final[int] = 180
MAX_PROVENANCE_REFERENCES: Final[int] = 32

PUBLIC_PROVENANCE_ROLES: Final[tuple[str, ...]] = (
    "PUBLICATION",
    "PUBLISHER",
    "IMMEDIATE_ACQUIRED_SOURCE",
    "CITED_SOURCE",
    "QUOTED_SOURCE",
    "UNDERLYING_ORIGIN",
    "PROVENANCE_CONTEXT",
)
PUBLIC_ATTRIBUTION_STATES: Final[tuple[str, ...]] = (
    "OBSERVED",
    "ASSERTED",
    "UNRESOLVED",
    "MIXED",
)
PUBLIC_ENTITY_KINDS: Final[tuple[str, ...]] = (
    "PUBLICATION",
    "PUBLISHER",
    "SOURCE_ENDPOINT",
    "OFFICIAL_STATEMENT",
    "OFFICIAL_DOCUMENT",
    "WIRE_REPORT",
    "DATASET",
    "SOCIAL_POST",
    "USER_PROVIDED",
    "OTHER",
    "UNKNOWN",
    "MIXED",
)

OMITTED_FIELD_CLASSES: Final[tuple[str, ...]] = (
    "SECRETS",
    "AUTHENTICATION_MATERIAL",
    "OWNER_ADMIN_TOKENS",
    "PRIVATE_DATABASE_PATHS",
    "RAW_ITEM_CONTENT",
    "RAW_ITEM_IDENTIFIERS",
    "SOURCE_INTERNAL_IDENTIFIERS",
    "PROVENANCE_METADATA_JSON",
    "RAW_OPERATOR_FEEDBACK",
    "WATCH_QUERIES_AND_CADENCE",
    "DELIVERY_RETRY_DIAGNOSTICS",
    "UNNECESSARY_RUNTIME_METADATA",
    "NON_PUBLIC_OPERATIONAL_DIAGNOSTICS",
)

_SENSITIVE_PATTERNS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}"), "[REDACTED_AUTH]"),
    (
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password)\s*[:=]\s*[^\s,;]{4,}"
        ),
        "[REDACTED_SECRET]",
    ),
    (re.compile(r"(?i)\bfile://\S+"), "[REDACTED_PATH]"),
    (re.compile(r"(?i)\b[A-Z]:\\(?:[^\s\\]+\\)*[^\s]*"), "[REDACTED_PATH]"),
    (re.compile(r"(?i)(?<!\w)/(?:home|opt|var|tmp|mnt)/[^\s,;]+"), "[REDACTED_PATH]"),
)


@dataclass(frozen=True)
class PublicProvenanceReference:
    provenance_entity_version_id: str
    provenance_role: str
    attribution_state: str
    entity_kind: str
    canonical_name: str


@dataclass(frozen=True)
class PublicSemanticContent:
    normalized_proposition: str
    claimant_actor: str | None
    subject_text: str | None
    object_theme: str | None
    event_action_type: str | None
    polarity: str
    modality: str
    original_language: str


@dataclass(frozen=True)
class PublicSafeProjection:
    public_projection_id: str
    schema_version: str
    publication_candidate_id: str
    publication_policy_version: str
    live_claim_id: str
    semantic_claim_version_id: str
    verification_decision_version_id: str
    factual_confidence_version_id: str
    canonical_verification_state: str
    coverage_limitation: str
    reproducibility_state: str
    public_safety_state: str
    limitation_codes: tuple[str, ...]
    content: PublicSemanticContent
    provenance_references: tuple[PublicProvenanceReference, ...]
    redaction_status: str
    redaction_count: int
    omitted_field_classes: tuple[str, ...]

    @property
    def promotes_factual_verification(self) -> bool:
        return False

    @property
    def creates_independent_corroboration(self) -> bool:
        return False

    def as_public_dict(self) -> dict[str, object]:
        """Return only the explicit public allowlist represented by this schema."""

        return asdict(self)


@dataclass(frozen=True)
class PublicSafeProjectionBoundary:
    runtime_storage: str = "PROJECT_LOCAL_ONLY"
    mixed_shared_canonical_runtime: str = "BLOCKED"
    production_live: str = "NOT_OPERATIONAL"
    public_ingress: str = "NOT_APPROVED_NOT_DEPLOYED"
    public_sharing: str = "NOT_ACTIVE"
    paid_providers: str = "NONE_APPROVED"
    owner_execution: str = "DISABLED"
    activation_gate: str = "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


PUBLIC_SAFE_PROJECTION_BOUNDARY = PublicSafeProjectionBoundary()


def _sanitize_text(value: object | None, *, max_chars: int) -> tuple[str | None, int]:
    if value is None:
        return None, 0
    text = str(value).replace("\x00", " ")
    text = " ".join(text.split())
    redactions = 0
    for pattern, replacement in _SENSITIVE_PATTERNS:
        text, count = pattern.subn(replacement, text)
        redactions += count
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "…"
        redactions += 1
    return text, redactions


def _sanitize_required(value: object, *, max_chars: int, field_name: str) -> tuple[str, int]:
    text, redactions = _sanitize_text(value, max_chars=max_chars)
    if not text:
        raise ValueError(f"public-safe required field became empty: {field_name}")
    return text, redactions


def _validated_provenance_references(
    references: Iterable[PublicProvenanceReference],
) -> tuple[tuple[PublicProvenanceReference, ...], int]:
    safe: list[PublicProvenanceReference] = []
    redactions = 0
    for reference in references:
        if reference.provenance_role not in PUBLIC_PROVENANCE_ROLES:
            raise ValueError(f"unsupported provenance_role: {reference.provenance_role}")
        if reference.attribution_state not in PUBLIC_ATTRIBUTION_STATES:
            raise ValueError(f"unsupported attribution_state: {reference.attribution_state}")
        if reference.entity_kind not in PUBLIC_ENTITY_KINDS:
            raise ValueError(f"unsupported entity_kind: {reference.entity_kind}")
        name, changed = _sanitize_required(
            reference.canonical_name,
            max_chars=MAX_PROVENANCE_NAME_CHARS,
            field_name="canonical_name",
        )
        redactions += changed
        safe.append(
            PublicProvenanceReference(
                provenance_entity_version_id=str(reference.provenance_entity_version_id),
                provenance_role=reference.provenance_role,
                attribution_state=reference.attribution_state,
                entity_kind=reference.entity_kind,
                canonical_name=name,
            )
        )
        if len(safe) >= MAX_PROVENANCE_REFERENCES:
            break
    safe.sort(
        key=lambda item: (
            item.provenance_role,
            item.attribution_state,
            item.entity_kind,
            item.provenance_entity_version_id,
        )
    )
    return tuple(safe), redactions


def project_public_safe(
    eligibility: PublicationEligibilityDecision,
    *,
    normalized_proposition: str,
    claimant_actor: str | None,
    subject_text: str | None,
    object_theme: str | None,
    event_action_type: str | None,
    polarity: str,
    modality: str,
    original_language: str,
    provenance_references: Iterable[PublicProvenanceReference],
) -> PublicSafeProjection:
    """Create a deterministic allowlisted projection from an eligible decision."""

    if eligibility.eligibility_state != "ELIGIBLE":
        raise ValueError("publication eligibility must be ELIGIBLE")
    if eligibility.public_safety_state != "ALLOWED":
        raise ValueError("public safety state must be ALLOWED")
    required_ids = (
        eligibility.semantic_claim_version_id,
        eligibility.verification_decision_version_id,
        eligibility.factual_confidence_version_id,
    )
    if any(value is None or not str(value).strip() for value in required_ids):
        raise ValueError("eligible decision is missing canonical identifiers")
    if eligibility.canonical_verification_state != "VERIFIED":
        raise ValueError("eligible decision must preserve canonical VERIFIED state")
    if eligibility.coverage_limitation not in ("UNKNOWN", "LIMITED", "ADEQUATE"):
        raise ValueError("eligible decision is missing a valid coverage limitation")

    proposition, redactions = _sanitize_required(
        normalized_proposition,
        max_chars=MAX_PROPOSITION_CHARS,
        field_name="normalized_proposition",
    )
    claimant, count = _sanitize_text(claimant_actor, max_chars=MAX_FIELD_CHARS)
    redactions += count
    subject, count = _sanitize_text(subject_text, max_chars=MAX_FIELD_CHARS)
    redactions += count
    theme, count = _sanitize_text(object_theme, max_chars=MAX_FIELD_CHARS)
    redactions += count
    action, count = _sanitize_text(event_action_type, max_chars=MAX_FIELD_CHARS)
    redactions += count
    language, count = _sanitize_required(
        original_language, max_chars=32, field_name="original_language"
    )
    redactions += count

    normalized_polarity = str(polarity).strip().upper()
    normalized_modality = str(modality).strip().upper()
    if normalized_polarity not in ("AFFIRMATIVE", "NEGATED", "UNKNOWN"):
        raise ValueError(f"unsupported polarity: {normalized_polarity}")
    if normalized_modality not in (
        "ASSERTED",
        "REPORTED",
        "ALLEGED",
        "DENIED",
        "ESTIMATED",
        "QUESTIONED",
        "UNKNOWN",
    ):
        raise ValueError(f"unsupported modality: {normalized_modality}")

    provenance, count = _validated_provenance_references(provenance_references)
    redactions += count

    content = PublicSemanticContent(
        normalized_proposition=proposition,
        claimant_actor=claimant,
        subject_text=subject,
        object_theme=theme,
        event_action_type=action,
        polarity=normalized_polarity,
        modality=normalized_modality,
        original_language=language,
    )
    identity = {
        "schema_version": PUBLIC_SAFE_PROJECTION_VERSION,
        "publication_candidate_id": eligibility.publication_candidate_id,
        "semantic_claim_version_id": eligibility.semantic_claim_version_id,
        "verification_decision_version_id": eligibility.verification_decision_version_id,
        "factual_confidence_version_id": eligibility.factual_confidence_version_id,
        "content": asdict(content),
        "provenance_references": [asdict(item) for item in provenance],
        "limitation_codes": list(eligibility.limitation_codes),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    projection_id = "public-projection-" + sha256(encoded.encode("utf-8")).hexdigest()[:24]

    return PublicSafeProjection(
        public_projection_id=projection_id,
        schema_version=PUBLIC_SAFE_PROJECTION_VERSION,
        publication_candidate_id=eligibility.publication_candidate_id,
        publication_policy_version=eligibility.policy_version,
        live_claim_id=eligibility.live_claim_id,
        semantic_claim_version_id=str(eligibility.semantic_claim_version_id),
        verification_decision_version_id=str(eligibility.verification_decision_version_id),
        factual_confidence_version_id=str(eligibility.factual_confidence_version_id),
        canonical_verification_state=eligibility.canonical_verification_state,
        coverage_limitation=eligibility.coverage_limitation,
        reproducibility_state=eligibility.reproducibility_state,
        public_safety_state=eligibility.public_safety_state,
        limitation_codes=eligibility.limitation_codes,
        content=content,
        provenance_references=provenance,
        redaction_status="APPLIED" if redactions else "NOT_REQUIRED",
        redaction_count=redactions,
        omitted_field_classes=OMITTED_FIELD_CLASSES,
    )


class PublicSafeProjectionService:
    """Read-only projection service over exact P13 semantic/provenance versions."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path

    def project(self, eligibility: PublicationEligibilityDecision) -> PublicSafeProjection:
        semantic_claim_version_id = eligibility.semantic_claim_version_id
        if not semantic_claim_version_id:
            raise ValueError("eligibility has no semantic_claim_version_id")

        with runtime_database_connection(self.database_path) as connection:
            claim = connection.execute(
                """SELECT normalized_proposition,claimant_actor,subject_text,object_theme,
                          event_action_type,polarity,modality,original_language
                   FROM semantic_claim_versions
                   WHERE semantic_claim_version_id=?""",
                (semantic_claim_version_id,),
            ).fetchone()
            if claim is None:
                raise ValueError("canonical semantic claim version is unavailable")

            rows = connection.execute(
                """SELECT r.provenance_entity_version_id,r.provenance_role,
                          r.attribution_state,e.entity_kind,e.canonical_name
                   FROM semantic_claim_provenance_role_versions AS r
                   JOIN semantic_provenance_entity_versions AS e
                     ON e.provenance_entity_version_id=r.provenance_entity_version_id
                   WHERE r.semantic_claim_version_id=?
                     AND r.role_version=(
                         SELECT MAX(r2.role_version)
                         FROM semantic_claim_provenance_role_versions AS r2
                         WHERE r2.semantic_claim_version_id=r.semantic_claim_version_id
                           AND r2.claim_provenance_role_id=r.claim_provenance_role_id
                     )
                   ORDER BY r.provenance_role,r.attribution_state,e.entity_kind,
                            r.provenance_entity_version_id""",
                (semantic_claim_version_id,),
            ).fetchall()

        references = tuple(
            PublicProvenanceReference(
                provenance_entity_version_id=str(row[0]),
                provenance_role=str(row[1]),
                attribution_state=str(row[2]),
                entity_kind=str(row[3]),
                canonical_name=str(row[4]),
            )
            for row in rows
        )
        return project_public_safe(
            eligibility,
            normalized_proposition=str(claim[0]),
            claimant_actor=None if claim[1] is None else str(claim[1]),
            subject_text=None if claim[2] is None else str(claim[2]),
            object_theme=None if claim[3] is None else str(claim[3]),
            event_action_type=None if claim[4] is None else str(claim[4]),
            polarity=str(claim[5]),
            modality=str(claim[6]),
            original_language=str(claim[7]),
            provenance_references=references,
        )


__all__ = [
    "PUBLIC_SAFE_PROJECTION_VERSION",
    "P17_2_GATE",
    "P17_2_MIGRATION",
    "OMITTED_FIELD_CLASSES",
    "PublicProvenanceReference",
    "PublicSemanticContent",
    "PublicSafeProjection",
    "PublicSafeProjectionBoundary",
    "PUBLIC_SAFE_PROJECTION_BOUNDARY",
    "PublicSafeProjectionService",
    "project_public_safe",
]
