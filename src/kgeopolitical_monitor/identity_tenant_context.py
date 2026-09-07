"""Provider-neutral P18.1 identity and authenticated tenant-context contracts.

This module deliberately does not select or connect an external identity
provider. It defines the trust boundaries future OIDC/OAuth2-class adapters
must satisfy while preserving the owner-local runtime as the active canonical
profile.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol, Sequence, runtime_checkable

from .shared_runtime_contract import AmbiguousTenantContextError, TenantContext


class AuthenticationError(RuntimeError):
    """Base error for fail-closed authentication processing."""


class UnauthenticatedError(AuthenticationError):
    """Raised when an authenticated principal is required but absent."""


class InvalidIdentityError(AuthenticationError):
    """Raised when provider-validated identity material violates the contract."""


class SessionExpiredError(AuthenticationError):
    """Raised when the presented session/token is expired."""


class SessionLifetimeError(AuthenticationError):
    """Raised when a session/token lifetime exceeds the approved policy."""


class RevocationCheckError(AuthenticationError):
    """Raised when revocation state cannot be established."""


class RevokedSessionError(AuthenticationError):
    """Raised when the session/token has been revoked."""


class TenantAuthorizationError(PermissionError):
    """Base error for authenticated tenant-scope authorization failures."""


class UnauthorizedTenantScopeError(TenantAuthorizationError):
    """Raised when the authenticated principal lacks the requested scope."""


class ServiceIdentityImpersonationError(TenantAuthorizationError):
    """Raised when a service identity is used where a human identity is required."""


class IdentityKind(str, Enum):
    HUMAN = "human"
    SERVICE = "service"


class CredentialKind(str, Enum):
    """Credential classes without any embedded role or owner authority."""

    HUMAN_SESSION_TOKEN = "human_session_token"
    SERVICE_ACCESS_TOKEN = "service_access_token"


class RevocationDecision(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


def _normalize_required(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise InvalidIdentityError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise InvalidIdentityError(f"{field_name} is required")
    return normalized


def _require_aware_timestamp(value: datetime, *, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InvalidIdentityError(f"{field_name} must be timezone-aware")
    return value


@dataclass(frozen=True)
class PresentedCredential:
    """Ephemeral credential envelope passed only to a validation adapter.

    The secret is excluded from repr/equality so it is not accidentally exposed
    in normal diagnostics. Credential kind carries no role and cannot grant
    owner authority by itself.
    """

    kind: CredentialKind
    secret: str = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, CredentialKind):
            raise InvalidIdentityError("credential kind is invalid")
        if not isinstance(self.secret, str) or not self.secret.strip():
            raise UnauthenticatedError("credential secret is required")


@dataclass(frozen=True)
class HumanIdentity:
    subject_id: str
    issuer: str
    session_id: str
    issued_at: datetime
    expires_at: datetime

    @property
    def identity_kind(self) -> IdentityKind:
        return IdentityKind.HUMAN

    @property
    def principal_id(self) -> str:
        return self.subject_id

    def __post_init__(self) -> None:
        object.__setattr__(self, "subject_id", _normalize_required(self.subject_id, field_name="subject_id"))
        object.__setattr__(self, "issuer", _normalize_required(self.issuer, field_name="issuer"))
        object.__setattr__(self, "session_id", _normalize_required(self.session_id, field_name="session_id"))
        issued = _require_aware_timestamp(self.issued_at, field_name="issued_at")
        expires = _require_aware_timestamp(self.expires_at, field_name="expires_at")
        if expires <= issued:
            raise InvalidIdentityError("expires_at must be after issued_at")


@dataclass(frozen=True)
class ServiceIdentity:
    service_id: str
    issuer: str
    session_id: str
    issued_at: datetime
    expires_at: datetime

    @property
    def identity_kind(self) -> IdentityKind:
        return IdentityKind.SERVICE

    @property
    def principal_id(self) -> str:
        return self.service_id

    def __post_init__(self) -> None:
        object.__setattr__(self, "service_id", _normalize_required(self.service_id, field_name="service_id"))
        object.__setattr__(self, "issuer", _normalize_required(self.issuer, field_name="issuer"))
        object.__setattr__(self, "session_id", _normalize_required(self.session_id, field_name="session_id"))
        issued = _require_aware_timestamp(self.issued_at, field_name="issued_at")
        expires = _require_aware_timestamp(self.expires_at, field_name="expires_at")
        if expires <= issued:
            raise InvalidIdentityError("expires_at must be after issued_at")


AuthenticatedPrincipal = HumanIdentity | ServiceIdentity


@dataclass(frozen=True)
class SessionValidationPolicy:
    """Provider-neutral short-lived credential policy."""

    max_lifetime: timedelta = timedelta(hours=1)
    max_future_issue_skew: timedelta = timedelta(seconds=30)

    def __post_init__(self) -> None:
        if self.max_lifetime <= timedelta(0):
            raise ValueError("max_lifetime must be positive")
        if self.max_future_issue_skew < timedelta(0):
            raise ValueError("max_future_issue_skew cannot be negative")


@runtime_checkable
class IdentityProviderAdapter(Protocol):
    """Provider-neutral adapter for standards-based credential validation.

    A concrete adapter is responsible for cryptographic/protocol validation,
    including issuer/audience/signature checks appropriate to its standard.
    P18.1 intentionally does not choose a provider.
    """

    @property
    def adapter_id(self) -> str:
        """Stable non-secret adapter identifier."""

    def validate_credential(
        self,
        credential: PresentedCredential,
        *,
        now: datetime,
    ) -> AuthenticatedPrincipal:
        """Return a provider-validated identity or raise AuthenticationError."""


@runtime_checkable
class SessionRevocationChecker(Protocol):
    """Revocation/session-status boundary required after identity validation."""

    def check(
        self,
        principal: AuthenticatedPrincipal,
        *,
        now: datetime,
    ) -> RevocationDecision:
        """Return ACTIVE, REVOKED, or UNKNOWN; UNKNOWN fails closed."""


def authenticate_principal(
    *,
    adapter: IdentityProviderAdapter,
    credential: PresentedCredential,
    revocation_checker: SessionRevocationChecker,
    now: datetime,
    policy: SessionValidationPolicy | None = None,
) -> AuthenticatedPrincipal:
    """Validate identity, temporal limits, credential kind, and revocation state."""

    policy = policy or SessionValidationPolicy()
    now = _require_aware_timestamp(now, field_name="now")

    adapter_id = str(adapter.adapter_id).strip()
    if not adapter_id:
        raise AuthenticationError("identity adapter_id is required")

    principal = adapter.validate_credential(credential, now=now)
    if not isinstance(principal, (HumanIdentity, ServiceIdentity)):
        raise InvalidIdentityError("identity adapter returned an unsupported principal type")

    if credential.kind is CredentialKind.HUMAN_SESSION_TOKEN and not isinstance(principal, HumanIdentity):
        raise InvalidIdentityError("human credential cannot authenticate a service identity")
    if credential.kind is CredentialKind.SERVICE_ACCESS_TOKEN and not isinstance(principal, ServiceIdentity):
        raise InvalidIdentityError("service credential cannot authenticate a human identity")

    if principal.issued_at > now + policy.max_future_issue_skew:
        raise InvalidIdentityError("identity issued_at is unacceptably in the future")
    if principal.expires_at <= now:
        raise SessionExpiredError("session/token is expired")
    if principal.expires_at - principal.issued_at > policy.max_lifetime:
        raise SessionLifetimeError("session/token lifetime exceeds policy")

    decision = revocation_checker.check(principal, now=now)
    if decision is RevocationDecision.REVOKED:
        raise RevokedSessionError("session/token is revoked")
    if decision is not RevocationDecision.ACTIVE:
        raise RevocationCheckError("revocation state is unknown; authentication fails closed")

    return principal


@dataclass(frozen=True)
class WorkspaceMembership:
    """Server-side binding from stable principal identity to tenant scope."""

    identity_kind: IdentityKind
    principal_id: str
    workspace_id: str
    project_ids: tuple[str, ...]
    active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.identity_kind, IdentityKind):
            raise InvalidIdentityError("membership identity_kind is invalid")
        object.__setattr__(self, "principal_id", _normalize_required(self.principal_id, field_name="principal_id"))
        object.__setattr__(self, "workspace_id", _normalize_required(self.workspace_id, field_name="workspace_id"))
        normalized_projects = tuple(dict.fromkeys(_normalize_required(p, field_name="project_id") for p in self.project_ids))
        if not normalized_projects:
            raise InvalidIdentityError("membership requires at least one project_id")
        object.__setattr__(self, "project_ids", normalized_projects)


@runtime_checkable
class WorkspaceMembershipResolver(Protocol):
    """Server-side resolver; request-supplied membership claims are not trusted."""

    def memberships_for(self, principal: AuthenticatedPrincipal) -> Sequence[WorkspaceMembership]:
        """Return current memberships for the authenticated principal."""


def require_human_principal(principal: AuthenticatedPrincipal | None) -> HumanIdentity:
    """Require a real authenticated human before future owner-only decisions."""

    if principal is None:
        raise UnauthenticatedError("authenticated human identity is required")
    if isinstance(principal, ServiceIdentity):
        raise ServiceIdentityImpersonationError(
            "service identity cannot satisfy human/owner authority requirements"
        )
    if not isinstance(principal, HumanIdentity):
        raise UnauthenticatedError("authenticated human identity is required")
    return principal


def derive_authenticated_tenant_context(
    *,
    principal: AuthenticatedPrincipal | None,
    memberships: WorkspaceMembershipResolver,
    requested_project_id: str,
    requested_workspace_id: str | None = None,
) -> TenantContext:
    """Derive tenant context from authenticated identity plus server-side membership.

    Request scope is treated as untrusted selection input. It can narrow an
    authorized server-side membership but cannot create membership or override
    the authenticated principal's workspace/project bindings.
    """

    if principal is None:
        raise UnauthenticatedError("authenticated principal is required")
    if not isinstance(principal, (HumanIdentity, ServiceIdentity)):
        raise UnauthenticatedError("authenticated principal is invalid")

    project_id = _normalize_required(requested_project_id, field_name="requested_project_id")
    workspace_id = None
    if requested_workspace_id is not None:
        workspace_id = _normalize_required(requested_workspace_id, field_name="requested_workspace_id")

    current = [
        membership
        for membership in memberships.memberships_for(principal)
        if membership.active
        and membership.identity_kind is principal.identity_kind
        and membership.principal_id == principal.principal_id
    ]

    if workspace_id is not None:
        current = [membership for membership in current if membership.workspace_id == workspace_id]
        if not current:
            raise UnauthorizedTenantScopeError("requested workspace is not authorized for principal")

    current = [membership for membership in current if project_id in membership.project_ids]
    if not current:
        raise UnauthorizedTenantScopeError("requested project is not authorized for principal")

    workspaces = {membership.workspace_id for membership in current}
    if len(workspaces) != 1:
        raise AmbiguousTenantContextError(
            "authorized tenant scope is ambiguous; an explicit authorized workspace is required"
        )

    return TenantContext(workspace_id=next(iter(workspaces)), project_id=project_id)
