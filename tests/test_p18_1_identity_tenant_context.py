import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.identity_tenant_context import (
    AuthenticationError,
    CredentialKind,
    HumanIdentity,
    IdentityKind,
    InvalidIdentityError,
    PresentedCredential,
    RevocationCheckError,
    RevocationDecision,
    RevokedSessionError,
    ServiceIdentity,
    ServiceIdentityImpersonationError,
    SessionExpiredError,
    SessionLifetimeError,
    SessionValidationPolicy,
    UnauthenticatedError,
    UnauthorizedTenantScopeError,
    WorkspaceMembership,
    authenticate_principal,
    derive_authenticated_tenant_context,
    require_human_principal,
)
from kgeopolitical_monitor.shared_runtime_contract import (
    AmbiguousTenantContextError,
    RuntimeProfile,
    RuntimeProfileConfig,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "p18_1" / "identity_memberships.json"
STATE = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
NOW = datetime(2026, 9, 7, 12, 30, tzinfo=timezone.utc)


@dataclass
class FakeIdentityAdapter:
    principal: HumanIdentity | ServiceIdentity
    adapter_id: str = "test-standards-adapter"

    def validate_credential(self, credential, *, now):
        return self.principal


@dataclass
class StaticRevocationChecker:
    decision: RevocationDecision = RevocationDecision.ACTIVE

    def check(self, principal, *, now):
        return self.decision


@dataclass
class StaticMembershipResolver:
    memberships: tuple[WorkspaceMembership, ...]

    def memberships_for(self, principal):
        return self.memberships


def _human(*, issued_at=None, expires_at=None):
    issued_at = issued_at or NOW - timedelta(minutes=5)
    expires_at = expires_at or NOW + timedelta(minutes=10)
    return HumanIdentity(
        subject_id="user-alpha",
        issuer="https://identity.example.invalid",
        session_id="human-session-1",
        issued_at=issued_at,
        expires_at=expires_at,
    )


def _service(*, issued_at=None, expires_at=None):
    issued_at = issued_at or NOW - timedelta(minutes=5)
    expires_at = expires_at or NOW + timedelta(minutes=10)
    return ServiceIdentity(
        service_id="service-ingest",
        issuer="https://identity.example.invalid",
        session_id="service-session-1",
        issued_at=issued_at,
        expires_at=expires_at,
    )


def _credential(kind):
    return PresentedCredential(kind=kind, secret="ephemeral-test-secret")


def _fixture_memberships():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    memberships = []
    for key, kind in (("human", IdentityKind.HUMAN), ("service", IdentityKind.SERVICE)):
        principal = data[key]
        for item in principal["workspaces"]:
            memberships.append(
                WorkspaceMembership(
                    identity_kind=kind,
                    principal_id=principal["principal_id"],
                    workspace_id=item["workspace_id"],
                    project_ids=tuple(item["projects"]),
                )
            )
    return tuple(memberships)


def test_presented_credential_does_not_expose_secret_in_repr():
    credential = _credential(CredentialKind.HUMAN_SESSION_TOKEN)
    assert "ephemeral-test-secret" not in repr(credential)


def test_human_credential_authenticates_only_after_active_revocation_check():
    principal = authenticate_principal(
        adapter=FakeIdentityAdapter(_human()),
        credential=_credential(CredentialKind.HUMAN_SESSION_TOKEN),
        revocation_checker=StaticRevocationChecker(),
        now=NOW,
    )
    assert isinstance(principal, HumanIdentity)
    assert principal.subject_id == "user-alpha"


def test_service_credential_authenticates_as_service_identity():
    principal = authenticate_principal(
        adapter=FakeIdentityAdapter(_service()),
        credential=_credential(CredentialKind.SERVICE_ACCESS_TOKEN),
        revocation_checker=StaticRevocationChecker(),
        now=NOW,
    )
    assert isinstance(principal, ServiceIdentity)
    assert principal.service_id == "service-ingest"


def test_empty_credential_fails_closed():
    with pytest.raises(UnauthenticatedError):
        PresentedCredential(kind=CredentialKind.HUMAN_SESSION_TOKEN, secret="  ")


@pytest.mark.parametrize(
    ("credential_kind", "principal"),
    (
        (CredentialKind.HUMAN_SESSION_TOKEN, _service()),
        (CredentialKind.SERVICE_ACCESS_TOKEN, _human()),
    ),
)
def test_human_and_service_credential_classes_cannot_cross_authenticate(credential_kind, principal):
    with pytest.raises(InvalidIdentityError):
        authenticate_principal(
            adapter=FakeIdentityAdapter(principal),
            credential=_credential(credential_kind),
            revocation_checker=StaticRevocationChecker(),
            now=NOW,
        )


def test_expired_session_fails_closed():
    principal = _human(
        issued_at=NOW - timedelta(minutes=20),
        expires_at=NOW - timedelta(seconds=1),
    )
    with pytest.raises(SessionExpiredError):
        authenticate_principal(
            adapter=FakeIdentityAdapter(principal),
            credential=_credential(CredentialKind.HUMAN_SESSION_TOKEN),
            revocation_checker=StaticRevocationChecker(),
            now=NOW,
        )


def test_session_longer_than_policy_fails_closed():
    principal = _human(
        issued_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(hours=2),
    )
    with pytest.raises(SessionLifetimeError):
        authenticate_principal(
            adapter=FakeIdentityAdapter(principal),
            credential=_credential(CredentialKind.HUMAN_SESSION_TOKEN),
            revocation_checker=StaticRevocationChecker(),
            now=NOW,
            policy=SessionValidationPolicy(max_lifetime=timedelta(hours=1)),
        )


def test_revoked_session_fails_closed():
    with pytest.raises(RevokedSessionError):
        authenticate_principal(
            adapter=FakeIdentityAdapter(_human()),
            credential=_credential(CredentialKind.HUMAN_SESSION_TOKEN),
            revocation_checker=StaticRevocationChecker(RevocationDecision.REVOKED),
            now=NOW,
        )


def test_unknown_revocation_state_fails_closed():
    with pytest.raises(RevocationCheckError):
        authenticate_principal(
            adapter=FakeIdentityAdapter(_human()),
            credential=_credential(CredentialKind.HUMAN_SESSION_TOKEN),
            revocation_checker=StaticRevocationChecker(RevocationDecision.UNKNOWN),
            now=NOW,
        )


def test_identity_issued_too_far_in_future_fails_closed():
    principal = _human(
        issued_at=NOW + timedelta(minutes=2),
        expires_at=NOW + timedelta(minutes=12),
    )
    with pytest.raises(InvalidIdentityError):
        authenticate_principal(
            adapter=FakeIdentityAdapter(principal),
            credential=_credential(CredentialKind.HUMAN_SESSION_TOKEN),
            revocation_checker=StaticRevocationChecker(),
            now=NOW,
        )


def test_missing_authenticated_principal_cannot_derive_tenant_context():
    resolver = StaticMembershipResolver(_fixture_memberships())
    with pytest.raises(UnauthenticatedError):
        derive_authenticated_tenant_context(
            principal=None,
            memberships=resolver,
            requested_workspace_id="workspace-alpha",
            requested_project_id="project-red",
        )


def test_explicit_authorized_workspace_and_project_derive_tenant_context():
    resolver = StaticMembershipResolver(_fixture_memberships())
    context = derive_authenticated_tenant_context(
        principal=_human(),
        memberships=resolver,
        requested_workspace_id="workspace-alpha",
        requested_project_id="project-red",
    )
    assert context.workspace_id == "workspace-alpha"
    assert context.project_id == "project-red"


def test_forged_workspace_scope_is_rejected_even_if_project_exists_elsewhere():
    resolver = StaticMembershipResolver(_fixture_memberships())
    with pytest.raises(UnauthorizedTenantScopeError):
        derive_authenticated_tenant_context(
            principal=_human(),
            memberships=resolver,
            requested_workspace_id="workspace-forged",
            requested_project_id="project-red",
        )


def test_unauthorized_project_scope_is_rejected():
    resolver = StaticMembershipResolver(_fixture_memberships())
    with pytest.raises(UnauthorizedTenantScopeError):
        derive_authenticated_tenant_context(
            principal=_human(),
            memberships=resolver,
            requested_workspace_id="workspace-alpha",
            requested_project_id="project-green",
        )


def test_workspace_can_be_derived_server_side_when_project_has_one_authorized_workspace():
    resolver = StaticMembershipResolver(_fixture_memberships())
    context = derive_authenticated_tenant_context(
        principal=_human(),
        memberships=resolver,
        requested_project_id="project-blue",
    )
    assert context.workspace_id == "workspace-alpha"
    assert context.project_id == "project-blue"


def test_ambiguous_authorized_workspace_requires_explicit_scope():
    resolver = StaticMembershipResolver(_fixture_memberships())
    with pytest.raises(AmbiguousTenantContextError):
        derive_authenticated_tenant_context(
            principal=_human(),
            memberships=resolver,
            requested_project_id="project-red",
        )


def test_service_identity_can_have_explicit_tenant_membership_without_becoming_human():
    resolver = StaticMembershipResolver(_fixture_memberships())
    service = _service()
    context = derive_authenticated_tenant_context(
        principal=service,
        memberships=resolver,
        requested_workspace_id="workspace-alpha",
        requested_project_id="project-red",
    )
    assert context.workspace_id == "workspace-alpha"
    assert service.identity_kind is IdentityKind.SERVICE


def test_human_requirement_accepts_human_identity():
    human = _human()
    assert require_human_principal(human) is human


def test_service_identity_cannot_satisfy_human_owner_authority_requirement():
    with pytest.raises(ServiceIdentityImpersonationError):
        require_human_principal(_service())


def test_credential_contract_contains_no_owner_bearer_token_class():
    assert {item.value for item in CredentialKind} == {
        "human_session_token",
        "service_access_token",
    }
    assert all("owner" not in item.value for item in CredentialKind)


def test_empty_identity_adapter_id_fails_closed():
    adapter = FakeIdentityAdapter(_human(), adapter_id="  ")
    with pytest.raises(AuthenticationError):
        authenticate_principal(
            adapter=adapter,
            credential=_credential(CredentialKind.HUMAN_SESSION_TOKEN),
            revocation_checker=StaticRevocationChecker(),
            now=NOW,
        )


def test_p18_1_preserves_owner_local_default_and_migration_033_boundary():
    config = RuntimeProfileConfig.owner_local()
    state = json.loads(STATE.read_text(encoding="utf-8"))

    assert config.profile is RuntimeProfile.OWNER_LOCAL
    assert config.shared_enabled is False
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in (ROOT / "migrations").glob("*.sql"))
