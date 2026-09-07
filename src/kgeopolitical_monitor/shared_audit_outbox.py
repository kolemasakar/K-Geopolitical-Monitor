"""P18.5 audit, transactional outbox and side-effect isolation contracts.

This provider-neutral in-memory harness models the transaction boundary that a
future shared datastore adapter must preserve. It does not connect to or create
a shared datastore, choose a provider, allocate a repository migration, expose
shared/public ingress, or activate the shared runtime.

A successful canonical mutation commits the canonical object, P18.4
idempotency receipt, append-only security audit record, and optional outbox
message under one lock. Delivery/publication receipts remain lifecycle evidence
only and can never promote factual verification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from threading import Lock
from typing import Any, Callable, Mapping, Protocol, Sequence, runtime_checkable

from .identity_tenant_context import (
    AuthenticatedPrincipal,
    HumanIdentity,
    IdentityKind,
    ServiceIdentity,
)
from .rbac_authorization import (
    Permission,
    RoleBindingResolver,
    require_permission,
)
from .shared_repository_concurrency import (
    IdempotencyConflictError,
    InMemorySharedRepositoryHarness,
    InvalidRepositoryCommandError,
    SharedCanonicalRecord,
    VersionConflictError,
    WriteCommand,
    WriteResult,
    _IdempotencyReceipt,
    _canonical_payload_json,
    _require_tenant_context,
    _required_text,
)
from .shared_runtime_contract import TenantContext


class SharedAuditOutboxError(RuntimeError):
    """Base error for fail-closed P18.5 audit/outbox processing."""


class InvalidAuditMetadataError(SharedAuditOutboxError, ValueError):
    """Raised when required audit/correlation metadata is malformed."""


class InvalidSideEffectIntentError(SharedAuditOutboxError, ValueError):
    """Raised when a side-effect intent is malformed or nondeterministic."""


class OutboxMessageNotFoundError(SharedAuditOutboxError, LookupError):
    """Raised when an outbox message does not exist inside exact tenant scope."""


class SideEffectDeliveryConflictError(SharedAuditOutboxError):
    """Raised when a delivery idempotency key is reused for different content."""


class SideEffectDispatchError(SharedAuditOutboxError):
    """Raised when an outbox dispatch cannot be completed safely."""


class SideEffectKind(str, Enum):
    DELIVERY = "delivery"
    PUBLICATION = "publication"


class OutboxState(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"


def _aware_utc(value: datetime, *, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InvalidAuditMetadataError(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _sha256_hex(material: str) -> str:
    return sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MutationAuditMetadata:
    """Caller-supplied non-secret context for one canonical mutation."""

    action: str
    correlation_id: str
    request_id: str
    occurred_at: datetime
    causation_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "action", _required_text(self.action, field_name="action")
        )
        object.__setattr__(
            self,
            "correlation_id",
            _required_text(self.correlation_id, field_name="correlation_id"),
        )
        object.__setattr__(
            self,
            "request_id",
            _required_text(self.request_id, field_name="request_id"),
        )
        if self.causation_id is not None:
            object.__setattr__(
                self,
                "causation_id",
                _required_text(self.causation_id, field_name="causation_id"),
            )
        object.__setattr__(
            self,
            "occurred_at",
            _aware_utc(self.occurred_at, field_name="occurred_at"),
        )


@dataclass(frozen=True)
class SideEffectIntent:
    """Immutable delivery/publication intent staged into the transactional outbox."""

    kind: SideEffectKind
    channel: str
    destination_ref: str
    payload: Mapping[str, Any]
    _payload_json: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, SideEffectKind):
            raise InvalidSideEffectIntentError("side-effect kind is invalid")
        try:
            channel = _required_text(self.channel, field_name="channel")
            destination = _required_text(
                self.destination_ref, field_name="destination_ref"
            )
            payload_json = _canonical_payload_json(self.payload)
        except InvalidRepositoryCommandError as exc:
            raise InvalidSideEffectIntentError(str(exc)) from exc
        object.__setattr__(self, "channel", channel)
        object.__setattr__(self, "destination_ref", destination)
        object.__setattr__(self, "_payload_json", payload_json)

    @property
    def payload_json(self) -> str:
        return self._payload_json

    @property
    def fingerprint(self) -> str:
        material = json.dumps(
            {
                "channel": self.channel,
                "destination_ref": self.destination_ref,
                "kind": self.kind.value,
                "payload_json": self.payload_json,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return _sha256_hex(material)


@dataclass(frozen=True)
class SecurityMutationAuditRecord:
    audit_id: str
    tenant_context: TenantContext
    actor_kind: IdentityKind
    actor_id: str
    actor_session_id: str
    action: str
    object_type: str
    object_id: str
    object_version: int
    command_fingerprint: str
    correlation_id: str
    request_id: str
    causation_id: str | None
    occurred_at: datetime

    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        _require_tenant_context(self.tenant_context)
        object.__setattr__(
            self, "audit_id", _required_text(self.audit_id, field_name="audit_id")
        )
        if not isinstance(self.actor_kind, IdentityKind):
            raise InvalidAuditMetadataError("actor_kind is invalid")
        for field_name in (
            "actor_id",
            "actor_session_id",
            "action",
            "object_type",
            "object_id",
            "command_fingerprint",
            "correlation_id",
            "request_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name=field_name),
            )
        if not isinstance(self.object_version, int) or self.object_version <= 0:
            raise InvalidAuditMetadataError("object_version must be positive")
        if self.causation_id is not None:
            object.__setattr__(
                self,
                "causation_id",
                _required_text(self.causation_id, field_name="causation_id"),
            )
        object.__setattr__(
            self,
            "occurred_at",
            _aware_utc(self.occurred_at, field_name="occurred_at"),
        )


@dataclass(frozen=True)
class TransactionalOutboxMessage:
    outbox_id: str
    tenant_context: TenantContext
    kind: SideEffectKind
    channel: str
    destination_ref: str
    payload_json: str
    payload_fingerprint: str
    delivery_idempotency_key: str
    object_type: str
    object_id: str
    object_version: int
    correlation_id: str
    created_at: datetime
    state: OutboxState = OutboxState.PENDING
    delivered_receipt_ref: str | None = None

    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        _require_tenant_context(self.tenant_context)
        if not isinstance(self.kind, SideEffectKind):
            raise InvalidSideEffectIntentError("outbox side-effect kind is invalid")
        if not isinstance(self.state, OutboxState):
            raise InvalidSideEffectIntentError("outbox state is invalid")
        for field_name in (
            "outbox_id",
            "channel",
            "destination_ref",
            "payload_json",
            "payload_fingerprint",
            "delivery_idempotency_key",
            "object_type",
            "object_id",
            "correlation_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name=field_name),
            )
        try:
            decoded = json.loads(self.payload_json)
        except json.JSONDecodeError as exc:
            raise InvalidSideEffectIntentError("outbox payload_json must be valid JSON") from exc
        if not isinstance(decoded, dict):
            raise InvalidSideEffectIntentError("outbox payload must decode to an object")
        if _sha256_hex(self.payload_json) != self.payload_fingerprint:
            raise InvalidSideEffectIntentError("outbox payload fingerprint mismatch")
        if not isinstance(self.object_version, int) or self.object_version <= 0:
            raise InvalidSideEffectIntentError("outbox object_version must be positive")
        object.__setattr__(
            self,
            "created_at",
            _aware_utc(self.created_at, field_name="created_at"),
        )
        if self.state is OutboxState.DELIVERED:
            if self.delivered_receipt_ref is None:
                raise InvalidSideEffectIntentError(
                    "delivered outbox message requires a receipt reference"
                )
            object.__setattr__(
                self,
                "delivered_receipt_ref",
                _required_text(
                    self.delivered_receipt_ref, field_name="delivered_receipt_ref"
                ),
            )
        elif self.delivered_receipt_ref is not None:
            raise InvalidSideEffectIntentError(
                "pending outbox message cannot carry a receipt reference"
            )

    @property
    def payload(self) -> dict[str, Any]:
        return json.loads(self.payload_json)


@dataclass(frozen=True)
class SideEffectReceipt:
    delivery_idempotency_key: str
    receipt_ref: str
    replayed: bool
    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "delivery_idempotency_key",
            _required_text(
                self.delivery_idempotency_key,
                field_name="delivery_idempotency_key",
            ),
        )
        object.__setattr__(
            self,
            "receipt_ref",
            _required_text(self.receipt_ref, field_name="receipt_ref"),
        )


@runtime_checkable
class IdempotentSideEffectConsumer(Protocol):
    """Provider-neutral consumer contract.

    A real adapter must durably deduplicate ``delivery_idempotency_key`` before
    or atomically with performing the external effect.
    """

    def deliver(self, message: TransactionalOutboxMessage) -> SideEffectReceipt:
        """Perform or replay one externally visible side effect."""


class InMemoryIdempotentSideEffectConsumerHarness:
    """Contract-only consumer proving stable-key retry semantics."""

    provider_id = None
    persistent = False
    contract_only = True

    def __init__(self) -> None:
        self._receipts: dict[str, tuple[str, str]] = {}
        self._effect_count = 0
        self._lock = Lock()

    def deliver(self, message: TransactionalOutboxMessage) -> SideEffectReceipt:
        if not isinstance(message, TransactionalOutboxMessage):
            raise SideEffectDispatchError("TransactionalOutboxMessage is required")

        key = message.delivery_idempotency_key
        payload_identity = json.dumps(
            {
                "kind": message.kind.value,
                "channel": message.channel,
                "destination_ref": message.destination_ref,
                "payload_fingerprint": message.payload_fingerprint,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        with self._lock:
            prior = self._receipts.get(key)
            if prior is not None:
                prior_identity, receipt_ref = prior
                if prior_identity != payload_identity:
                    raise SideEffectDeliveryConflictError(
                        "delivery idempotency key was reused for different side-effect content"
                    )
                return SideEffectReceipt(
                    delivery_idempotency_key=key,
                    receipt_ref=receipt_ref,
                    replayed=True,
                )

            receipt_ref = f"receipt-{_sha256_hex(key + ':' + payload_identity)[:24]}"
            self._receipts[key] = (payload_identity, receipt_ref)
            self._effect_count += 1
            return SideEffectReceipt(
                delivery_idempotency_key=key,
                receipt_ref=receipt_ref,
                replayed=False,
            )

    @property
    def effect_count(self) -> int:
        with self._lock:
            return self._effect_count


class InMemoryAuditedOutboxRepositoryHarness(InMemorySharedRepositoryHarness):
    """P18.5 transaction/outbox contract harness; never a production datastore."""

    provider_id = None
    persistent = False
    contract_only = True

    def __init__(
        self,
        *,
        before_commit_hook: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._audit_records: list[SecurityMutationAuditRecord] = []
        self._outbox: dict[tuple[str, str, str], TransactionalOutboxMessage] = {}
        self._p18_5_retry_identity: dict[tuple[str, str, str], str] = {}
        self._before_commit_hook = before_commit_hook

    @staticmethod
    def _principal_metadata(
        principal: AuthenticatedPrincipal,
    ) -> tuple[IdentityKind, str, str]:
        if isinstance(principal, (HumanIdentity, ServiceIdentity)):
            return principal.identity_kind, principal.principal_id, principal.session_id
        raise InvalidAuditMetadataError("authenticated principal metadata is required")

    @staticmethod
    def _retry_identity(
        *,
        principal: AuthenticatedPrincipal,
        command: WriteCommand,
        metadata: MutationAuditMetadata,
        side_effect: SideEffectIntent | None,
    ) -> str:
        actor_kind, actor_id, _ = InMemoryAuditedOutboxRepositoryHarness._principal_metadata(
            principal
        )
        material = json.dumps(
            {
                "actor_kind": actor_kind.value,
                "actor_id": actor_id,
                "command_fingerprint": command.fingerprint,
                "action": metadata.action,
                "side_effect_fingerprint": (
                    side_effect.fingerprint if side_effect is not None else None
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return _sha256_hex(material)

    @staticmethod
    def _audit_id(
        *,
        tenant_context: TenantContext,
        command: WriteCommand,
        metadata: MutationAuditMetadata,
    ) -> str:
        material = json.dumps(
            {
                "workspace_id": tenant_context.workspace_id,
                "project_id": tenant_context.project_id,
                "idempotency_key": command.idempotency_key,
                "command_fingerprint": command.fingerprint,
                "action": metadata.action,
                "correlation_id": metadata.correlation_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return f"audit-{_sha256_hex(material)[:32]}"

    @staticmethod
    def _outbox_message(
        *,
        tenant_context: TenantContext,
        record: SharedCanonicalRecord,
        command: WriteCommand,
        metadata: MutationAuditMetadata,
        intent: SideEffectIntent,
    ) -> TransactionalOutboxMessage:
        material = json.dumps(
            {
                "workspace_id": tenant_context.workspace_id,
                "project_id": tenant_context.project_id,
                "idempotency_key": command.idempotency_key,
                "command_fingerprint": command.fingerprint,
                "intent_fingerprint": intent.fingerprint,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = _sha256_hex(material)
        outbox_id = f"outbox-{digest[:32]}"
        delivery_key = f"effect-{digest}"
        return TransactionalOutboxMessage(
            outbox_id=outbox_id,
            tenant_context=tenant_context,
            kind=intent.kind,
            channel=intent.channel,
            destination_ref=intent.destination_ref,
            payload_json=intent.payload_json,
            payload_fingerprint=_sha256_hex(intent.payload_json),
            delivery_idempotency_key=delivery_key,
            object_type=record.object_type,
            object_id=record.object_id,
            object_version=record.version,
            correlation_id=metadata.correlation_id,
            created_at=metadata.occurred_at,
        )

    def write(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        command: WriteCommand,
        audit_metadata: MutationAuditMetadata,
        side_effect: SideEffectIntent | None = None,
    ) -> WriteResult:
        """Atomically commit canonical write, idempotency, audit and optional outbox."""

        context = _require_tenant_context(tenant_context)
        require_permission(
            principal=principal,
            tenant_context=context,
            resolver=role_bindings,
            permission=Permission.CANONICAL_MUTATE,
        )
        if not isinstance(command, WriteCommand):
            raise InvalidRepositoryCommandError("WriteCommand is required")
        if not isinstance(audit_metadata, MutationAuditMetadata):
            raise InvalidAuditMetadataError("MutationAuditMetadata is required")
        if side_effect is not None and not isinstance(side_effect, SideEffectIntent):
            raise InvalidSideEffectIntentError("SideEffectIntent is required")

        actor_kind, actor_id, actor_session_id = self._principal_metadata(principal)
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
        retry_identity = self._retry_identity(
            principal=principal,
            command=command,
            metadata=audit_metadata,
            side_effect=side_effect,
        )

        with self._lock:
            prior_receipt = self._idempotency.get(retry_key)
            if prior_receipt is not None:
                if prior_receipt.fingerprint != fingerprint:
                    raise IdempotencyConflictError(
                        "idempotency key was already used for a different command"
                    )
                if self._p18_5_retry_identity.get(retry_key) != retry_identity:
                    raise IdempotencyConflictError(
                        "idempotency key was already used with different actor, action, "
                        "or side-effect intent"
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
            audit = SecurityMutationAuditRecord(
                audit_id=self._audit_id(
                    tenant_context=context,
                    command=command,
                    metadata=audit_metadata,
                ),
                tenant_context=context,
                actor_kind=actor_kind,
                actor_id=actor_id,
                actor_session_id=actor_session_id,
                action=audit_metadata.action,
                object_type=record.object_type,
                object_id=record.object_id,
                object_version=record.version,
                command_fingerprint=fingerprint,
                correlation_id=audit_metadata.correlation_id,
                request_id=audit_metadata.request_id,
                causation_id=audit_metadata.causation_id,
                occurred_at=audit_metadata.occurred_at,
            )
            outbox_message = (
                self._outbox_message(
                    tenant_context=context,
                    record=record,
                    command=command,
                    metadata=audit_metadata,
                    intent=side_effect,
                )
                if side_effect is not None
                else None
            )

            # Build every transaction artifact before mutating harness state.
            # The hook simulates ordinary process failure immediately before
            # commit; no partial canonical/audit/outbox state may escape.
            if self._before_commit_hook is not None:
                self._before_commit_hook()

            self._records[object_key] = record
            self._idempotency[retry_key] = _IdempotencyReceipt(
                fingerprint=fingerprint,
                original_result=result,
            )
            self._p18_5_retry_identity[retry_key] = retry_identity
            self._audit_records.append(audit)
            if outbox_message is not None:
                outbox_key = (
                    context.workspace_id,
                    context.project_id,
                    outbox_message.outbox_id,
                )
                self._outbox[outbox_key] = outbox_message
            return result

    def list_audit_records(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
    ) -> tuple[SecurityMutationAuditRecord, ...]:
        context = _require_tenant_context(tenant_context)
        require_permission(
            principal=principal,
            tenant_context=context,
            resolver=role_bindings,
            permission=Permission.CANONICAL_READ,
        )
        with self._lock:
            records = tuple(
                record
                for record in self._audit_records
                if record.tenant_context == context
            )
        return records

    def list_outbox_messages(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
    ) -> tuple[TransactionalOutboxMessage, ...]:
        context = _require_tenant_context(tenant_context)
        require_permission(
            principal=principal,
            tenant_context=context,
            resolver=role_bindings,
            permission=Permission.CANONICAL_READ,
        )
        with self._lock:
            messages = tuple(
                message
                for (workspace_id, project_id, _), message in self._outbox.items()
                if workspace_id == context.workspace_id
                and project_id == context.project_id
            )
        return tuple(sorted(messages, key=lambda message: message.outbox_id))

    def dispatch_outbox_message(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        outbox_id: str,
        consumer: IdempotentSideEffectConsumer,
        after_consumer_hook: Callable[[], None] | None = None,
    ) -> SideEffectReceipt:
        """Dispatch one message with stable-key replay after post-effect failure."""

        context = _require_tenant_context(tenant_context)
        require_permission(
            principal=principal,
            tenant_context=context,
            resolver=role_bindings,
            permission=Permission.SERVICE_EXECUTE,
        )
        normalized_outbox_id = _required_text(outbox_id, field_name="outbox_id")
        key = (context.workspace_id, context.project_id, normalized_outbox_id)

        with self._lock:
            message = self._outbox.get(key)
            if message is None:
                raise OutboxMessageNotFoundError(
                    "outbox message not found in the authorized workspace/project scope"
                )
            if message.state is OutboxState.DELIVERED:
                return SideEffectReceipt(
                    delivery_idempotency_key=message.delivery_idempotency_key,
                    receipt_ref=message.delivered_receipt_ref or "",
                    replayed=True,
                )

        if not isinstance(consumer, IdempotentSideEffectConsumer):
            raise SideEffectDispatchError(
                "consumer must satisfy IdempotentSideEffectConsumer"
            )
        receipt = consumer.deliver(message)
        if receipt.delivery_idempotency_key != message.delivery_idempotency_key:
            raise SideEffectDispatchError(
                "consumer receipt idempotency key does not match outbox message"
            )

        # Simulate process loss after the external effect but before local
        # delivery-state commit. On retry the consumer receives the same stable
        # idempotency key and must replay instead of duplicating the effect.
        if after_consumer_hook is not None:
            after_consumer_hook()

        with self._lock:
            current = self._outbox.get(key)
            if current is None:
                raise OutboxMessageNotFoundError(
                    "outbox message disappeared before delivery-state commit"
                )
            if current.state is OutboxState.DELIVERED:
                return SideEffectReceipt(
                    delivery_idempotency_key=current.delivery_idempotency_key,
                    receipt_ref=current.delivered_receipt_ref or "",
                    replayed=True,
                )
            self._outbox[key] = TransactionalOutboxMessage(
                outbox_id=current.outbox_id,
                tenant_context=current.tenant_context,
                kind=current.kind,
                channel=current.channel,
                destination_ref=current.destination_ref,
                payload_json=current.payload_json,
                payload_fingerprint=current.payload_fingerprint,
                delivery_idempotency_key=current.delivery_idempotency_key,
                object_type=current.object_type,
                object_id=current.object_id,
                object_version=current.object_version,
                correlation_id=current.correlation_id,
                created_at=current.created_at,
                state=OutboxState.DELIVERED,
                delivered_receipt_ref=receipt.receipt_ref,
            )
        return receipt

    def contract_counts(self) -> tuple[int, int, int, int]:
        """Return canonical/idempotency/audit/outbox counts for contract tests."""

        with self._lock:
            return (
                len(self._records),
                len(self._idempotency),
                len(self._audit_records),
                len(self._outbox),
            )
