"""Phase 17.4 provider-neutral local/test publication target.

Only deterministic local/in-memory target behavior is implemented. No network,
provider credential, public endpoint or external publication is activated.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Final, Protocol

from .release_manifest import PublicationPackage


PUBLICATION_TARGET_VERSION: Final[str] = "KGM_PROVIDER_NEUTRAL_PUBLICATION_TARGET_V1"
P17_4_GATE: Final[str] = "P17_4_PROVIDER_NEUTRAL_PUBLICATION_TARGET_VALIDATED"
P17_4_MIGRATION: Final[str] = "NONE"


@dataclass(frozen=True)
class PublicationTargetReceipt:
    receipt_id: str
    target_key: str
    release_id: str
    manifest_id: str
    payload_sha256: str
    status: str
    duplicate: bool
    detail: str | None = None

    @property
    def factual_verification_effect(self) -> str:
        return "NONE"

    @property
    def publication_evidence_only(self) -> bool:
        return True


class PublicationTarget(Protocol):
    target_key: str

    def publish(self, package: PublicationPackage) -> PublicationTargetReceipt:
        ...


class InMemoryPublicationTarget:
    """Deterministic test sink with idempotent release handling."""

    def __init__(self, target_key: str = "LOCAL_TEST_SINK") -> None:
        key = str(target_key).strip()
        if not key:
            raise ValueError("target_key is required")
        self.target_key = key
        self._receipts_by_release: dict[str, PublicationTargetReceipt] = {}

    @staticmethod
    def _receipt_id(target_key: str, package: PublicationPackage) -> str:
        identity = {
            "target_key": target_key,
            "release_id": package.release_id,
            "manifest_id": package.manifest.release_manifest_id,
            "payload_sha256": package.manifest.payload_sha256,
        }
        encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"))
        return "publication-receipt-" + sha256(encoded.encode("utf-8")).hexdigest()[:24]

    def publish(self, package: PublicationPackage) -> PublicationTargetReceipt:
        if not package.release_id or not package.manifest.release_manifest_id:
            raise ValueError("publication package identity is incomplete")
        existing = self._receipts_by_release.get(package.release_id)
        if existing is not None:
            return PublicationTargetReceipt(
                receipt_id=existing.receipt_id,
                target_key=existing.target_key,
                release_id=existing.release_id,
                manifest_id=existing.manifest_id,
                payload_sha256=existing.payload_sha256,
                status=existing.status,
                duplicate=True,
                detail="IDEMPOTENT_DUPLICATE_SUPPRESSED",
            )
        receipt = PublicationTargetReceipt(
            receipt_id=self._receipt_id(self.target_key, package),
            target_key=self.target_key,
            release_id=package.release_id,
            manifest_id=package.manifest.release_manifest_id,
            payload_sha256=package.manifest.payload_sha256,
            status="ACCEPTED_LOCAL_TEST_ONLY",
            duplicate=False,
        )
        self._receipts_by_release[package.release_id] = receipt
        return receipt

    def receipt_for(self, release_id: str) -> PublicationTargetReceipt | None:
        return self._receipts_by_release.get(str(release_id))

    @property
    def accepted_count(self) -> int:
        return len(self._receipts_by_release)


class FailingTestPublicationTarget:
    """Test-only failure target proving isolation; never performs I/O."""

    target_key = "LOCAL_TEST_FAILURE_SINK"

    def publish(self, package: PublicationPackage) -> PublicationTargetReceipt:
        raise RuntimeError(f"simulated publication target failure for {package.release_id}")


@dataclass(frozen=True)
class PublicationTargetBoundary:
    runtime_storage: str = "PROJECT_LOCAL_ONLY"
    target_mode: str = "LOCAL_TEST_ONLY"
    external_targets: str = "NOT_ACTIVATED"
    public_ingress: str = "NOT_APPROVED_NOT_DEPLOYED"
    production_live: str = "NOT_OPERATIONAL"
    public_sharing: str = "NOT_ACTIVE"
    paid_providers: str = "NONE_APPROVED"
    activation_gate: str = "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


PUBLICATION_TARGET_BOUNDARY = PublicationTargetBoundary()


__all__ = [
    "PUBLICATION_TARGET_VERSION",
    "P17_4_GATE",
    "P17_4_MIGRATION",
    "PublicationTargetReceipt",
    "PublicationTarget",
    "InMemoryPublicationTarget",
    "FailingTestPublicationTarget",
    "PublicationTargetBoundary",
    "PUBLICATION_TARGET_BOUNDARY",
]
