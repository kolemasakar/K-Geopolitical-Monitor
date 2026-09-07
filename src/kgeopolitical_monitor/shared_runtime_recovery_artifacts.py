"""Additive P18.7 artifact-level recovery hardening.

The base P18.7 contract in :mod:`shared_runtime_recovery` defines provider-neutral
manifest/restore/rollback evidence.  This module strengthens that contract with
an opaque encrypted-artifact envelope, deterministic tenant-scoped record
snapshots, actual clean-target restore semantics, logical recovery-point
selection, and failure-based measured RPO/RTO evidence.

No concrete cryptographic algorithm, provider, off-host storage service, shared
datastore, migration, cutover or activation is implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .shared_runtime_contract import TenantContext
from .shared_runtime_recovery import (
    BackupContractError,
    RestoreContractError,
    SharedBackupManifest,
)


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_SCHEMES = {"", "none", "plaintext", "identity", "unencrypted"}


class ArtifactIntegrityError(RestoreContractError):
    """Raised when protected artifact or decoded snapshot integrity fails."""


class ArtifactTenantIsolationError(RestoreContractError):
    """Raised when backup/restore/recovery-point scope can cross a tenant."""


class RecoveryTargetNotCleanError(RestoreContractError):
    """Raised when a clean-environment restore would overwrite state."""


class RecoveryPointSelectionError(RestoreContractError):
    """Raised when no unambiguous durable logical recovery point is available."""


class RecoveryObjectiveMeasurementError(RestoreContractError):
    """Raised when recovery-objective evidence is invalid or assumed."""


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise BackupContractError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise BackupContractError(f"{field_name} is required")
    return normalized


def _utc(value: datetime, *, field_name: str, error_type=RestoreContractError) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise error_type(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _sha256_hex(value: str, *, field_name: str, error_type=ArtifactIntegrityError) -> str:
    digest = str(value).strip().lower()
    if not _SHA256_RE.fullmatch(digest):
        raise error_type(f"{field_name} must be a 64-character SHA-256 hex digest")
    return digest


def _canonical_json(value: Any, *, field_name: str) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise BackupContractError(f"{field_name} must be canonical JSON data") from exc


def _same_tenant(left: TenantContext, right: TenantContext) -> bool:
    return left.workspace_id == right.workspace_id and left.project_id == right.project_id


@dataclass(frozen=True)
class RecoveryRecordSnapshot:
    """Immutable recovery representation of one tenant-scoped object."""

    workspace_id: str
    project_id: str
    object_type: str
    object_id: str
    payload_json: str

    def __post_init__(self) -> None:
        for name in ("workspace_id", "project_id", "object_type", "object_id"):
            object.__setattr__(self, name, _required_text(getattr(self, name), field_name=name))
        try:
            decoded = json.loads(self.payload_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise BackupContractError("payload_json must contain valid JSON") from exc
        object.__setattr__(self, "payload_json", _canonical_json(decoded, field_name="payload_json"))

    @classmethod
    def from_payload(
        cls,
        *,
        tenant_context: TenantContext,
        object_type: str,
        object_id: str,
        payload: Mapping[str, Any],
    ) -> "RecoveryRecordSnapshot":
        if not isinstance(tenant_context, TenantContext):
            raise BackupContractError("record snapshot requires explicit TenantContext")
        if not isinstance(payload, Mapping):
            raise BackupContractError("record snapshot payload must be a mapping")
        return cls(
            workspace_id=tenant_context.workspace_id,
            project_id=tenant_context.project_id,
            object_type=object_type,
            object_id=object_id,
            payload_json=_canonical_json(dict(payload), field_name="payload"),
        )

    @property
    def tenant_context(self) -> TenantContext:
        return TenantContext(workspace_id=self.workspace_id, project_id=self.project_id)


@dataclass(frozen=True)
class TenantRecoverySnapshot:
    """Deterministic exact-tenant recovery payload bound to one checkpoint."""

    tenant_context: TenantContext
    schema_version: int
    checkpoint_id: str
    captured_at: datetime
    records: tuple[RecoveryRecordSnapshot, ...]
    content_sha256: str = field(init=False)
    row_counts: tuple[tuple[str, int], ...] = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_context, TenantContext):
            raise BackupContractError("recovery snapshot requires explicit TenantContext")
        if not isinstance(self.schema_version, int) or isinstance(self.schema_version, bool) or self.schema_version <= 0:
            raise BackupContractError("schema_version must be a positive integer")
        object.__setattr__(self, "checkpoint_id", _required_text(self.checkpoint_id, field_name="checkpoint_id"))
        object.__setattr__(self, "captured_at", _utc(self.captured_at, field_name="captured_at"))

        normalized = tuple(sorted(self.records, key=lambda row: (row.object_type, row.object_id)))
        identities: set[tuple[str, str]] = set()
        counts: dict[str, int] = {}
        for row in normalized:
            if not isinstance(row, RecoveryRecordSnapshot):
                raise BackupContractError("snapshot records must be RecoveryRecordSnapshot values")
            if not _same_tenant(row.tenant_context, self.tenant_context):
                raise ArtifactTenantIsolationError("recovery snapshot cannot mix workspace/project tenants")
            identity = (row.object_type, row.object_id)
            if identity in identities:
                raise BackupContractError("recovery snapshot contains a duplicate object identity")
            identities.add(identity)
            counts[row.object_type] = counts.get(row.object_type, 0) + 1
        object.__setattr__(self, "records", normalized)
        object.__setattr__(self, "row_counts", tuple(sorted(counts.items())))

        canonical = {
            "workspace_id": self.tenant_context.workspace_id,
            "project_id": self.tenant_context.project_id,
            "schema_version": self.schema_version,
            "checkpoint_id": self.checkpoint_id,
            "captured_at": self.captured_at.isoformat(),
            "records": [
                {
                    "object_type": row.object_type,
                    "object_id": row.object_id,
                    "payload_json": row.payload_json,
                }
                for row in normalized
            ],
        }
        digest = sha256(_canonical_json(canonical, field_name="snapshot").encode("utf-8")).hexdigest()
        object.__setattr__(self, "content_sha256", digest)


@dataclass(frozen=True)
class EncryptedBackupArtifact:
    """Opaque encrypted payload envelope bound to a validated P18.7 manifest.

    ``ciphertext`` is private material and intentionally omitted from repr.  The
    envelope validates bytes/integrity/binding, not cryptographic strength.
    """

    manifest: SharedBackupManifest
    encryption_scheme: str
    ciphertext: bytes = field(repr=False)
    ciphertext_sha256: str = ""
    provider_id: None = field(default=None, init=False)
    contract_only: bool = field(default=True, init=False)
    off_host_storage_observed: bool = field(default=False, init=False)
    cryptographic_adapter_observed: bool = field(default=False, init=False)
    provider_pitr_observed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.manifest, SharedBackupManifest):
            raise BackupContractError("artifact requires a validated SharedBackupManifest")
        scheme = _required_text(self.encryption_scheme, field_name="encryption_scheme")
        if scheme.casefold() in _FORBIDDEN_SCHEMES:
            raise BackupContractError("artifact must declare an encrypted payload scheme")
        object.__setattr__(self, "encryption_scheme", scheme)
        if not isinstance(self.ciphertext, bytes) or not self.ciphertext:
            raise BackupContractError("encrypted artifact ciphertext must be non-empty bytes")
        expected = _sha256_hex(self.ciphertext_sha256, field_name="ciphertext_sha256")
        actual = sha256(self.ciphertext).hexdigest()
        if actual != expected:
            raise ArtifactIntegrityError("ciphertext SHA-256 does not match artifact metadata")
        object.__setattr__(self, "ciphertext_sha256", expected)


@runtime_checkable
class EncryptedBackupCodec(Protocol):
    """Future adapter boundary; P18.7 ships no concrete cryptographic codec."""

    @property
    def codec_id(self) -> str:
        """Stable codec identifier."""

    def open(self, artifact: EncryptedBackupArtifact) -> TenantRecoverySnapshot:
        """Decrypt and verify an artifact into an exact tenant snapshot."""


def verify_artifact_snapshot_binding(
    *,
    artifact: EncryptedBackupArtifact,
    snapshot: TenantRecoverySnapshot,
) -> TenantRecoverySnapshot:
    if not isinstance(artifact, EncryptedBackupArtifact):
        raise BackupContractError("EncryptedBackupArtifact is required")
    if not isinstance(snapshot, TenantRecoverySnapshot):
        raise ArtifactIntegrityError("codec did not return TenantRecoverySnapshot")
    manifest = artifact.manifest
    if not _same_tenant(manifest.tenant_context, snapshot.tenant_context):
        raise ArtifactTenantIsolationError("decoded snapshot tenant differs from backup manifest")
    if manifest.schema_version != snapshot.schema_version:
        raise ArtifactIntegrityError("decoded snapshot schema differs from backup manifest")
    if manifest.checkpoint_id != snapshot.checkpoint_id:
        raise ArtifactIntegrityError("decoded snapshot checkpoint differs from backup manifest")
    if manifest.content_sha256 != snapshot.content_sha256:
        raise ArtifactIntegrityError("decoded snapshot SHA-256 differs from backup manifest")
    if dict(manifest.row_counts) != dict(snapshot.row_counts):
        raise ArtifactIntegrityError("decoded snapshot row counts differ from backup manifest")
    return snapshot


class InMemoryCleanRestoreTarget:
    """Provider-free clean restore harness with actual record reconciliation."""

    def __init__(self, *, tenant_context: TenantContext, schema_version: int) -> None:
        if not isinstance(tenant_context, TenantContext):
            raise RestoreContractError("restore target requires explicit TenantContext")
        if not isinstance(schema_version, int) or isinstance(schema_version, bool) or schema_version <= 0:
            raise RestoreContractError("restore target schema_version must be positive")
        self.tenant_context = tenant_context
        self.schema_version = schema_version
        self._records: tuple[RecoveryRecordSnapshot, ...] = ()
        self._content_sha256: str | None = None

    @property
    def is_clean(self) -> bool:
        return not self._records and self._content_sha256 is None

    @property
    def records(self) -> tuple[RecoveryRecordSnapshot, ...]:
        return self._records

    @property
    def restored_content_sha256(self) -> str | None:
        return self._content_sha256

    def restore(self, snapshot: TenantRecoverySnapshot) -> tuple[RecoveryRecordSnapshot, ...]:
        if not self.is_clean:
            raise RecoveryTargetNotCleanError("clean restore target cannot overwrite existing state")
        if not isinstance(snapshot, TenantRecoverySnapshot):
            raise RestoreContractError("restore requires TenantRecoverySnapshot")
        if not _same_tenant(snapshot.tenant_context, self.tenant_context):
            raise ArtifactTenantIsolationError("clean restore cannot cross workspace/project tenant")
        if snapshot.schema_version != self.schema_version:
            raise ArtifactIntegrityError("clean restore target schema is incompatible")
        self._records = tuple(snapshot.records)
        self._content_sha256 = snapshot.content_sha256
        return self._records


def restore_encrypted_artifact(
    *,
    artifact: EncryptedBackupArtifact,
    codec: EncryptedBackupCodec,
    target: InMemoryCleanRestoreTarget,
) -> tuple[RecoveryRecordSnapshot, ...]:
    if not isinstance(codec, EncryptedBackupCodec):
        raise BackupContractError("restore requires an EncryptedBackupCodec")
    if not isinstance(target, InMemoryCleanRestoreTarget):
        raise RestoreContractError("restore requires InMemoryCleanRestoreTarget")
    snapshot = verify_artifact_snapshot_binding(artifact=artifact, snapshot=codec.open(artifact))
    return target.restore(snapshot)


@dataclass(frozen=True)
class LogicalRecoveryPoint:
    tenant_context: TenantContext
    durable_at: datetime
    sequence: int
    snapshot: TenantRecoverySnapshot

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_context, TenantContext):
            raise RecoveryPointSelectionError("recovery point requires explicit TenantContext")
        object.__setattr__(
            self,
            "durable_at",
            _utc(self.durable_at, field_name="durable_at", error_type=RecoveryPointSelectionError),
        )
        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise RecoveryPointSelectionError("recovery point sequence must be non-negative")
        if not isinstance(self.snapshot, TenantRecoverySnapshot):
            raise RecoveryPointSelectionError("recovery point requires TenantRecoverySnapshot")
        if not _same_tenant(self.tenant_context, self.snapshot.tenant_context):
            raise ArtifactTenantIsolationError("recovery point cannot bind another tenant snapshot")


def select_logical_recovery_point(
    *,
    tenant_context: TenantContext,
    points: Sequence[LogicalRecoveryPoint],
    target_at: datetime,
) -> LogicalRecoveryPoint:
    """Return the latest durable logical point at/before ``target_at``.

    This proves checkpoint-selection semantics only; it does not claim provider
    WAL/PITR availability.
    """

    if not isinstance(tenant_context, TenantContext):
        raise RecoveryPointSelectionError("selection requires explicit TenantContext")
    target = _utc(target_at, field_name="target_at", error_type=RecoveryPointSelectionError)
    candidates: list[LogicalRecoveryPoint] = []
    for point in points:
        if not isinstance(point, LogicalRecoveryPoint):
            raise RecoveryPointSelectionError("points must contain LogicalRecoveryPoint values")
        if not _same_tenant(point.tenant_context, tenant_context):
            raise ArtifactTenantIsolationError("recovery-point set cannot mix tenants")
        if point.durable_at <= target:
            candidates.append(point)
    if not candidates:
        raise RecoveryPointSelectionError("no durable recovery point exists at or before target")
    return max(candidates, key=lambda point: (point.durable_at, point.sequence))


@dataclass(frozen=True)
class MeasuredRecoveryObjectiveEvidence:
    """Failure-based measured recovery evidence, not an SLA or target."""

    last_durable_recovery_point_at: datetime
    failure_at: datetime
    restore_started_at: datetime
    restore_completed_at: datetime
    measured_rpo_seconds: float = field(init=False)
    measured_rto_seconds: float = field(init=False)
    service_level_claim_authorized: bool = field(default=False, init=False)
    provider_pitr_observed: bool = field(default=False, init=False)
    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        durable = _utc(
            self.last_durable_recovery_point_at,
            field_name="last_durable_recovery_point_at",
            error_type=RecoveryObjectiveMeasurementError,
        )
        failure = _utc(self.failure_at, field_name="failure_at", error_type=RecoveryObjectiveMeasurementError)
        started = _utc(
            self.restore_started_at,
            field_name="restore_started_at",
            error_type=RecoveryObjectiveMeasurementError,
        )
        completed = _utc(
            self.restore_completed_at,
            field_name="restore_completed_at",
            error_type=RecoveryObjectiveMeasurementError,
        )
        if not durable <= failure <= started <= completed:
            raise RecoveryObjectiveMeasurementError("recovery timestamps must be monotonic")
        object.__setattr__(self, "last_durable_recovery_point_at", durable)
        object.__setattr__(self, "failure_at", failure)
        object.__setattr__(self, "restore_started_at", started)
        object.__setattr__(self, "restore_completed_at", completed)
        object.__setattr__(self, "measured_rpo_seconds", (failure - durable).total_seconds())
        object.__setattr__(self, "measured_rto_seconds", (completed - failure).total_seconds())


def public_artifact_metadata(artifact: EncryptedBackupArtifact) -> dict[str, object]:
    """Data-minimized metadata: no ciphertext and no secret/key locator."""

    if not isinstance(artifact, EncryptedBackupArtifact):
        raise BackupContractError("EncryptedBackupArtifact is required")
    manifest = artifact.manifest
    return {
        "backup_id": manifest.backup_id,
        "workspace_id": manifest.tenant_context.workspace_id,
        "project_id": manifest.tenant_context.project_id,
        "schema_version": manifest.schema_version,
        "schema_contract_id": manifest.schema_contract_id,
        "captured_at": manifest.captured_at.isoformat(),
        "checkpoint_id": manifest.checkpoint_id,
        "content_sha256": manifest.content_sha256,
        "row_counts": manifest.row_counts,
        "encryption_scheme": artifact.encryption_scheme,
        "ciphertext_sha256": artifact.ciphertext_sha256,
        "off_host_copy_required": manifest.off_host_copy,
        "off_host_storage_observed": artifact.off_host_storage_observed,
        "provider_id": artifact.provider_id,
        "contract_only": artifact.contract_only,
        "provider_pitr_observed": artifact.provider_pitr_observed,
        "canonical_cutover_authorized": False,
        "shared_runtime_activated": False,
        "factual_verification_authority": False,
    }
