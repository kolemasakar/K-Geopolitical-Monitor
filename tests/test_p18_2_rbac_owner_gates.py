from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.identity_tenant_context import (
    HumanIdentity,
    IdentityKind,
    ServiceIdentity,
    ServiceIdentityImpersonationError,
    UnauthenticatedError,
)
from kgeopolitical_monitor.rbac_authorization import (
    AccessDeniedError,
    InvalidRoleBindingError,
    OWNER_ONLY_PERMISSIONS,
    Permission,
    Role,
    RoleBinding,
    AuthorizationGrant,
    OwnerOnlyGateError,
    effective_permissions,
    require_permission,
)
from kgeopolitical_monitor.shared_runtime_contract import TenantContext


NOW = datetime(2026, 9, 7, 13, 0, tzinfo=timezone.utc)


def human(subject_id: str = "user-alpha") -> HumanIdentity:
    return HumanIdentity(
        subject_id=subject_id,
        issuer="test-issuer",
        session_id=f"session-{subject_id}",
        issued_at=NOW - timedelta(minutes=5),
        expires_at=NOW + timedelta(minutes=25),
    )


def service(service_id: str = "service-ingest") -> ServiceIdentity:
    return ServiceIdentity(
        service_id=service_id,
        issuer="test-issuer",
        session_id=f"session-{service_id}",
        issued_at=NOW - timedelta(minutes=5),
        expires_at=NOW + timedelta(minutes=25),
    )


CTX_RED = TenantContext(workspace_id="workspace-alpha", project_id="project-red")
CTX_BLUE = TenantContext(workspace_id="workspace-alpha", project_id="project-blue")
CTX_OTHER = TenantContext(workspace_id="workspace-beta", project_id="project-red")


@dataclass
class StaticResolver:
    bindings: tuple[object, ...]

    def bindings_for(self, principal):
        return self.bindings


def binding(
    role: Role,
    *,
    principal_id: str = "user-alpha",
    workspace_id: str = "workspace-alpha",
    project_id: str | None = None,
    active: bool = True,
) -> RoleBinding:
    return RoleBinding(
        identity_kind=IdentityKind.HUMAN,
        principal_id=principal_id,
        workspace_id=workspace_id,
        project_id=project_id,
        role=role,
        active=active,
    )


def service_binding(*permissions: Permission, active: bool = True) -> RoleBinding:
    return RoleBinding(
        identity_kind=IdentityKind.SERVICE,
        principal_id="service-ingest",
        workspace_id="workspace-alpha",
        project_id="project-red",
        role=Role.SERVICE,
        service_permissions=tuple(permissions),
        active=active,
    )


def test_role_binding_normalizes_and_preserves_workspace_scope():
    value = RoleBinding(
        identity_kind=IdentityKind.HUMAN,
        principal_id=" user-alpha ",
        workspace_id=" workspace-alpha ",
        project_id=" project-red ",
        role=Role.ANALYST,
    )
    assert value.principal_id == "user-alpha"
    assert value.workspace_id == "workspace-alpha"
    assert value.project_id == "project-red"


def test_human_identity_cannot_receive_service_role():
    with pytest.raises(InvalidRoleBindingError):
        binding(Role.SERVICE)


def test_service_identity_cannot_receive_human_role():
    with pytest.raises(InvalidRoleBindingError):
        RoleBinding(
            identity_kind=IdentityKind.SERVICE,
            principal_id="service-ingest",
            workspace_id="workspace-alpha",
            role=Role.ADMIN,
        )


def test_human_role_cannot_carry_service_permissions():
    with pytest.raises(InvalidRoleBindingError):
        RoleBinding(
            identity_kind=IdentityKind.HUMAN,
            principal_id="user-alpha",
            workspace_id="workspace-alpha",
            role=Role.ANALYST,
            service_permissions=(Permission.CANONICAL_READ,),
        )


def test_service_scope_cannot_include_owner_only_permission():
    with pytest.raises(InvalidRoleBindingError):
        service_binding(Permission.STRATEGIC_PHASE18_SHARED_RUNTIME_ACTIVATE)


def test_service_permissions_are_deduplicated():
    value = service_binding(
        Permission.CANONICAL_READ,
        Permission.CANONICAL_READ,
        Permission.SERVICE_EXECUTE,
    )
    assert value.service_permissions == (
        Permission.CANONICAL_READ,
        Permission.SERVICE_EXECUTE,
    )


def test_no_role_binding_means_deny_by_default():
    assert effective_permissions(
        principal=human(),
        tenant_context=CTX_RED,
        resolver=StaticResolver(()),
    ) == frozenset()


def test_missing_principal_has_no_effective_permissions():
    assert effective_permissions(
        principal=None,
        tenant_context=CTX_RED,
        resolver=StaticResolver((binding(Role.OWNER),)),
    ) == frozenset()


def test_inactive_binding_is_ignored():
    assert effective_permissions(
        principal=human(),
        tenant_context=CTX_RED,
        resolver=StaticResolver((binding(Role.ADMIN, active=False),)),
    ) == frozenset()


def test_binding_for_another_principal_is_ignored():
    assert effective_permissions(
        principal=human(),
        tenant_context=CTX_RED,
        resolver=StaticResolver((binding(Role.ADMIN, principal_id="user-other"),)),
    ) == frozenset()


def test_cross_workspace_binding_is_denied_even_with_same_project_id():
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=human(),
            tenant_context=CTX_OTHER,
            resolver=StaticResolver((binding(Role.ADMIN),)),
            permission=Permission.CANONICAL_READ,
        )


def test_project_scoped_binding_does_not_grant_other_project():
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=human(),
            tenant_context=CTX_BLUE,
            resolver=StaticResolver((binding(Role.ANALYST, project_id="project-red"),)),
            permission=Permission.ANALYSIS_MUTATE,
        )


def test_workspace_binding_applies_to_projects_inside_same_workspace():
    grant = require_permission(
        principal=human(),
        tenant_context=CTX_BLUE,
        resolver=StaticResolver((binding(Role.VIEWER),)),
        permission=Permission.CANONICAL_READ,
    )
    assert grant.tenant_context == CTX_BLUE
    assert grant.roles == (Role.VIEWER,)


def test_viewer_can_read_but_cannot_mutate_canonical_state():
    resolver = StaticResolver((binding(Role.VIEWER),))
    assert Permission.CANONICAL_READ in effective_permissions(
        principal=human(), tenant_context=CTX_RED, resolver=resolver
    )
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=resolver,
            permission=Permission.CANONICAL_MUTATE,
        )


def test_analyst_can_mutate_analysis_but_not_canonical_state():
    resolver = StaticResolver((binding(Role.ANALYST),))
    grant = require_permission(
        principal=human(),
        tenant_context=CTX_RED,
        resolver=resolver,
        permission=Permission.ANALYSIS_MUTATE,
    )
    assert grant.roles == (Role.ANALYST,)
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=resolver,
            permission=Permission.CANONICAL_MUTATE,
        )


def test_admin_can_mutate_canonical_state():
    grant = require_permission(
        principal=human(),
        tenant_context=CTX_RED,
        resolver=StaticResolver((binding(Role.ADMIN),)),
        permission=Permission.CANONICAL_MUTATE,
    )
    assert isinstance(grant, AuthorizationGrant)
    assert grant.roles == (Role.ADMIN,)


@pytest.mark.parametrize("permission", sorted(OWNER_ONLY_PERMISSIONS, key=lambda p: p.value))
def test_admin_cannot_bypass_any_owner_only_strategic_gate(permission):
    with pytest.raises(OwnerOnlyGateError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=StaticResolver((binding(Role.ADMIN),)),
            permission=permission,
        )


def test_analyst_cannot_perform_owner_only_strategic_action():
    with pytest.raises(OwnerOnlyGateError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=StaticResolver((binding(Role.ANALYST),)),
            permission=Permission.STRATEGIC_PHASE18_SHARED_RUNTIME_ACTIVATE,
        )


def test_project_scoped_owner_cannot_satisfy_workspace_strategic_gate():
    with pytest.raises(OwnerOnlyGateError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=StaticResolver((binding(Role.OWNER, project_id="project-red"),)),
            permission=Permission.STRATEGIC_CANONICAL_CUTOVER_APPROVE,
        )


@pytest.mark.parametrize("permission", sorted(OWNER_ONLY_PERMISSIONS, key=lambda p: p.value))
def test_workspace_owner_can_satisfy_each_owner_only_strategic_gate(permission):
    grant = require_permission(
        principal=human(),
        tenant_context=CTX_RED,
        resolver=StaticResolver((binding(Role.OWNER),)),
        permission=permission,
    )
    assert grant.roles == (Role.OWNER,)
    assert grant.permission is permission


def test_service_identity_has_no_implicit_permissions_from_service_role():
    assert effective_permissions(
        principal=service(),
        tenant_context=CTX_RED,
        resolver=StaticResolver((service_binding(),)),
    ) == frozenset()


def test_service_identity_can_use_only_explicit_allowlisted_scope():
    resolver = StaticResolver(
        (service_binding(Permission.CANONICAL_READ, Permission.SERVICE_EXECUTE),)
    )
    grant = require_permission(
        principal=service(),
        tenant_context=CTX_RED,
        resolver=resolver,
        permission=Permission.SERVICE_EXECUTE,
    )
    assert grant.roles == (Role.SERVICE,)
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=service(),
            tenant_context=CTX_RED,
            resolver=resolver,
            permission=Permission.ANALYSIS_MUTATE,
        )


def test_service_identity_cannot_satisfy_owner_only_gate():
    with pytest.raises(ServiceIdentityImpersonationError):
        require_permission(
            principal=service(),
            tenant_context=CTX_RED,
            resolver=StaticResolver((service_binding(Permission.CANONICAL_READ),)),
            permission=Permission.STRATEGIC_PROVIDER_APPROVE,
        )


def test_multiple_human_roles_union_non_strategic_permissions():
    resolver = StaticResolver((binding(Role.VIEWER), binding(Role.ANALYST)))
    permissions = effective_permissions(
        principal=human(), tenant_context=CTX_RED, resolver=resolver
    )
    assert Permission.CANONICAL_READ in permissions
    assert Permission.ANALYSIS_MUTATE in permissions
    assert Permission.CANONICAL_MUTATE not in permissions


def test_multiple_non_owner_roles_never_union_into_owner_authority():
    resolver = StaticResolver((binding(Role.ADMIN), binding(Role.ANALYST), binding(Role.VIEWER)))
    with pytest.raises(OwnerOnlyGateError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=resolver,
            permission=Permission.STRATEGIC_MIGRATION_AUTHORIZE,
        )


def test_unauthenticated_principal_fails_closed_for_required_permission():
    with pytest.raises(UnauthenticatedError):
        require_permission(
            principal=None,
            tenant_context=CTX_RED,
            resolver=StaticResolver(()),
            permission=Permission.CANONICAL_READ,
        )


def test_invalid_permission_value_fails_closed():
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=StaticResolver((binding(Role.OWNER),)),
            permission="strategic.phase18.shared_runtime.activate",  # type: ignore[arg-type]
        )


def test_role_resolver_returning_non_binding_fails_closed():
    with pytest.raises(InvalidRoleBindingError):
        require_permission(
            principal=human(),
            tenant_context=CTX_RED,
            resolver=StaticResolver((object(),)),
            permission=Permission.CANONICAL_READ,
        )


def test_non_tenant_context_fails_closed():
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=human(),
            tenant_context="workspace-alpha/project-red",  # type: ignore[arg-type]
            resolver=StaticResolver((binding(Role.OWNER),)),
            permission=Permission.CANONICAL_READ,
        )
