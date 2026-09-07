"""P18.6 provider-neutral shared-runtime security and secrets controls.

The contracts in this module are deliberately deployment-neutral. They define
fail-closed security behavior that a future shared runtime must preserve without
selecting a provider, exposing ingress, provisioning a datastore, allocating a
migration, or activating shared runtime.

Observed network/TLS reachability and provider-specific controls remain launch
evidence for later Phase 18 shadow/readiness gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
import hmac
import ipaddress
import json
import re
from threading import Lock
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

from .identity_tenant_context import (
    AuthenticatedPrincipal,
    HumanIdentity,
    IdentityKind,
    ServiceIdentity,
    WorkspaceMembership,
)
from .rbac_authorization import (
    Permission,
    RoleBinding,
    RoleBindingResolver,
    require_permission,
)
from .shared_audit_outbox import (
    InMemoryAuditedOutboxRepositoryHarness,
    MutationAuditMetadata,
    SideEffectIntent,
)
from .shared_repository_concurrency import WriteCommand, WriteResult
from .shared_runtime_contract import TenantContext


class SharedRuntimeSecurityError(RuntimeError):
    """Base error for fail-closed P18.6 shared-runtime security processing."""


class NetworkBoundaryViolation(SharedRuntimeSecurityError, ValueError):
    """Raised when shared ingress/datastore/egress violates the security boundary."""


class SecretExposureError(SharedRuntimeSecurityError, ValueError):
    """Raised when private secret material reaches a forbidden surface."""


class SessionBindingError(SharedRuntimeSecurityError):
    """Raised when one session identity is rebound to different credential evidence."""


class RequestSecurityViolation(SharedRuntimeSecurityError, ValueError):
    """Raised for IDOR/injection/CSRF or malformed request-security input."""


class ResourceLimitExceeded(SharedRuntimeSecurityError):
    """Raised when a tenant request exceeds a configured abuse/resource limit."""


class SecurityIdentityError(SharedRuntimeSecurityError):
    """Raised when shared security identity cannot be bound unambiguously."""


class AuthPresentation(str, Enum):
    BEARER_HEADER = "bearer_header"
    COOKIE_SESSION = "cookie_session"


class QueryOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    IN = "in"
    CONTAINS = "contains"


class SecurityEventKind(str, Enum):
    AUTH_FAILURE = "auth_failure"
    SESSION_MISUSE = "session_misuse"
    IDOR_DENIED = "idor_denied"
    INJECTION_DENIED = "injection_denied"
    SSRF_DENIED = "ssrf_denied"
    CSRF_DENIED = "csrf_denied"
    PRIVILEGE_ESCALATION_DENIED = "privilege_escalation_denied"
    RESOURCE_LIMIT_DENIED = "resource_limit_denied"
    SECRET_EXPOSURE_BLOCKED = "secret_exposure_blocked"


@dataclass(frozen=True)
class SharedRuntimeSecurityPolicy:
    """Provider-neutral boundary policy for a future shared runtime candidate.

    ``datastore_public_ingress=False`` and ``datastore_tls_required=True`` are
    configuration-contract assertions only. P18.6 does not claim that a real
    datastore has been deployed or externally probed.
    """

    application_base_url: str
    datastore_public_ingress: bool = False
    datastore_tls_required: bool = True
    admin_public_ingress: bool = False
    allowed_egress_hosts: tuple[str, ...] = ()
    max_request_bytes: int = 1_048_576
    max_page_size: int = 500
    max_requests_per_window: int = 60
    rate_window: timedelta = timedelta(minutes=1)

    provider_id: None = field(default=None, init=False)
    contract_only: bool = field(default=True, init=False)
    network_reachability_observed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        parsed = urlsplit(self.application_base_url)
        if parsed.scheme.lower() != "https":
            raise NetworkBoundaryViolation("shared application boundary must be HTTPS-only")
        if not parsed.hostname:
            raise NetworkBoundaryViolation("shared application HTTPS boundary requires a host")
        if parsed.username is not None or parsed.password is not None:
            raise NetworkBoundaryViolation("application boundary URL cannot embed credentials")
        if parsed.fragment:
            raise NetworkBoundaryViolation("application boundary URL cannot contain a fragment")
        if self.datastore_public_ingress:
            raise NetworkBoundaryViolation("shared canonical datastore public ingress is forbidden")
        if not self.datastore_tls_required:
            raise NetworkBoundaryViolation("shared canonical datastore transport encryption is required")
        if self.admin_public_ingress:
            raise NetworkBoundaryViolation("unrestricted public administrative ingress is forbidden")
        if not isinstance(self.max_request_bytes, int) or self.max_request_bytes <= 0:
            raise ValueError("max_request_bytes must be positive")
        if not isinstance(self.max_page_size, int) or self.max_page_size <= 0:
            raise ValueError("max_page_size must be positive")
        if not isinstance(self.max_requests_per_window, int) or self.max_requests_per_window <= 0:
            raise ValueError("max_requests_per_window must be positive")
        if not isinstance(self.rate_window, timedelta) or self.rate_window <= timedelta(0):
            raise ValueError("rate_window must be positive")

        normalized_hosts: list[str] = []
        for host in self.allowed_egress_hosts:
            normalized = _normalize_host(host)
            if normalized not in normalized_hosts:
                normalized_hosts.append(normalized)
        object.__setattr__(self, "allowed_egress_hosts", tuple(normalized_hosts))


@dataclass(frozen=True)
class TenantObjectReference:
    workspace_id: str
    project_id: str
    object_type: str
    object_id: str

    def __post_init__(self) -> None:
        for name in ("workspace_id", "project_id", "object_type", "object_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise RequestSecurityViolation(f"{name} is required")
            object.__setattr__(self, name, value.strip())


@dataclass(frozen=True)
class StructuredQuery:
    """A structured query primitive; raw SQL/filter expressions are not accepted."""

    field: str
    operator: QueryOperator
    value: Any

    def __post_init__(self) -> None:
        if not isinstance(self.field, str) or not self.field.strip():
            raise RequestSecurityViolation("structured query field is required")
        object.__setattr__(self, "field", self.field.strip())
        if not isinstance(self.operator, QueryOperator):
            raise RequestSecurityViolation("structured query operator is invalid")


@dataclass(frozen=True)
class CsrfRequestContext:
    presentation: AuthPresentation
    origin: str | None = None
    csrf_cookie: str | None = field(default=None, repr=False)
    csrf_header: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class SecretReference:
    """Opaque reference to a secret; never the secret value itself."""

    source: str
    name: str

    def __post_init__(self) -> None:
        source = str(self.source).strip().lower()
        name = str(self.name).strip()
        if source not in {"env", "secret_store"}:
            raise SecretExposureError("secret source must be env or secret_store")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.:/-]{1,127}", name):
            raise SecretExposureError("secret reference name is invalid")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "name", name)

    @property
    def locator(self) -> str:
        return f"{self.source}://{self.name}"


@dataclass(frozen=True)
class SessionCredentialEvidence:
    """Non-secret credential evidence supplied by an authentication adapter."""

    fingerprint_sha256: str

    def __post_init__(self) -> None:
        value = str(self.fingerprint_sha256).strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise SessionBindingError("credential fingerprint must be a SHA-256 hex digest")
        object.__setattr__(self, "fingerprint_sha256", value)


@dataclass(frozen=True)
class SecurityEventAuditMapping:
    event_kind: SecurityEventKind
    audit_action: str
    severity: str
    factual_verification_authority: bool = field(default=False, init=False)


_SECURITY_EVENT_MAP = {
    SecurityEventKind.AUTH_FAILURE: ("security.auth_failure", "medium"),
    SecurityEventKind.SESSION_MISUSE: ("security.session_misuse", "high"),
    SecurityEventKind.IDOR_DENIED: ("security.idor_denied", "high"),
    SecurityEventKind.INJECTION_DENIED: ("security.injection_denied", "high"),
    SecurityEventKind.SSRF_DENIED: ("security.ssrf_denied", "high"),
    SecurityEventKind.CSRF_DENIED: ("security.csrf_denied", "high"),
    SecurityEventKind.PRIVILEGE_ESCALATION_DENIED: (
        "security.privilege_escalation_denied",
        "critical",
    ),
    SecurityEventKind.RESOURCE_LIMIT_DENIED: ("security.resource_limit_denied", "medium"),
    SecurityEventKind.SECRET_EXPOSURE_BLOCKED: ("security.secret_exposure_blocked", "critical"),
}


_SENSITIVE_KEY_PARTS = (
    "authorization",
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "cookie",
    "credential",
)


def principal_security_key(principal: AuthenticatedPrincipal) -> str:
    """Return issuer-scoped stable actor identity for P18.6 security decisions."""

    if not isinstance(principal, (HumanIdentity, ServiceIdentity)):
        raise SecurityIdentityError("authenticated principal is required")
    issuer = str(principal.issuer).strip()
    principal_id = str(principal.principal_id).strip()
    if not issuer or not principal_id:
        raise SecurityIdentityError("principal issuer and identifier are required")
    return f"{issuer}:{principal.identity_kind.value}:{principal_id}"


def security_event_mapping(event_kind: SecurityEventKind) -> SecurityEventAuditMapping:
    if not isinstance(event_kind, SecurityEventKind):
        raise RequestSecurityViolation("security event kind is invalid")
    action, severity = _SECURITY_EVENT_MAP[event_kind]
    return SecurityEventAuditMapping(
        event_kind=event_kind,
        audit_action=action,
        severity=severity,
    )


def require_same_tenant_object(
    *, tenant_context: TenantContext, object_ref: TenantObjectReference
) -> TenantObjectReference:
    if not isinstance(tenant_context, TenantContext):
        raise RequestSecurityViolation("server-derived tenant context is required")
    if not isinstance(object_ref, TenantObjectReference):
        raise RequestSecurityViolation("structured tenant object reference is required")
    if (
        object_ref.workspace_id != tenant_context.workspace_id
        or object_ref.project_id != tenant_context.project_id
    ):
        raise RequestSecurityViolation("object reference is outside authenticated tenant scope")
    return object_ref


def validate_structured_query(
    query: StructuredQuery, *, allowed_fields: Sequence[str]
) -> StructuredQuery:
    if not isinstance(query, StructuredQuery):
        raise RequestSecurityViolation("raw query/filter expressions are forbidden")
    normalized = {str(field).strip() for field in allowed_fields if str(field).strip()}
    if query.field not in normalized:
        raise RequestSecurityViolation("query field is not allowlisted")
    return query


def validate_csrf(
    request: CsrfRequestContext, *, allowed_origins: Sequence[str]
) -> None:
    if not isinstance(request, CsrfRequestContext):
        raise RequestSecurityViolation("CSRF request context is required")
    if request.presentation is AuthPresentation.BEARER_HEADER:
        # Header bearer authentication is not cookie ambient-authority CSRF.
        return
    if request.presentation is not AuthPresentation.COOKIE_SESSION:
        raise RequestSecurityViolation("authentication presentation is invalid")

    normalized_origins = {_normalize_origin(origin) for origin in allowed_origins}
    if request.origin is None or _normalize_origin(request.origin) not in normalized_origins:
        raise RequestSecurityViolation("cookie session origin is not allowlisted")
    if not request.csrf_cookie or not request.csrf_header:
        raise RequestSecurityViolation("cookie session requires CSRF cookie and header")
    if not hmac.compare_digest(request.csrf_cookie, request.csrf_header):
        raise RequestSecurityViolation("CSRF token mismatch")


def validate_outbound_https_url(url: str, *, allowed_hosts: Sequence[str]) -> str:
    """Validate one provider-neutral egress URL against a strict SSRF boundary."""

    if not isinstance(url, str) or not url.strip():
        raise NetworkBoundaryViolation("outbound URL is required")
    parsed = urlsplit(url.strip())
    if parsed.scheme.lower() != "https":
        raise NetworkBoundaryViolation("outbound integrations require HTTPS")
    if not parsed.hostname:
        raise NetworkBoundaryViolation("outbound URL requires a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise NetworkBoundaryViolation("outbound URL cannot embed credentials")
    if parsed.port not in (None, 443):
        raise NetworkBoundaryViolation("outbound HTTPS is restricted to port 443")
    host = _normalize_host(parsed.hostname)
    allowlist = {_normalize_host(item) for item in allowed_hosts}
    if not allowlist or host not in allowlist:
        raise NetworkBoundaryViolation("outbound host is not explicitly allowlisted")

    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise NetworkBoundaryViolation("local/resolver-only outbound hosts are forbidden")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        # Hostnames still require DNS/IP enforcement in the concrete egress adapter.
        return url.strip()
    if not addr.is_global:
        raise NetworkBoundaryViolation("non-global IP targets are forbidden")
    return url.strip()


def validate_request_size(size_bytes: int, *, policy: SharedRuntimeSecurityPolicy) -> int:
    if not isinstance(size_bytes, int) or size_bytes < 0:
        raise RequestSecurityViolation("request size must be a non-negative integer")
    if size_bytes > policy.max_request_bytes:
        raise ResourceLimitExceeded("request exceeds shared-runtime size limit")
    return size_bytes


def validate_page_size(page_size: int, *, policy: SharedRuntimeSecurityPolicy) -> int:
    if not isinstance(page_size, int) or page_size <= 0:
        raise RequestSecurityViolation("page_size must be positive")
    if page_size > policy.max_page_size:
        raise ResourceLimitExceeded("page_size exceeds shared-runtime limit")
    return page_size


def _normalize_host(host: str) -> str:
    value = str(host).strip().lower().rstrip(".")
    if not value:
        raise NetworkBoundaryViolation("host is required")
    if "/" in value or "@" in value or ":" in value and not _looks_like_ip_literal(value):
        raise NetworkBoundaryViolation("host must not contain URL syntax")
    return value


def _looks_like_ip_literal(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def _normalize_origin(origin: str) -> str:
    if not isinstance(origin, str) or not origin.strip():
        raise RequestSecurityViolation("origin is required")
    parsed = urlsplit(origin.strip())
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise RequestSecurityViolation("allowed browser origins must use HTTPS")
    if parsed.username is not None or parsed.password is not None:
        raise RequestSecurityViolation("origin cannot embed credentials")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise RequestSecurityViolation("origin must not include path/query/fragment")
    port = f":{parsed.port}" if parsed.port is not None else ""
    return f"https://{parsed.hostname.lower()}{port}"


def _contains_sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(key).lower())
    return any(part in normalized for part in _SENSITIVE_KEY_PARTS)


def redact_sensitive(
    value: Any, *, known_secret_values: Sequence[str] = ()
) -> Any:
    """Return a recursive public/log-safe projection with deterministic redaction."""

    secrets = tuple(
        secret
        for secret in (str(item) for item in known_secret_values)
        if len(secret) >= 8
    )
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _contains_sensitive_key(key_text):
                redacted[key_text] = "[REDACTED]"
            else:
                redacted[key_text] = redact_sensitive(
                    item, known_secret_values=secrets
                )
        return redacted
    if isinstance(value, (list, tuple)):
        return [
            redact_sensitive(item, known_secret_values=secrets) for item in value
        ]
    if isinstance(value, str):
        result = value
        result = re.sub(
            r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}",
            "Bearer [REDACTED]",
            result,
        )
        for secret in secrets:
            result = result.replace(secret, "[REDACTED]")
        return result
    return value


def assert_secret_free_surface(
    value: Any, *, known_secret_values: Sequence[str] = ()
) -> None:
    """Reject secret-bearing structures before canonical/public/export surfaces."""

    secrets = tuple(str(item) for item in known_secret_values if str(item))
    if isinstance(value, Mapping):
        for key, item in value.items():
            if _contains_sensitive_key(str(key)):
                raise SecretExposureError("sensitive key is forbidden on this surface")
            assert_secret_free_surface(item, known_secret_values=secrets)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            assert_secret_free_surface(item, known_secret_values=secrets)
        return
    if isinstance(value, str):
        if re.search(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}", value):
            raise SecretExposureError("bearer credential is forbidden on this surface")
        for secret in secrets:
            if secret and secret in value:
                raise SecretExposureError("known secret material is forbidden on this surface")


@dataclass(frozen=True)
class IssuerBoundWorkspaceMembership:
    """P18.6 issuer envelope around the P18.1 membership value."""

    issuer: str
    membership: WorkspaceMembership

    def __post_init__(self) -> None:
        issuer = str(self.issuer).strip()
        if not issuer:
            raise SecurityIdentityError("membership issuer is required")
        if not isinstance(self.membership, WorkspaceMembership):
            raise SecurityIdentityError("WorkspaceMembership is required")
        object.__setattr__(self, "issuer", issuer)


class IssuerBoundWorkspaceMembershipResolver:
    """Shared-profile resolver that refuses cross-issuer subject collisions."""

    def __init__(self, *bindings: IssuerBoundWorkspaceMembership) -> None:
        if not all(isinstance(item, IssuerBoundWorkspaceMembership) for item in bindings):
            raise SecurityIdentityError("issuer-bound memberships are required")
        self._bindings = tuple(bindings)

    def memberships_for(
        self, principal: AuthenticatedPrincipal
    ) -> tuple[WorkspaceMembership, ...]:
        principal_security_key(principal)
        return tuple(
            item.membership
            for item in self._bindings
            if item.issuer == principal.issuer
            and item.membership.identity_kind is principal.identity_kind
            and item.membership.principal_id == principal.principal_id
        )


@dataclass(frozen=True)
class IssuerBoundRoleBinding:
    """P18.6 issuer envelope around the P18.2 server-side RBAC binding."""

    issuer: str
    binding: RoleBinding

    def __post_init__(self) -> None:
        issuer = str(self.issuer).strip()
        if not issuer:
            raise SecurityIdentityError("role-binding issuer is required")
        if not isinstance(self.binding, RoleBinding):
            raise SecurityIdentityError("RoleBinding is required")
        object.__setattr__(self, "issuer", issuer)


class IssuerBoundRoleBindingResolver:
    """Shared-profile RBAC resolver keyed by issuer + kind + principal id."""

    def __init__(self, *bindings: IssuerBoundRoleBinding) -> None:
        if not all(isinstance(item, IssuerBoundRoleBinding) for item in bindings):
            raise SecurityIdentityError("issuer-bound role bindings are required")
        self._bindings = tuple(bindings)

    def bindings_for(self, principal: AuthenticatedPrincipal) -> tuple[RoleBinding, ...]:
        principal_security_key(principal)
        return tuple(
            item.binding
            for item in self._bindings
            if item.issuer == principal.issuer
            and item.binding.identity_kind is principal.identity_kind
            and item.binding.principal_id == principal.principal_id
        )


@dataclass(frozen=True)
class SecurityEventRecord:
    event_id: str
    tenant_context: TenantContext
    actor_security_key: str | None
    event_kind: SecurityEventKind
    audit_action: str
    severity: str
    occurred_at: datetime
    details_json: str

    factual_verification_authority: bool = field(default=False, init=False)

    @property
    def details(self) -> dict[str, Any]:
        return json.loads(self.details_json)


class InMemorySecurityEventAuditSink:
    """Append-only contract sink for security events, never factual truth."""

    provider_id = None
    persistent = False
    contract_only = True

    def __init__(self) -> None:
        self._records: list[SecurityEventRecord] = []
        self._lock = Lock()

    def record(
        self,
        *,
        tenant_context: TenantContext,
        event_kind: SecurityEventKind,
        occurred_at: datetime,
        details: Mapping[str, Any],
        principal: AuthenticatedPrincipal | None = None,
        known_secret_values: Sequence[str] = (),
    ) -> SecurityEventRecord:
        if not isinstance(tenant_context, TenantContext):
            raise RequestSecurityViolation("server-derived tenant context is required")
        mapping = security_event_mapping(event_kind)
        if not isinstance(occurred_at, datetime) or occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise RequestSecurityViolation("security-event timestamp must be timezone-aware")
        if not isinstance(details, Mapping):
            raise RequestSecurityViolation("security-event details must be a mapping")
        safe_details = redact_sensitive(details, known_secret_values=known_secret_values)
        details_json = json.dumps(
            safe_details,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        actor_key = principal_security_key(principal) if principal is not None else None
        material = json.dumps(
            {
                "workspace_id": tenant_context.workspace_id,
                "project_id": tenant_context.project_id,
                "actor": actor_key,
                "event_kind": event_kind.value,
                "occurred_at": occurred_at.astimezone(timezone.utc).isoformat(),
                "details_json": details_json,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        record = SecurityEventRecord(
            event_id=f"security-{sha256(material.encode('utf-8')).hexdigest()[:32]}",
            tenant_context=tenant_context,
            actor_security_key=actor_key,
            event_kind=event_kind,
            audit_action=mapping.audit_action,
            severity=mapping.severity,
            occurred_at=occurred_at.astimezone(timezone.utc),
            details_json=details_json,
        )
        with self._lock:
            self._records.append(record)
        return record

    def list_records(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
    ) -> tuple[SecurityEventRecord, ...]:
        require_permission(
            principal=principal,
            tenant_context=tenant_context,
            resolver=role_bindings,
            permission=Permission.CANONICAL_READ,
        )
        with self._lock:
            return tuple(
                record
                for record in self._records
                if record.tenant_context == tenant_context
            )


class InMemorySessionBindingGuard:
    """Contract-only guard against issuer/session credential rebinding."""

    provider_id = None
    persistent = False
    contract_only = True

    def __init__(self) -> None:
        self._bindings: dict[tuple[str, str], str] = {}
        self._lock = Lock()

    def validate(
        self,
        *,
        principal: AuthenticatedPrincipal,
        evidence: SessionCredentialEvidence,
    ) -> None:
        key = (principal_security_key(principal), str(principal.session_id))
        with self._lock:
            prior = self._bindings.get(key)
            if prior is None:
                self._bindings[key] = evidence.fingerprint_sha256
                return
            if not hmac.compare_digest(prior, evidence.fingerprint_sha256):
                raise SessionBindingError(
                    "authenticated session was rebound to different credential evidence"
                )


class InMemoryTenantRateLimiter:
    """Deterministic provider-neutral per-tenant sliding-window limiter."""

    provider_id = None
    persistent = False
    contract_only = True

    def __init__(self, policy: SharedRuntimeSecurityPolicy) -> None:
        if not isinstance(policy, SharedRuntimeSecurityPolicy):
            raise ValueError("SharedRuntimeSecurityPolicy is required")
        self._policy = policy
        self._requests: dict[tuple[str, str], list[datetime]] = {}
        self._lock = Lock()

    def check(self, *, tenant_context: TenantContext, now: datetime) -> None:
        if not isinstance(tenant_context, TenantContext):
            raise RequestSecurityViolation("server-derived tenant context is required")
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise RequestSecurityViolation("rate-limit timestamp must be timezone-aware")
        now_utc = now.astimezone(timezone.utc)
        cutoff = now_utc - self._policy.rate_window
        key = (tenant_context.workspace_id, tenant_context.project_id)
        with self._lock:
            current = [
                seen
                for seen in self._requests.get(key, [])
                if seen > cutoff
            ]
            if len(current) >= self._policy.max_requests_per_window:
                raise ResourceLimitExceeded("tenant request-rate limit exceeded")
            current.append(now_utc)
            self._requests[key] = current


class IssuerAwareAuditedOutboxRepositoryHarness(
    InMemoryAuditedOutboxRepositoryHarness
):
    """P18.6 hardening wrapper for P18.5 actor retry identity.

    The P18.5 harness is deployment-neutral and historically keyed actor retry
    identity by kind + principal_id. In a federated/shared identity model the
    issuer is part of actor identity. This subclass preserves P18.5 behavior
    while making shared-security retry identity issuer-aware.
    """

    @staticmethod
    def _retry_identity(
        *,
        principal: AuthenticatedPrincipal,
        command: WriteCommand,
        metadata: MutationAuditMetadata,
        side_effect: SideEffectIntent | None,
    ) -> str:
        material = json.dumps(
            {
                "actor_security_key": principal_security_key(principal),
                "command_fingerprint": command.fingerprint,
                "action": metadata.action,
                "side_effect_fingerprint": (
                    side_effect.fingerprint if side_effect is not None else None
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256(material.encode("utf-8")).hexdigest()

    def secure_write(
        self,
        *,
        principal: AuthenticatedPrincipal | None,
        tenant_context: TenantContext,
        role_bindings: RoleBindingResolver,
        command: WriteCommand,
        audit_metadata: MutationAuditMetadata,
        side_effect: SideEffectIntent | None = None,
    ) -> WriteResult:
        # Explicitly preserve deny-by-default authorization at the shared
        # security boundary before delegating to the atomic P18.5 contract.
        require_permission(
            principal=principal,
            tenant_context=tenant_context,
            resolver=role_bindings,
            permission=Permission.CANONICAL_MUTATE,
        )
        if principal is None:
            raise SecurityIdentityError("authenticated principal is required")
        principal_security_key(principal)
        return super().write(
            principal=principal,
            tenant_context=tenant_context,
            role_bindings=role_bindings,
            command=command,
            audit_metadata=audit_metadata,
            side_effect=side_effect,
        )
