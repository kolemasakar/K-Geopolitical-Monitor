"""P18.7 provider-neutral shared-runtime backup, DR and rollback contracts.

This module deliberately does not provision a shared datastore, implement a
cryptographic primitive, select a backup provider, allocate a repository
migration number, or activate shared runtime.  It defines the fail-closed
contracts a later provider adapter must satisfy.

Encrypted backup payloads are opaque bytes accompanied by integrity metadata
and an external ``SecretReference``.  A concrete cryptographic implementation,
off-host storage, provider PITR/WAL and network evidence remain later
non-production/activation-readiness evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .shared_runtime_contract import StorageScope, TenantContext
from .shared_runtime_security import SecretReference


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_ENCRYPTION_SCHEMES = {"", "none", "plaintext", "identity", "unencrypted"}


class SharedRuntimeRecoveryError(RuntimeError):
    """Base error for fail-closed P18.7 recovery processing."""


class BackupContractError(SharedRuntimeRecoveryError, ValueError):
    """Raised when backup metadata or an encrypted artifact is invalid."""


class BackupIntegrityError(SharedRuntimeRecoveryError):
    """Raised when backup integrity or decoded snapshot identity does not match."""


class RestoreIsolationError(SharedRuntimeRecoveryError):
    """Raised when a restore could cross workspace/project ownership boundaries."""


class RestoreTargetNotCleanError(SharedRuntimeRecoveryError):
    """Raised when a restore target is not a clean environment."""


class RecoveryPointError(SharedRuntimeRecoveryError, ValueError):
    """Raised when recovery-point evidence is absent, ambiguous or out of scope."""


class RecoveryObjectiveEvidenceError(SharedRuntimeRecoveryError, ValueError):
    """Raised when RPO/RTO evidence is assumed rather than measured."""


class OwnerLocalRollbackError(SharedRuntimeRecoveryError):
    """Raised when a failed shared candidate cannot be discarded cleanly."""


def _required_text(value: str, *, field_name: str, error_type=BackupContractError) -> str:
    if not isinstance(value, str):
        raise error_type(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise error_type(f"{field_name} is required")
    return normalized


def _utc(value: datetime, *, field_name: str, error_type=BackupContractError) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise error_type(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _sha256_hex(value: str, *, field_name: str, error_type=BackupContractError) -> str:
    digest = str(value).strip().lower()
    if not _SHA256_RE.fullmatch(digest):
        raise error_type(f"{field_name} must be a 64-character SHA-256 hex digest")
    return digest


def _canonical_json(value: Any, *, field_name: str) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise BackupContractError(f"{field_name} must be canonical JSON data") from exc
    return encoded


def _same_tenant(left: TenantContext, right: TenantContext) -> bool:
    return (
        left.workspace_id == right.workspace_id
        and left.project_id == right.project_id
    )


@dataclass(frozen=True)
class SharedRuntimeRecoveryPolicy:
    """Provider-neutral P18.7 recovery boundary.

    The observation flags are intentionally false: P18.7 validates contract
    semantics, not a deployed provider or network/storage topology.
    """

    backup_encryption_required: bool = True
    external_key_reference_required: bool = True
    clean_restore_required: bool = True
    exact_tenant_restore_required: bool = True
    measured_recovery_objectives_required: bool = True
    owner_local_rollback_required: bool = True

    provider_id: None = field(default=None, init=False)
    contract_only: bool = field(default=True, init=False)
    off_host_backup_observed: bool = field(default=False, init=False)
    provider_pitr_observed: bool = field(default=False, init=False)
    cryptographic_adapter_observed: bool = field(default=False, init=False)
    shared_runtime_activated: bool = field(default=False, init=False)
    canonical_cutover_authorized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        required = (
            self.backup_encryption_required,
            self.external_key_reference_required,
            self.clean_restore_required,
            self.exact_tenant_restore_required,
            self.measured_recovery_objectives_required,
            self.owner_local_rollback_required,
        )
        if not all(value is True for value in required):
            raise BackupContractError("P18.7 recovery safeguards are mandatory and fail closed")


@dataclass(frozen=True)
class RecoveryRecord:
    """Immutable tenant-scoped canonical row/object snapshot."""

    workspace_id: str
    project_id: str
    object_type: str
    object_id: str
    payload_json: str

    def __post_init__(self) -> None:
        for name in ("workspace_id", "project_id", "object_type", "object_id"):
            object.__setattr__(
                self,
                name,
                _required_text(getattr(self, name), field_name=name),
            )
        try:
            decoded = json.loads(self.payload_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise BackupContractError("payload_json must contain valid JSON") from exc
        canonical = _canonical_json(decoded, field_name="payload_json")
        object.__setattr__(self, "payload_json", canonical)

    @classmethod
    def from_payload(
        cls,
        *,
        tenant_context: TenantContext,
        object_type: str,
        object_id: str,
        payload: Mapping[str, Any],
    ) -> "RecoveryRecord":
        if not isinstance(tenant_context, TenantContext):
            raise BackupContractError("RecoveryRecord requires TenantContext")
        if not isinstance(payload, Mapping):
            raise BackupContractError("recovery record payload must be a mapping")
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
    """Deterministic recovery snapshot for exactly one workspace/project."""

    tenant_context: TenantContext
    captured_at: datetime
    logical_schema_version: int
    repository_migration_version: int
    recovery_sequence: int
    records: tuple[RecoveryRecord, ...]
    content_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_context, TenantContext):
            raise BackupContractError("snapshot requires explicit TenantContext")
        object.__setattr__(self, "captured_at", _utc(self.captured_at, field_name="captured_at"))
        if not isinstance(self.logical_schema_version, int) or self.logical_schema_version <= 0:
            raise BackupContractError("logical_schema_version must be positive")
        if not isinstance(self.repository_migration_version, int) or self.repository_migration_version < 0:
            raise BackupContractError("repository_migration_version must be non-negative")
        if not isinstance(self.recovery_sequence, int) or self.recovery_sequence < 0:
            raise BackupContractError("recovery_sequence must be non-negative")

        normalized = tuple(sorted(self.records, key=lambda row: (row.object_type, row.object_id)))
        identities: set[tuple[str, str]] = set()
        for row in normalized:
            if not isinstance(row, RecoveryRecord):
                raise BackupContractError("snapshot records must be RecoveryRecord values")
            if not _same_tenant(row.tenant_context, self.tenant_context):
                raise RestoreIsolationError("snapshot cannot contain a record from another tenant")
            identity = (row.object_type, row.object_id)
            if identity in identities:
                raise BackupContractError("snapshot contains a duplicate object identity")
            identities.add(identity)
        object.__setattr__(self, "records", normalized)

        payload = {
            "workspace_id": self.tenant_context.workspace_id,
            "project_id": self.tenant_context.project_id,
            "captured_at": self.captured_at.isoformat(),
            "logical_schema_version": self.logical_schema_version,
            "repository_migration_version": self.repository_migration_version,
            "recovery_sequence": self.recovery_sequence,
            "records": [
                {
                    "object_type": row.object_type,
                    "object_id": row.object_id,
                    "payload_json": row.payload_json,
                }
                for row in normalized
            ],
        }
        digest = sha256(_canonical_json(payload, field_name="snapshot").encode("utf-8")).hexdigest()
        object.__setattr__(self, "content_sha256", digest)


@dataclass(frozen=True)
class EncryptedBackupArtifact:
    """Opaque encrypted backup envelope produced by a future adapter.

    ``ciphertext`` is private material and intentionally hidden from repr.  The
    class verifies only envelope/integrity semantics; it does not claim to
    validate the cryptographic strength of a concrete adapter.
    """

    backup_id: str
    tenant_context: TenantContext
    created_at: datetime
    logical_schema_version: int
    repository_migration_version: int
    recovery_sequence: int
    snapshot_sha256: str
    encryption_scheme: str
    key_reference: SecretReference
    ciphertext: bytes = field(repr=False)
    ciphertext_sha256: str = ""

    provider_id: None = field(default=None, init=False)
    contract_only: bool = field(default=True, init=False)
    off_host_storage_observed: bool = field(default=False, init=False)
    provider_pitr_observed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "backup_id", _required_text(self.backup_id, field_name="backup_id"))
        if not isinstance(self.tenant_context, TenantContext):
            raise BackupContractError("backup artifact requires TenantContext")
        object.__setattr__(self, "created_at", _utc(self.created_at, field_name="created_at"))
        if not isinstance(self.logical_schema_version, int) or self.logical_schema_version <= 0:
            raise BackupContractError("logical_schema_version must be positive")
        if not isinstance(self.repository_migration_version, int) or self.repository_migration_version < 0:
            raise BackupContractError("repository_migration_version must be non-negative")
        if not isinstance(self.recovery_sequence, int) or self.recovery_sequence < 0:
            raise BackupContractError("recovery_sequence must be non-negative")
        object.__setattr__(
            self,
            "snapshot_sha256",
            _sha256_hex(self.snapshot_sha256, field_name="snapshot_sha256"),
        )
        scheme = _required_text(self.encryption_scheme, field_name="encryption_scheme").casefold()
        if scheme in _FORBIDDEN_ENCRYPTION_SCHEMES:
            raise BackupContractError("backup artifact must declare an encrypted payload scheme")
        object.__setattr__(self, "encryption_scheme", self.encryption_scheme.strip())
        if not isinstance(self.key_reference, SecretReference):
            raise BackupContractError("backup encryption requires an external SecretReference")
        if not isinstance(self.ciphertext, bytes) or not self.ciphertext:
            raise BackupContractError("encrypted backup ciphertext must be non-empty bytes")
        expected = _sha256_hex(self.ciphertext_sha256, field_name="ciphertext_sha256")
        actual = sha256(self.ciphertext).hexdigest()
        if actual != expected:
            raise BackupIntegrityError("backup ciphertext SHA-256 does not match artifact metadata")
        object.__setattr__(self, "ciphertext_sha256", expected)


@runtime_checkable
class EncryptedBackupCodec(Protocol):
    """Adapter boundary.  P18.7 does not ship a concrete crypto implementation."""

    @property
    def codec_id(self) -> str:
        """Stable provider/adapter-neutral codec identifier."""

    def seal(
        self,
        snapshot: TenantRecoverySnapshot,
        *,
        key_reference: SecretReference,
    ) -> EncryptedBackupArtifact:
        """Return an opaque encrypted artifact for ``snapshot``."""

    def open(self, artifact: EncryptedBackupArtifact) -> TenantRecoverySnapshot:
        """Decrypt/verify an artifact and return the exact tenant snapshot."""


def verify_decoded_snapshot(
    *,
    artifact: EncryptedBackupArtifact,
    snapshot: TenantRecoverySnapshot,
) -> TenantRecoverySnapshot:
    if not isinstance(artifact, EncryptedBackupArtifact):
        raise BackupContractError("encrypted backup artifact is required")
    if not isinstance(snapshot, TenantRecoverySnapshot):
        raise BackupIntegrityError("backup codec did not return TenantRecoverySnapshot")
    if not _same_tenant(artifact.tenant_context, snapshot.tenant_context):
        raise RestoreIsolationError("decoded backup tenant differs from artifact tenant")
    if artifact.logical_schema_version != snapshot.logical_schema_version:
        raise BackupIntegrityError("decoded snapshot schema version differs from artifact")
    if artifact.repository_migration_version != snapshot.repository_migration_version:
        raise BackupIntegrityError("decoded snapshot migration version differs from artifact")
    if artifact.recovery_sequence != snapshot.recovery_sequence:
        raise BackupIntegrityError("decoded snapshot recovery sequence differs from artifact")
    if artifact.snapshot_sha256 != snapshot.content_sha256:
        raise BackupIntegrityError("decoded snapshot SHA-256 differs from artifact metadata")
    return snapshot


class InMemoryCleanRestoreTarget:
    """Provider-free clean-environment restore harness for one tenant."""

    def __init__(
        self,
        *,
        tenant_context: TenantContext,
        logical_schema_version: int,
        repository_migration_version: int,
    ) -> None:
        if not isinstance(tenant_context, TenantContext):
            raise BackupContractError("restore target requires TenantContext")
        if not isinstance(logical_schema_version, int) or logical_schema_version <= 0:
            raise BackupContractError("restore target logical_schema_version must be positive")
        if not isinstance(repository_migration_version, int) or repository_migration_version < 0:
            raise BackupContractError("restore target migration version must be non-negative")
        self.tenant_context = tenant_context
        self.logical_schema_version = logical_schema_version
        self.repository_migration_version = repository_migration_version
        self._records: tuple[RecoveryRecord, ...] = ()
        self._restored_snapshot_sha256: str | None = None

    @property
    def is_clean(self) -> bool:
        return not self._records and self._restored_snapshot_sha256 is None

    @property
    def records(self) -> tuple[RecoveryRecord, ...]:
        return self._records

    @property
    def restored_snapshot_sha256(self) -> str | None:
        return self._restored_snapshot_sha256

    def restore(self, snapshot: TenantRecoverySnapshot) -> tuple[RecoveryRecord, ...]:
        if not self.is_clean:
            raise RestoreTargetNotCleanError("restore requires a clean target and never overwrites state")
        if not isinstance(snapshot, TenantRecoverySnapshot):
            raise BackupContractError("restore requires TenantRecoverySnapshot")
        if not _same_tenant(snapshot.tenant_context, self.tenant_context):
            raise RestoreIsolationError("restore cannot cross workspace/project tenant scope")
        if snapshot.logical_schema_version != self.logical_schema_version:
            raise BackupIntegrityError("restore target logical schema version is incompatible")
        if snapshot.repository_migration_version != self.repository_migration_version:
            raise BackupIntegrityError("restore target repository migration version is incompatible")
        for row in snapshot.records:
            if not _same_tenant(row.tenant_context, self.tenant_context):
                raise RestoreIsolationError("restore record escaped target tenant scope")
        self._records = tuple(snapshot.records)
        self._restored_snapshot_sha256 = snapshot.content_sha256
        return self._records


def restore_encrypted_backup(
    *,
    artifact: EncryptedBackupArtifact,
    codec: EncryptedBackupCodec,
    target: InMemoryCleanRestoreTarget,
) -> tuple[RecoveryRecord, ...]:
    if not isinstance(codec, EncryptedBackupCodec):
        raise BackupContractError("restore requires an EncryptedBackupCodec adapter")
    if not isinstance(target, InMemoryCleanRestoreTarget):
        raise BackupContractError("restore requires a clean restore target")
    snapshot = verify_decoded_snapshot(artifact=artifact, snapshot=codec.open(artifact))
    return target.restore(snapshot)


@dataclass(frozen=True)
class RecoveryPoint:
    tenant_context: TenantContext
    durable_at: datetime
    sequence: int
    snapshot: TenantRecoverySnapshot

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_context, TenantContext):
            raise RecoveryPointError("recovery point requires TenantContext")
        object.__setattr__(
            self,
            "durable_at",
            _utc(self.durable_at, field_name="durable_at", error_type=RecoveryPointError),
        )
        if not isinstance(self.sequence, int) or self.sequence < 0:
            raise RecoveryPointError("recovery point sequence must be non-negative")
        if not isinstance(self.snapshot, TenantRecoverySnapshot):
            raise RecoveryPointError("recovery point requires TenantRecoverySnapshot")
        if not _same_tenant(self.tenant_context, self.snapshot.tenant_context):
            raise RestoreIsolationError("recovery point cannot bind another tenant snapshot")
        if self.sequence != self.snapshot.recovery_sequence:
            raise RecoveryPointError("recovery point sequence must equal snapshot recovery_sequence")


def select_recovery_point(
    *,
    tenant_context: TenantContext,
    points: Sequence[RecoveryPoint],
    target_at: datetime,
) -> RecoveryPoint:
    """Select latest durable logical recovery point at/before target time.

    This validates provider-neutral point-in-time *semantics* only.  It is not
    evidence that a provider WAL/PITR facility exists.
    """

    if not isinstance(tenant_context, TenantContext):
        raise RecoveryPointError("recovery-point selection requires TenantContext")
    target = _utc(target_at, field_name="target_at", error_type=RecoveryPointError)
    candidates: list[RecoveryPoint] = []
    for point in points:
        if not isinstance(point, RecoveryPoint):
            raise RecoveryPointError("points must contain RecoveryPoint values")
        if not _same_tenant(point.tenant_context, tenant_context):
            raise RestoreIsolationError("recovery-point set cannot mix tenants")
        if point.durable_at <= target:
            candidates.append(point)
    if not candidates:
        raise RecoveryPointError("no durable recovery point exists at or before target time")
    return max(candidates, key=lambda point: (point.durable_at, point.sequence))


@dataclass(frozen=True)
class RecoveryDrillTimeline:
    """Observed timestamps used to derive measured RPO/RTO evidence."""

    last_durable_recovery_point_at: datetime
    failure_at: datetime
    restore_started_at: datetime
    restore_completed_at: datetime
    measured_rpo_seconds: float = field(init=False)
    measured_rto_seconds: float = field(init=False)

    def __post_init__(self) -> None:
        durable = _utc(
            self.last_durable_recovery_point_at,
            field_name="last_durable_recovery_point_at",
            error_type=RecoveryObjectiveEvidenceError,
        )
        failure = _utc(self.failure_at, field_name="failure_at", error_type=RecoveryObjectiveEvidenceError)
        started = _utc(
            self.restore_started_at,
            field_name="restore_started_at",
            error_type=RecoveryObjectiveEvidenceError,
        )
        completed = _utc(
            self.restore_completed_at,
            field_name="restore_completed_at",
            error_type=RecoveryObjectiveEvidenceError,
        )
        if not durable <= failure <= started <= completed:
            raise RecoveryObjectiveEvidenceError("recovery drill timestamps must be monotonic")
        object.__setattr__(self, "last_durable_recovery_point_at", durable)
        object.__setattr__(self, "failure_at", failure)
        object.__setattr__(self, "restore_started_at", started)
        object.__setattr__(self, "restore_completed_at", completed)
        object.__setattr__(self, "measured_rpo_seconds", (failure - durable).total_seconds())
        object.__setattr__(self, "measured_rto_seconds", (completed - failure).total_seconds())


@dataclass(frozen=True)
class RecoveryDrillEvidence:
    tenant_context: TenantContext
    clean_environment_restore_succeeded: bool
    tenant_isolation_validated: bool
    content_reconciled: bool
    timeline: RecoveryDrillTimeline
    provider_pitr_observed: bool = False
    service_level_claim_authorized: bool = False
    factual_verification_authority: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_context, TenantContext):
            raise RecoveryObjectiveEvidenceError("recovery drill evidence requires TenantContext")
        if not isinstance(self.timeline, RecoveryDrillTimeline):
            raise RecoveryObjectiveEvidenceError("recovery drill requires measured timeline evidence")
        if not all(
            (
                self.clean_environment_restore_succeeded,
                self.tenant_isolation_validated,
                self.content_reconciled,
            )
        ):
            raise RecoveryObjectiveEvidenceError("recovery drill evidence is incomplete")
        if self.service_level_claim_authorized:
            raise RecoveryObjectiveEvidenceError(
                "P18.7 measurements cannot authorize a production service-level claim"
            )
        if self.factual_verification_authority:
            raise RecoveryObjectiveEvidenceError("recovery evidence cannot promote factual verification")

    @property
    def measured_rpo_seconds(self) -> float:
        return self.timeline.measured_rpo_seconds

    @property
    def measured_rto_seconds(self) -> float:
        return self.timeline.measured_rto_seconds


@dataclass(frozen=True)
class OwnerLocalBaseline:
    """Content identity of the independently operable owner-local canonical store."""

    store_id: str
    database_sha256: str
    canonical_storage_policy: StorageScope = StorageScope.PROJECT_LOCAL_SQLITE

    def __post_init__(self) -> None:
        object.__setattr__(self, "store_id", _required_text(self.store_id, field_name="store_id", error_type=OwnerLocalRollbackError))
        object.__setattr__(
            self,
            "database_sha256",
            _sha256_hex(
                self.database_sha256,
                field_name="database_sha256",
                error_type=OwnerLocalRollbackError,
            ),
        )
        if self.canonical_storage_policy is not StorageScope.PROJECT_LOCAL_SQLITE:
            raise OwnerLocalRollbackError("owner-local rollback baseline must be project-local SQLite")


@dataclass(frozen=True)
class OwnerLocalRollbackEvidence:
    store_id: str
    database_sha256: str
    shared_candidate_discarded: bool
    owner_local_unchanged: bool
    canonical_cutover_authorized: bool = False
    shared_runtime_activated: bool = False


def validate_owner_local_rollback(
    *,
    before: OwnerLocalBaseline,
    after: OwnerLocalBaseline,
    shared_candidate_discarded: bool,
) -> OwnerLocalRollbackEvidence:
    if not isinstance(before, OwnerLocalBaseline) or not isinstance(after, OwnerLocalBaseline):
        raise OwnerLocalRollbackError("owner-local before/after baselines are required")
    if shared_candidate_discarded is not True:
        raise OwnerLocalRollbackError("failed shared candidate must be discardable before rollback passes")
    if before.store_id != after.store_id or before.database_sha256 != after.database_sha256:
        raise OwnerLocalRollbackError("owner-local canonical store changed during shared-candidate rollback")
    return OwnerLocalRollbackEvidence(
        store_id=before.store_id,
        database_sha256=before.database_sha256,
        shared_candidate_discarded=True,
        owner_local_unchanged=True,
    )


def public_backup_metadata(artifact: EncryptedBackupArtifact) -> dict[str, object]:
    """Return non-secret backup metadata without ciphertext or key locator."""

    if not isinstance(artifact, EncryptedBackupArtifact):
        raise BackupContractError("encrypted backup artifact is required")
    return {
        "backup_id": artifact.backup_id,
        "workspace_id": artifact.tenant_context.workspace_id,
        "project_id": artifact.tenant_context.project_id,
        "created_at": artifact.created_at.isoformat(),
        "logical_schema_version": artifact.logical_schema_version,
        "repository_migration_version": artifact.repository_migration_version,
        "recovery_sequence": artifact.recovery_sequence,
        "snapshot_sha256": artifact.snapshot_sha256,
        "ciphertext_sha256": artifact.ciphertext_sha256,
        "encryption_scheme": artifact.encryption_scheme,
        "provider_id": artifact.provider_id,
        "contract_only": artifact.contract_only,
        "off_host_storage_observed": artifact.off_host_storage_observed,
        "provider_pitr_observed": artifact.provider_pitr_observed,
        "canonical_cutover_authorized": False,
        "shared_runtime_activated": False,
        "factual_verification_authority": False,
    }
