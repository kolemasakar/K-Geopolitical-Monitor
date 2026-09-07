"""P18.4 tenant-scoped repository, idempotency and concurrency contracts.

This module is a provider-neutral contract harness. It does not connect to,
create, migrate, or activate a shared datastore. Every canonical repository
operation requires an authenticated principal, an explicit TenantContext, and
server-side RBAC resolution. Stored object keys and idempotency keys are always
scoped by workspace_id/project_id.

The in-memory harness exists only to validate repository semantics before any
provider-specific shared datastore implementation is selected. The active
canonical runtime remains the project-isolated owner-only SQLite profile.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from threading import Lock
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .identity_tenant_context import AuthenticatedPrincipal
from .rbac_authorization import Permission, RoleBindingResolver, require_permission
from .shared_runtime_contract import StorageScope, TenantContext


class SharedRepositoryError(RuntimeError):
    """Base error for fail-closed P18.4 repository processing."""


class InvalidRepositoryCommandError(SharedRepositoryError, ValueError):
    """Raised when a repository command is malformed or unsafe."""


class SharedObjectNotFoundError(SharedRepositoryError, LookupError):
    """Raised when an object does not exist inside the exact tenant scope."""


class IdempotencyConflictError(SharedRepositoryError):
    """Raised when an idempotency key is reused for a different command."""


class VersionConflictError(SharedRepositoryError):
    """Raised when optimistic concurrency detects a stale writer."""

    def __init__(self, *, expected_version: int, current_version: int) -> None:
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            f"optimistic concurrency conflict: expected version {expected_version}, "
            f"current version {current_version}"
        )


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise InvalidRepositoryCommandError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise InvalidRepositoryCommandError(f"{field_name} is required")
    return normalized


def _canonical_payload_json(payload: Mapping[str, Any]) -> str:
    if not isinstance(payload, Mapping):
        raise InvalidRepositoryCommandError("payload must be a mapping")
    try:
        return json.dumps(
            dict(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise InvalidRepositoryCommandError(
            "payload must be deterministically JSON-serializable"
        ) from exc


def _require_tenant_context(tenant_context: TenantContext) -> TenantContext:
    if not isinstance(tenant_context, TenantContext):
        raise InvalidRepositoryCommandError(
            "explicit workspace_id/project_id TenantContext is required"
        )
    return tenant_context


@dataclass(frozen=True)
class SharedCanonicalRecord:
    """Immutable result envelope for one tenant-scoped canonical object."""

    tenant_context: TenantContext
    object_type: str
    object_id: str
    version: int
    payload_json: str

    def __post_init__(self) -> None:
        _require_tenant_context(self.tenant_context)
        object.__setattr__(
            self,
            "object_type",
            _required_text(self.object_type, field_name="object_type"),
        )
        object.__setattr__(
            self,
            "object_id",
            _required_text(self.object_id, field_name="object_id"),
        )
        if not isinstance(self.version, int) or self.version <= 0:
            raise InvalidRepositoryCommandError("record version must be positive")
        if not isinstance(self.payload_json, str):
            raise InvalidRepositoryCommandError("payload_json must be a string")
        try:
            decoded = json.loads(self.payload_json)
        except json.JSONDecodeError as exc:
            raise InvalidRepositoryCommandError("payload_json must be valid JSON") from exc
        if not isinstance(decoded, dict):
            raise InvalidRepositoryCommandError("record payload must decode to an object")

    @property
    def payload(self) -> dict[str, Any]:
        """Return a detached decoded payload."""

        return json.loads(self.payload_json)


@dataclass(frozen=True)
class WriteCommand:
    """Retryable optimistic-concurrency command.

    ``expected_version=0`` is the create-if-absent contract. Updates must pass
    the last observed positive version. Every command requires an idempotency
    key because duplicate execution materially changes canonical state.
    """

    object_type: str
    object_id: str
    payload: Mapping[str, Any]
    idempotency_key: str
    expected_version: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "object_type",
            _required_text(self.object_type, field_name="object_type"),
        )
        object.__setattr__(
            self,
            "object_id",
            _required_text(self.object_id, field_name="object_id"),
        )
        object.__setattr__(
            self,
            "idempotency_key",
            _required_text(self.idempotency_key, field_name="idempotency_key"),
        )
        if not isinstance(self.expected_version, int) or self.expected_version < 0:
            raise InvalidRepositoryCommandError(
                "expected_version must be a non-negative integer"
            )
        _canonical_payload_json(self.payload)

    @property
    def payload_json(self) -> str:
        return _canonical_payload_json(self.payload)

    @property
    def fingerprint(self) -> str:
        material = json.dumps(
            {
                "expected_version": self.expected_version,
                "object_id": self.object_id,
                "object_type": self.object_type,
                "payload_json": self.payload_json,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return sha256(material).hexdigest()


@dataclass(frozen=True)
class WriteResult:
    record: SharedCanonicalRecord
    idempotency_key: str
    command_fingerprint: str
    replayed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "idempotency_key",
            _required_text(self.idempotency_key, field_name="idempotency_key"),
        )
        fingerprint = _required_text(
            self.command_fingerprint,
            field_name="command_fingerprint",
        ).lower()
        if len(fingerprint) != 64 or any(ch not in "0123456789abcdef" for ch in fingerprint):
            raise InvalidRepositoryCommandError(
                "command_fingerprint must be a SHA-256 hex digest"
            )
        object.__setattr__(self, "command_fingerprint", fingerprint)


@dataclass(frozen=True)
class _IdempotencyReceipt:
    fingerprint: str
    original_result: WriteResult


@runtime_checkable
class TenantScopedSharedRepository(Protocol):
    """Provider-neutral shared canonical repository contract.

    Implementations must keep the authorization/scope arguments on every
    canonical method. A repository API that permits an unscoped read or write
    does not satisfy P18.4.
    """

    @property
    def storage_scope(self) -> StorageScope:
        """Must be SHARED_CANONICAL for a future shared adapter."""

    def get(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        object_type: str,
        object_id: str,
    ) -> SharedCanonicalRecord:
        """Read one object from the exact authorized tenant scope."""

    def list_by_type(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        object_type: str,
    ) -> Sequence[SharedCanonicalRecord]:
        """List only objects from the exact authorized tenant scope."""

    def write(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        command: WriteCommand,
    ) -> WriteResult:
        """Apply one idempotent optimistic-concurrency mutation."""


class InMemorySharedRepositoryHarness:
    """Thread-safe P18.4 contract harness, never a production datastore.

    The harness proves semantics only. It intentionally has no database URL,
    provider identifier, persistence, migration runner, network transport, or
    activation capability.
    """

    storage_scope = StorageScope.SHARED_CANONICAL
    provider_id = None
    persistent = False
    contract_only = True

    def __init__(self) -> None:
        self._records: dict[
            tuple[str, str, str, str], SharedCanonicalRecord
        ] = {}
        self._idempotency: dict[
            tuple[str, str, str], _IdempotencyReceipt
        ] = {}
        self._lock = Lock()

    @staticmethod
    def _object_key(
        tenant_context: TenantContext,
        *,
        object_type: str,
        object_id: str,
    ) -> tuple[str, str, str, str]:
        context = _require_tenant_context(tenant_context)
        return (
            context.workspace_id,
            context.project_id,
            _required_text(object_type, field_name="object_type"),
            _required_text(object_id, field_name="object_id"),
        )

    @staticmethod
    def _idempotency_key(
        tenant_context: TenantContext,
        *,
        idempotency_key: str,
    ) -> tuple[str, str, str]:
        context = _require_tenant_context(tenant_context)
        return (
            context.workspace_id,
            context.project_id,
            _required_text(idempotency_key, field_name="idempotency_key"),
        )

    def get(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        object_type: str,
        object_id: str,
    ) -> SharedCanonicalRecord:
        require_permission(
            principal=principal,
            tenant_context=_require_tenant_context(tenant_context),
            resolver=role_bindings,
            permission=Permission.CANONICAL_READ,
        )
        key = self._object_key(
            tenant_context,
            object_type=object_type,
            object_id=object_id,
        )
        with self._lock:
            record = self._records.get(key)
        if record is None:
            raise SharedObjectNotFoundError(
                "object not found in the authorized workspace/project scope"
            )
        return record

    def list_by_type(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        object_type: str,
    ) -> tuple[SharedCanonicalRecord, ...]:
        require_permission(
            principal=principal,
            tenant_context=_require_tenant_context(tenant_context),
            resolver=role_bindings,
            permission=Permission.CANONICAL_READ,
        )
        normalized_type = _required_text(object_type, field_name="object_type")
        prefix = (
            tenant_context.workspace_id,
            tenant_context.project_id,
            normalized_type,
        )
        with self._lock:
            records = [
                record
                for key, record in self._records.items()
                if key[:3] == prefix
            ]
        return tuple(sorted(records, key=lambda record: record.object_id))

    def write(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        command: WriteCommand,
    ) -> WriteResult:
        context = _require_tenant_context(tenant_context)
        require_permission(
            principal=principal,
            tenant_context=context,
            resolver=role_bindings,
            permission=Permission.CANONICAL_MUTATE,
        )
        if not isinstance(command, WriteCommand):
            raise InvalidRepositoryCommandError("WriteCommand is required")

        object_key = self._object_key(
            context,
            object_type=command.object_type,
            object_id=command.object_id,
        )
        retry_key = self._idempotency_key(
            context,
            idempotency_key=command.idempotency_key,
        )
        fingerprint = command.fingerprint

        # One lock represents the atomic transaction boundary of the contract
        # harness: object-version check, canonical mutation, and idempotency
        # receipt publication either happen together or not at all.
        with self._lock:
            prior_receipt = self._idempotency.get(retry_key)
            if prior_receipt is not None:
                if prior_receipt.fingerprint != fingerprint:
                    raise IdempotencyConflictError(
                        "idempotency key was already used for a different command"
                    )
                original = prior_receipt.original_result
                return WriteResult(
                    record=original.record,
                    idempotency_key=original.idempotency_key,
                    command_fingerprint=original.command_fingerprint,
                    replayed=True,
                )

            current = self._records.get(object_key)
            current_version = current.version if current is not None else 0
            if command.expected_version != current_version:
                raise VersionConflictError(
                    expected_version=command.expected_version,
                    current_version=current_version,
                )

            record = SharedCanonicalRecord(
                tenant_context=context,
                object_type=command.object_type,
                object_id=command.object_id,
                version=current_version + 1,
                payload_json=command.payload_json,
            )
            result = WriteResult(
                record=record,
                idempotency_key=command.idempotency_key,
                command_fingerprint=fingerprint,
                replayed=False,
            )
            self._records[object_key] = record
            self._idempotency[retry_key] = _IdempotencyReceipt(
                fingerprint=fingerprint,
                original_result=result,
            )
            return result

    def contract_counts(self) -> tuple[int, int]:
        """Expose deterministic harness counts for tests, never operational state."""

        with self._lock:
            return len(self._records), len(self._idempotency)
