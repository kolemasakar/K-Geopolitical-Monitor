"""P18.7 provider-neutral shared-runtime backup, DR and rollback contracts.

This module defines recovery invariants and an in-memory validation harness only.
It does not provision backup storage, select a provider, create encryption keys,
allocate a migration, activate shared runtime, or replace the independently
operable owner-local SQLite recovery path in :mod:`runtime_backup`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re

from .shared_datastore_schema import MIGRATION_NUMBER_NOT_ALLOCATED
from .shared_runtime_contract import StorageScope, TenantContext
from .shared_runtime_security import SecretReference


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SharedRuntimeRecoveryError(RuntimeError):
    """Base error for fail-closed P18.7 recovery processing."""


class BackupContractError(SharedRuntimeRecoveryError, ValueError):
    """Raised when backup evidence violates the P18.7 contract."""


class RestoreContractError(SharedRuntimeRecoveryError, ValueError):
    """Raised when a restore request or drill is unsafe or inconsistent."""


class RollbackContractError(SharedRuntimeRecoveryError, ValueError):
    """Raised when owner-local rollback independence cannot be demonstrated."""


def _required_text(value: str, *, field_name: str, error_type=BackupContractError) -> str:
    if not isinstance(value, str):
        raise error_type(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise error_type(f"{field_name} is required")
    return normalized


def _sha256(value: str, *, field_name: str, error_type=BackupContractError) -> str:
    normalized = _required_text(value, field_name=field_name, error_type=error_type).lower()
    if not _SHA256_RE.fullmatch(normalized):
        raise error_type(f"{field_name} must be a 64-character SHA-256 hex digest")
    return normalized


def _utc(value: datetime, *, field_name: str, error_type=BackupContractError) -> datetime:
    if not isinstance(value, datetime):
        raise error_type(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise error_type(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _row_counts(values: tuple[tuple[str, int], ...]) -> tuple[tuple[str, int], ...]:
    if not values:
        raise BackupContractError("backup row-count evidence is required")
    result: list[tuple[str, int]] = []
    seen: set[str] = set()
    for table_name, count in values:
        name = _required_text(table_name, field_name="table_name")
        if name in seen:
            raise BackupContractError("backup row-count evidence contains duplicate tables")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise BackupContractError("backup row counts must be non-negative integers")
        seen.add(name)
        result.append((name, count))
    return tuple(result)


@dataclass(frozen=True)
class SharedRecoveryPlanContract:
    """Provider-neutral recovery capability contract for a future shared candidate."""

    encrypted_backups_required: bool = True
    off_host_backup_required: bool = True
    clean_environment_restore_required: bool = True
    tenant_exact_match_required: bool = True
    pitr_supported: bool = False
    equivalent_checkpoint_restore_supported: bool = True
    provider_id: None = field(default=None, init=False)
    migration_number: str = field(default=MIGRATION_NUMBER_NOT_ALLOCATED, init=False)
    migration_033_authorized: bool = field(default=False, init=False)
    shared_runtime_active: bool = field(default=False, init=False)
    canonical_cutover_authorized: bool = field(default=False, init=False)
    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not self.encrypted_backups_required:
            raise BackupContractError("shared-runtime backups must be encrypted")
        if not self.off_host_backup_required:
            raise BackupContractError("shared-runtime backups require an off-host copy")
        if not self.clean_environment_restore_required:
            raise RestoreContractError("clean-environment restore drills are required")
        if not self.tenant_exact_match_required:
            raise RestoreContractError("tenant-exact restore isolation is required")
        if not self.pitr_supported and not self.equivalent_checkpoint_restore_supported:
            raise RestoreContractError(
                "recovery requires PITR or an equivalent recoverable-checkpoint mechanism"
            )


def build_p18_7_recovery_plan_contract() -> SharedRecoveryPlanContract:
    """Return the default P18.7 contract without activating shared infrastructure."""

    return SharedRecoveryPlanContract()


@dataclass(frozen=True)
class SharedBackupManifest:
    """Non-secret integrity/provenance manifest for an encrypted shared backup.

    ``encryption_key_reference`` is an opaque P18.6 ``SecretReference``. Secret
    values must never be placed in this manifest, logs, canonical rows or public
    artifacts.
    """

    backup_id: str
    tenant_context: TenantContext
    schema_version: int
    schema_contract_id: str
    captured_at: datetime
    checkpoint_id: str
    content_sha256: str
    encryption_key_reference: SecretReference = field(repr=False)
    row_counts: tuple[tuple[str, int], ...] = ()
    encrypted: bool = True
    off_host_copy: bool = True
    migration_number: str = MIGRATION_NUMBER_NOT_ALLOCATED
    provider_id: None = field(default=None, init=False)
    storage_scope: StorageScope = field(default=StorageScope.SHARED_CANONICAL, init=False)
    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "backup_id", _required_text(self.backup_id, field_name="backup_id"))
        if not isinstance(self.tenant_context, TenantContext):
            raise BackupContractError("backup requires explicit TenantContext")
        if not isinstance(self.schema_version, int) or isinstance(self.schema_version, bool) or self.schema_version <= 0:
            raise BackupContractError("schema_version must be a positive integer")
        object.__setattr__(
            self,
            "schema_contract_id",
            _required_text(self.schema_contract_id, field_name="schema_contract_id"),
        )
        object.__setattr__(self, "captured_at", _utc(self.captured_at, field_name="captured_at"))
        object.__setattr__(
            self,
            "checkpoint_id",
            _required_text(self.checkpoint_id, field_name="checkpoint_id"),
        )
        object.__setattr__(
            self,
            "content_sha256",
            _sha256(self.content_sha256, field_name="content_sha256"),
        )
        if not isinstance(self.encryption_key_reference, SecretReference):
            raise BackupContractError("backup encryption requires an opaque SecretReference")
        if not self.encrypted:
            raise BackupContractError("unencrypted shared-runtime backup is forbidden")
        if not self.off_host_copy:
            raise BackupContractError("shared-runtime backup requires an off-host copy")
        if self.migration_number != MIGRATION_NUMBER_NOT_ALLOCATED:
            raise BackupContractError("P18.7 cannot allocate or preauthorize a repository migration")
        object.__setattr__(self, "row_counts", _row_counts(self.row_counts))


@dataclass(frozen=True)
class RestoreRequest:
    """Fail-closed restore request for a verified backup into a clean target."""

    manifest: SharedBackupManifest
    requested_tenant: TenantContext
    requested_checkpoint_id: str
    observed_content_sha256: str
    observed_schema_version: int
    target_is_clean: bool

    def __post_init__(self) -> None:
        if not isinstance(self.manifest, SharedBackupManifest):
            raise RestoreContractError("restore requires a validated SharedBackupManifest")
        if not isinstance(self.requested_tenant, TenantContext):
            raise RestoreContractError("restore requires explicit requested TenantContext")
        object.__setattr__(
            self,
            "requested_checkpoint_id",
            _required_text(
                self.requested_checkpoint_id,
                field_name="requested_checkpoint_id",
                error_type=RestoreContractError,
            ),
        )
        object.__setattr__(
            self,
            "observed_content_sha256",
            _sha256(
                self.observed_content_sha256,
                field_name="observed_content_sha256",
                error_type=RestoreContractError,
            ),
        )
        if (
            not isinstance(self.observed_schema_version, int)
            or isinstance(self.observed_schema_version, bool)
            or self.observed_schema_version <= 0
        ):
            raise RestoreContractError("observed_schema_version must be a positive integer")


def validate_restore_request(request: RestoreRequest) -> RestoreRequest:
    """Validate tenant, integrity, schema, checkpoint and clean-target invariants."""

    if not isinstance(request, RestoreRequest):
        raise RestoreContractError("RestoreRequest is required")
    manifest = request.manifest
    if request.requested_tenant != manifest.tenant_context:
        raise RestoreContractError("cross-tenant restore is forbidden")
    if not request.target_is_clean:
        raise RestoreContractError("restore target must be a clean environment")
    if request.requested_checkpoint_id != manifest.checkpoint_id:
        raise RestoreContractError("restore checkpoint does not match backup manifest")
    if request.observed_content_sha256 != manifest.content_sha256:
        raise RestoreContractError("restore content digest does not match backup manifest")
    if request.observed_schema_version != manifest.schema_version:
        raise RestoreContractError("restore schema version does not match backup manifest")
    return request


@dataclass(frozen=True)
class RestoreDrillEvidence:
    """Measured evidence from a clean-environment restore drill.

    RPO/RTO are derived from observed timestamps. They are evidence values, not
    targets, guarantees or SLA claims.
    """

    request: RestoreRequest
    restored_tenant: TenantContext
    recovery_target_at: datetime
    started_at: datetime
    completed_at: datetime
    reconciliation_passed: bool
    cross_tenant_rows_observed: bool = False
    factual_verification_authority: bool = field(default=False, init=False)
    sla_claimed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        validate_restore_request(self.request)
        if not isinstance(self.restored_tenant, TenantContext):
            raise RestoreContractError("restore drill requires restored TenantContext")
        if self.restored_tenant != self.request.manifest.tenant_context:
            raise RestoreContractError("restore drill tenant differs from backup tenant")
        recovery_target = _utc(
            self.recovery_target_at,
            field_name="recovery_target_at",
            error_type=RestoreContractError,
        )
        started = _utc(self.started_at, field_name="started_at", error_type=RestoreContractError)
        completed = _utc(
            self.completed_at,
            field_name="completed_at",
            error_type=RestoreContractError,
        )
        if completed < started:
            raise RestoreContractError("restore completion cannot precede restore start")
        if recovery_target < self.request.manifest.captured_at:
            raise RestoreContractError("recovery target cannot precede the recoverable checkpoint")
        if not self.reconciliation_passed:
            raise RestoreContractError("restore drill requires successful reconciliation")
        if self.cross_tenant_rows_observed:
            raise RestoreContractError("restore drill observed cross-tenant rows")
        object.__setattr__(self, "recovery_target_at", recovery_target)
        object.__setattr__(self, "started_at", started)
        object.__setattr__(self, "completed_at", completed)

    @property
    def observed_rpo_seconds(self) -> float:
        return (self.recovery_target_at - self.request.manifest.captured_at).total_seconds()

    @property
    def observed_rto_seconds(self) -> float:
        return (self.completed_at - self.started_at).total_seconds()


@dataclass(frozen=True)
class RollbackEvidence:
    """Evidence that a failed shared candidate is discardable without local mutation."""

    candidate_id: str
    owner_local_sha256_before: str
    owner_local_sha256_after: str
    shared_candidate_discarded: bool
    owner_local_storage_scope: StorageScope = StorageScope.PROJECT_LOCAL_SQLITE
    shared_runtime_active: bool = False
    canonical_cutover_performed: bool = False
    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "candidate_id",
            _required_text(
                self.candidate_id,
                field_name="candidate_id",
                error_type=RollbackContractError,
            ),
        )
        object.__setattr__(
            self,
            "owner_local_sha256_before",
            _sha256(
                self.owner_local_sha256_before,
                field_name="owner_local_sha256_before",
                error_type=RollbackContractError,
            ),
        )
        object.__setattr__(
            self,
            "owner_local_sha256_after",
            _sha256(
                self.owner_local_sha256_after,
                field_name="owner_local_sha256_after",
                error_type=RollbackContractError,
            ),
        )


def validate_rollback_evidence(evidence: RollbackEvidence) -> RollbackEvidence:
    """Require discardability while preserving unchanged owner-local canonical state."""

    if not isinstance(evidence, RollbackEvidence):
        raise RollbackContractError("RollbackEvidence is required")
    if not evidence.shared_candidate_discarded:
        raise RollbackContractError("failed shared candidate must be discardable")
    if evidence.owner_local_storage_scope is not StorageScope.PROJECT_LOCAL_SQLITE:
        raise RollbackContractError("rollback must preserve project-local owner canonical storage")
    if evidence.owner_local_sha256_before != evidence.owner_local_sha256_after:
        raise RollbackContractError("owner-local canonical database changed during shared rollback")
    if evidence.shared_runtime_active:
        raise RollbackContractError("P18.7 cannot activate shared runtime")
    if evidence.canonical_cutover_performed:
        raise RollbackContractError("P18.7 cannot perform canonical cutover")
    return evidence
