"""Phase 17.3 release manifest, provenance and reproducibility contract.

Builds deterministic publication release manifests from an already validated
P17.2 public-safe projection. The manifest is a derived, local-only object: it
never publishes, mutates canonical intelligence, reconstructs missing history,
or activates a target/provider.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Final, Iterable

from .public_safe_projection import PublicSafeProjection


RELEASE_MANIFEST_VERSION: Final[str] = "KGM_RELEASE_MANIFEST_V1"
P17_3_GATE: Final[str] = "P17_3_RELEASE_MANIFEST_PROVENANCE_VALIDATED"
P17_3_MIGRATION: Final[str] = "NONE"
MAX_REPRODUCIBILITY_REFERENCES: Final[int] = 32


@dataclass(frozen=True)
class ReleaseManifest:
    release_manifest_id: str
    schema_version: str
    publication_policy_version: str
    public_projection_id: str
    publication_candidate_id: str
    semantic_claim_version_id: str
    verification_decision_version_id: str
    factual_confidence_version_id: str
    canonical_verification_state: str
    coverage_limitation: str
    reproducibility_state: str
    reproducibility_references: tuple[str, ...]
    reproducibility_limitation: str | None
    provenance_roles: tuple[str, ...]
    limitation_codes: tuple[str, ...]
    redaction_status: str
    payload_sha256: str
    generated_at: str

    @property
    def promotes_factual_verification(self) -> bool:
        return False

    @property
    def proves_underlying_origin(self) -> bool:
        return False

    @property
    def reconstructed_exact_history(self) -> bool:
        return False


@dataclass(frozen=True)
class PublicationPackage:
    release_id: str
    manifest: ReleaseManifest
    public_payload: dict[str, object]


@dataclass(frozen=True)
class ReleaseManifestBoundary:
    runtime_storage: str = "PROJECT_LOCAL_ONLY"
    mixed_shared_canonical_runtime: str = "BLOCKED"
    production_live: str = "NOT_OPERATIONAL"
    public_ingress: str = "NOT_APPROVED_NOT_DEPLOYED"
    public_sharing: str = "NOT_ACTIVE"
    paid_providers: str = "NONE_APPROVED"
    activation_gate: str = "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


RELEASE_MANIFEST_BOUNDARY = ReleaseManifestBoundary()


def _stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _normalized_reproducibility_references(
    projection: PublicSafeProjection,
    references: Iterable[str],
) -> tuple[tuple[str, ...], str | None]:
    normalized = tuple(sorted({str(item).strip() for item in references if str(item).strip()}))
    if len(normalized) > MAX_REPRODUCIBILITY_REFERENCES:
        raise ValueError("too many reproducibility references")

    state = str(projection.reproducibility_state).strip().upper()
    if state in {"NOT_INSTRUMENTED", "UNAVAILABLE", "UNKNOWN", ""}:
        if normalized:
            raise ValueError("exact reproducibility references require persisted instrumentation")
        return (), "EXACT_HISTORY_NOT_INSTRUMENTED_OR_UNAVAILABLE"

    if not normalized:
        return (), "PERSISTED_REPRODUCIBILITY_REFERENCE_NOT_SUPPLIED"
    return normalized, None


def build_release_manifest(
    projection: PublicSafeProjection,
    *,
    generated_at: str,
    reproducibility_references: Iterable[str] = (),
) -> ReleaseManifest:
    """Build a deterministic manifest over the exact public-safe payload."""

    if projection.schema_version != "KGM_PUBLIC_SAFE_PROJECTION_V1":
        raise ValueError("unsupported public-safe projection version")
    if projection.canonical_verification_state != "VERIFIED":
        raise ValueError("release manifest requires canonical VERIFIED projection")
    if projection.public_safety_state != "ALLOWED":
        raise ValueError("release manifest requires public safety ALLOWED")
    if projection.redaction_status not in {"NOT_REQUIRED", "APPLIED"}:
        raise ValueError("projection redaction status is invalid")
    generated = str(generated_at).strip()
    if not generated:
        raise ValueError("generated_at is required")

    payload = projection.as_public_dict()
    payload_sha = sha256(_stable_json(payload).encode("utf-8")).hexdigest()
    repro_refs, repro_limitation = _normalized_reproducibility_references(
        projection, reproducibility_references
    )
    provenance_roles = tuple(sorted({item.provenance_role for item in projection.provenance_references}))

    identity = {
        "schema_version": RELEASE_MANIFEST_VERSION,
        "publication_policy_version": projection.publication_policy_version,
        "public_projection_id": projection.public_projection_id,
        "publication_candidate_id": projection.publication_candidate_id,
        "semantic_claim_version_id": projection.semantic_claim_version_id,
        "verification_decision_version_id": projection.verification_decision_version_id,
        "factual_confidence_version_id": projection.factual_confidence_version_id,
        "coverage_limitation": projection.coverage_limitation,
        "reproducibility_state": projection.reproducibility_state,
        "reproducibility_references": repro_refs,
        "reproducibility_limitation": repro_limitation,
        "provenance_roles": provenance_roles,
        "limitation_codes": projection.limitation_codes,
        "redaction_status": projection.redaction_status,
        "payload_sha256": payload_sha,
        "generated_at": generated,
    }
    manifest_id = "release-manifest-" + sha256(_stable_json(identity).encode("utf-8")).hexdigest()[:24]
    return ReleaseManifest(
        release_manifest_id=manifest_id,
        schema_version=RELEASE_MANIFEST_VERSION,
        publication_policy_version=projection.publication_policy_version,
        public_projection_id=projection.public_projection_id,
        publication_candidate_id=projection.publication_candidate_id,
        semantic_claim_version_id=projection.semantic_claim_version_id,
        verification_decision_version_id=projection.verification_decision_version_id,
        factual_confidence_version_id=projection.factual_confidence_version_id,
        canonical_verification_state=projection.canonical_verification_state,
        coverage_limitation=projection.coverage_limitation,
        reproducibility_state=projection.reproducibility_state,
        reproducibility_references=repro_refs,
        reproducibility_limitation=repro_limitation,
        provenance_roles=provenance_roles,
        limitation_codes=projection.limitation_codes,
        redaction_status=projection.redaction_status,
        payload_sha256=payload_sha,
        generated_at=generated,
    )


def build_publication_package(
    projection: PublicSafeProjection,
    *,
    generated_at: str,
    reproducibility_references: Iterable[str] = (),
) -> PublicationPackage:
    manifest = build_release_manifest(
        projection,
        generated_at=generated_at,
        reproducibility_references=reproducibility_references,
    )
    package_identity = {
        "manifest": asdict(manifest),
        "public_payload": projection.as_public_dict(),
    }
    release_id = "release-" + sha256(_stable_json(package_identity).encode("utf-8")).hexdigest()[:24]
    return PublicationPackage(
        release_id=release_id,
        manifest=manifest,
        public_payload=projection.as_public_dict(),
    )


__all__ = [
    "RELEASE_MANIFEST_VERSION",
    "P17_3_GATE",
    "P17_3_MIGRATION",
    "ReleaseManifest",
    "PublicationPackage",
    "ReleaseManifestBoundary",
    "RELEASE_MANIFEST_BOUNDARY",
    "build_release_manifest",
    "build_publication_package",
]
