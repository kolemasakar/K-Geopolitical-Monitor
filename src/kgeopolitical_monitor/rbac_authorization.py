"""P18.2 deny-by-default RBAC and owner-only strategic gate contracts.

This module consumes the authenticated principal and server-derived TenantContext
from P18.1. It does not trust role claims from credentials or request payloads.
Role bindings are resolved server-side and scoped to a workspace, optionally to
one project. Strategic activation/cutover/provider/migration permissions require
a human workspace OWNER binding and never fall back to ADMIN or SERVICE.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Sequence, runtime_checkable

from .identity_tenant_context import (
    AuthenticatedPrincipal,
    HumanIdentity,
    IdentityKind,
    ServiceIdentity,
    UnauthenticatedError,
    require_human_principal,
)
from .shared_runtime_contract import TenantContext


class AuthorizationError(PermissionError):
    """Base error for fail-closed authorization processing."""


class AccessDeniedError(AuthorizationError):
    """Raised when no current server-side grant authorizes an action."""


class InvalidRoleBindingError(AuthorizationError):
    """Raised when a persisted/server-side role binding violates the contract."""


class OwnerOnlyGateError(AccessDeniedError):
    """Raised when an irreversible/strategic owner-only gate is not satisfied."""


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    SERVICE = "service"


class Permission(str, Enum):
    """Provider-neutral service-layer permissions for the P18.2 contract."""

    CANONICAL_READ = "canonical.read"
    CANONICAL_MUTATE = "canonical.mutate"
    ANALYSIS_MUTATE = "analysis.mutate"
    WORKSPACE_ADMIN = "workspace.admin"
    OPERATOR_ACTION = "operator.action"
    SERVICE_EXECUTE = "service.execute"

    STRATEGIC_PHASE14_ACTIVATE = "strategic.phase14.activate"
    STRATEGIC_PHASE17_PUBLICATION_ACTIVATE = "strategic.phase17.publication.activate"
    STRATEGIC_PHASE18_SHARED_RUNTIME_ACTIVATE = "strategic.phase18.shared_runtime.activate"
    STRATEGIC_PROVIDER_APPROVE = "strategic.provider.approve"
    STRATEGIC_CANONICAL_CUTOVER_APPROVE = "strategic.canonical_cutover.approve"
    STRATEGIC_MIGRATION_AUTHORIZE = "strategic.migration.authorize"


OWNER_ONLY_PERMISSIONS = frozenset(
    {
        Permission.STRATEGIC_PHASE14_ACTIVATE,
        Permission.STRATEGIC_PHASE17_PUBLICATION_ACTIVATE,
        Permission.STRATEGIC_PHASE18_SHARED_RUNTIME_ACTIVATE,
        Permission.STRATEGIC_PROVIDER_APPROVE,
        Permission.STRATEGIC_CANONICAL_CUTOVER_APPROVE,
        Permission.STRATEGIC_MIGRATION_AUTHORIZE,
    }
)


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: frozenset(
        {
            Permission.CANONICAL_READ,
            Permission.CANONICAL_MUTATE,
            Permission.ANALYSIS_MUTATE,
            Permission.WORKSPACE_ADMIN,
            Permission.OPERATOR_ACTION,
            *OWNER_ONLY_PERMISSIONS,
        }
    ),
    Role.ADMIN: frozenset(
        {
            Permission.CANONICAL_READ,
            Permission.CANONICAL_MUTATE,
            Permission.ANALYSIS_MUTATE,
            Permission.WORKSPACE_ADMIN,
            Permission.OPERATOR_ACTION,
        }
    ),
    Role.ANALYST: frozenset(
        {
            Permission.CANONICAL_READ,
            Permission.ANALYSIS_MUTATE,
            Permission.OPERATOR_ACTION,
        }
    ),
    Role.VIEWER: frozenset({Permission.CANONICAL_READ}),
    # SERVICE is deliberately empty. Service authority exists only through
    # enumerated service_permissions on the server-side binding.
    Role.SERVICE: frozenset(),
}


SERVICE_SCOPE_ALLOWLIST = frozenset(
    {
        Permission.CANONICAL_READ,
        Permission.ANALYSIS_MUTATE,
        Permission.OPERATOR_ACTION,
        Permission.SERVICE_EXECUTE,
    }
)


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise InvalidRoleBindingError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise InvalidRoleBindingError(f"{field_name} is required")
    return normalized


@dataclass(frozen=True)
class RoleBinding:
    """Server-side principal-to-role binding scoped to a workspace/project.

    ``project_id=None`` means a workspace-wide binding. A project-specific
    binding never grants authority in another project. SERVICE bindings carry
    explicit, allowlisted service scopes; all human-role permissions are derived
    from the fixed role matrix above rather than request/token claims.
    """

    identity_kind: IdentityKind
    principal_id: str
    workspace_id: str
    role: Role
    project_id: str | None = None
    service_permissions: tuple[Permission, ...] = ()
    active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.identity_kind, IdentityKind):
            raise InvalidRoleBindingError("identity_kind is invalid")
        if not isinstance(self.role, Role):
            raise InvalidRoleBindingError("role is invalid")

        object.__setattr__(self, "principal_id", _required_text(self.principal_id, field_name="principal_id"))
        object.__setattr__(self, "workspace_id", _required_text(self.workspace_id, field_name="workspace_id"))
        if self.project_id is not None:
            object.__setattr__(self, "project_id", _required_text(self.project_id, field_name="project_id"))

        normalized_scopes: list[Permission] = []
        for permission in self.service_permissions:
            if not isinstance(permission, Permission):
                raise InvalidRoleBindingError("service_permissions contains an invalid permission")
            if permission not in normalized_scopes:
                normalized_scopes.append(permission)
        object.__setattr__(self, "service_permissions", tuple(normalized_scopes))

        if self.identity_kind is IdentityKind.SERVICE:
            if self.role is not Role.SERVICE:
                raise InvalidRoleBindingError("service identity may only receive SERVICE role")
            disallowed = set(self.service_permissions) - SERVICE_SCOPE_ALLOWLIST
            if disallowed:
                raise InvalidRoleBindingError("service scope exceeds the P18.2 allowlist")
        else:
            if self.role is Role.SERVICE:
                raise InvalidRoleBindingError("human identity cannot receive SERVICE role")
            if self.service_permissions:
                raise InvalidRoleBindingError("human role binding cannot carry service_permissions")

        if self.role is Role.OWNER and self.identity_kind is not IdentityKind.HUMAN:
            raise InvalidRoleBindingError("OWNER role requires a human identity")


@runtime_checkable
class RoleBindingResolver(Protocol):
    """Server-side role source; request/token role claims are never authoritative."""

    def bindings_for(self, principal: AuthenticatedPrincipal) -> Sequence[RoleBinding]:
        """Return current bindings for the authenticated principal."""


@dataclass(frozen=True)
class AuthorizationGrant:
    principal_id: str
    identity_kind: IdentityKind
    tenant_context: TenantContext
    permission: Permission
    roles: tuple[Role, ...]


def _matching_bindings(
    *,
    principal: AuthenticatedPrincipal,
    tenant_context: TenantContext,
    resolver: RoleBindingResolver,
) -> list[RoleBinding]:
    if not isinstance(principal, (HumanIdentity, ServiceIdentity)):
        raise UnauthenticatedError("authenticated principal is required")
    if not isinstance(tenant_context, TenantContext):
        raise AccessDeniedError("server-derived tenant context is required")

    matches: list[RoleBinding] = []
    for binding in resolver.bindings_for(principal):
        if not isinstance(binding, RoleBinding):
            raise InvalidRoleBindingError("role resolver returned an unsupported binding")
        if not binding.active:
            continue
        if binding.identity_kind is not principal.identity_kind:
            continue
        if binding.principal_id != principal.principal_id:
            continue
        if binding.workspace_id != tenant_context.workspace_id:
            continue
        if binding.project_id is not None and binding.project_id != tenant_context.project_id:
            continue
        matches.append(binding)
    return matches


def effective_permissions(
    *,
    principal: AuthenticatedPrincipal | None,
    tenant_context: TenantContext,
    resolver: RoleBindingResolver,
) -> frozenset[Permission]:
    """Return current effective permissions, with empty set as deny-by-default."""

    if principal is None:
        return frozenset()

    permissions: set[Permission] = set()
    for binding in _matching_bindings(
        principal=principal,
        tenant_context=tenant_context,
        resolver=resolver,
    ):
        if binding.role is Role.SERVICE:
            permissions.update(binding.service_permissions)
        else:
            permissions.update(ROLE_PERMISSIONS[binding.role])
    return frozenset(permissions)


def require_permission(
    *,
    principal: AuthenticatedPrincipal | None,
    tenant_context: TenantContext,
    resolver: RoleBindingResolver,
    permission: Permission,
) -> AuthorizationGrant:
    """Require an explicit current permission for the exact tenant context.

    Owner-only strategic permissions are intentionally stricter than ordinary
    role permissions: they require a human principal plus an active workspace-
    wide OWNER binding. ADMIN, project-scoped OWNER, SERVICE, and permission
    unions cannot satisfy those strategic gates.
    """

    if principal is None:
        raise UnauthenticatedError("authenticated principal is required")
    if not isinstance(permission, Permission):
        raise AccessDeniedError("requested permission is invalid")

    matches = _matching_bindings(
        principal=principal,
        tenant_context=tenant_context,
        resolver=resolver,
    )

    if permission in OWNER_ONLY_PERMISSIONS:
        human = require_human_principal(principal)
        owner_bindings = [
            binding
            for binding in matches
            if binding.role is Role.OWNER
            and binding.identity_kind is IdentityKind.HUMAN
            and binding.principal_id == human.principal_id
            and binding.project_id is None
        ]
        if not owner_bindings:
            raise OwnerOnlyGateError(
                "strategic action requires an active human workspace OWNER binding"
            )
        return AuthorizationGrant(
            principal_id=human.principal_id,
            identity_kind=IdentityKind.HUMAN,
            tenant_context=tenant_context,
            permission=permission,
            roles=(Role.OWNER,),
        )

    allowed = effective_permissions(
        principal=principal,
        tenant_context=tenant_context,
        resolver=resolver,
    )
    if permission not in allowed:
        raise AccessDeniedError("permission denied by deny-by-default RBAC policy")

    roles: list[Role] = []
    for binding in matches:
        binding_permissions = (
            frozenset(binding.service_permissions)
            if binding.role is Role.SERVICE
            else ROLE_PERMISSIONS[binding.role]
        )
        if permission in binding_permissions and binding.role not in roles:
            roles.append(binding.role)

    return AuthorizationGrant(
        principal_id=principal.principal_id,
        identity_kind=principal.identity_kind,
        tenant_context=tenant_context,
        permission=permission,
        roles=tuple(roles),
    )
