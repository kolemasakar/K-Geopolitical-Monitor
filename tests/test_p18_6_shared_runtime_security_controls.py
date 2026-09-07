import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.identity_tenant_context import (
    HumanIdentity,
    IdentityKind,
    UnauthorizedTenantScopeError,
    WorkspaceMembership,
    derive_authenticated_tenant_context,
)
from kgeopolitical_monitor.rbac_authorization import (
    AccessDeniedError,
    Permission,
    Role,
    RoleBinding,
    require_permission,
)
from kgeopolitical_monitor.shared_audit_outbox import MutationAuditMetadata
from kgeopolitical_monitor.shared_repository_concurrency import (
    IdempotencyConflictError,
    WriteCommand,
)
from kgeopolitical_monitor.shared_runtime_contract import TenantContext
from kgeopolitical_monitor.shared_runtime_security import (
    AuthPresentation,
    CsrfRequestContext,
    InMemorySecurityEventAuditSink,
    InMemorySessionBindingGuard,
    InMemoryTenantRateLimiter,
    IssuerAwareAuditedOutboxRepositoryHarness,
    IssuerBoundRoleBinding,
    IssuerBoundRoleBindingResolver,
    IssuerBoundWorkspaceMembership,
    IssuerBoundWorkspaceMembershipResolver,
    NetworkBoundaryViolation,
    QueryOperator,
    RequestSecurityViolation,
    ResourceLimitExceeded,
    SecretExposureError,
    SecretReference,
    SecurityEventKind,
    SessionBindingError,
    SessionCredentialEvidence,
    SharedRuntimeSecurityPolicy,
    StructuredQuery,
    TenantObjectReference,
    assert_secret_free_surface,
    principal_security_key,
    redact_sensitive,
    require_same_tenant_object,
    security_event_mapping,
    validate_csrf,
    validate_outbound_https_url,
    validate_page_size,
    validate_request_size,
    validate_structured_query,
)


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"


def now() -> datetime:
    return datetime(2026, 9, 7, 19, 0, tzinfo=timezone.utc)


def human(*, issuer: str = "https://issuer-a.example", subject: str = "owner-1", session: str = "s-1") -> HumanIdentity:
    issued = now() - timedelta(minutes=5)
    return HumanIdentity(
        subject_id=subject,
        issuer=issuer,
        session_id=session,
        issued_at=issued,
        expires_at=issued + timedelta(minutes=30),
    )


def tenant(workspace: str = "workspace-a", project: str = "project-1") -> TenantContext:
    return TenantContext(workspace_id=workspace, project_id=project)


def owner_binding(subject: str = "owner-1", *, workspace: str = "workspace-a") -> RoleBinding:
    return RoleBinding(
        identity_kind=IdentityKind.HUMAN,
        principal_id=subject,
        workspace_id=workspace,
        project_id=None,
        role=Role.OWNER,
    )


def issuer_owner_resolver(*issuers: str, subject: str = "owner-1") -> IssuerBoundRoleBindingResolver:
    return IssuerBoundRoleBindingResolver(
        *[
            IssuerBoundRoleBinding(
                issuer=issuer,
                binding=owner_binding(subject),
            )
            for issuer in issuers
        ]
    )


def policy(**overrides) -> SharedRuntimeSecurityPolicy:
    values = {
        "application_base_url": "https://shared.example.test",
        "allowed_egress_hosts": ("api.example.test",),
        "max_request_bytes": 1024,
        "max_page_size": 100,
        "max_requests_per_window": 2,
        "rate_window": timedelta(minutes=1),
    }
    values.update(overrides)
    return SharedRuntimeSecurityPolicy(**values)


def command(*, key: str = "idem-1") -> WriteCommand:
    return WriteCommand(
        object_type="event",
        object_id="event-1",
        payload={"summary": "safe"},
        idempotency_key=key,
        expected_version=0,
    )


def metadata() -> MutationAuditMetadata:
    return MutationAuditMetadata(
        action="event.update",
        correlation_id="corr-1",
        request_id="req-1",
        occurred_at=now(),
    )


def test_p18_6_security_policy_is_provider_neutral_contract_only():
    item = policy()
    assert item.provider_id is None
    assert item.contract_only is True
    assert item.network_reachability_observed is False
    assert item.datastore_public_ingress is False
    assert item.datastore_tls_required is True
    assert item.admin_public_ingress is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"application_base_url": "http://shared.example.test"},
        {"application_base_url": "https://user:password@shared.example.test"},
        {"datastore_public_ingress": True},
        {"datastore_tls_required": False},
        {"admin_public_ingress": True},
    ],
)
def test_shared_runtime_network_boundary_fails_closed(kwargs):
    with pytest.raises(NetworkBoundaryViolation):
        policy(**kwargs)


def test_secret_reference_is_opaque_and_rejects_inline_source():
    ref = SecretReference(source="env", name="KGM_SHARED_SIGNING_KEY")
    assert ref.locator == "env://KGM_SHARED_SIGNING_KEY"
    with pytest.raises(SecretExposureError):
        SecretReference(source="inline", name="actual-secret")


def test_recursive_redaction_removes_sensitive_keys_bearer_and_known_secret():
    secret = "super-secret-value"
    value = {
        "authorization": "Bearer abcdefghijklmnop",
        "nested": {
            "message": f"prefix {secret} suffix",
            "api_key": "raw-key",
        },
    }
    redacted = redact_sensitive(value, known_secret_values=(secret,))
    encoded = json.dumps(redacted, sort_keys=True)
    assert secret not in encoded
    assert "abcdefghijklmnop" not in encoded
    assert "raw-key" not in encoded
    assert encoded.count("[REDACTED]") >= 3


@pytest.mark.parametrize(
    "value,secrets",
    [
        ({"password": "x"}, ()),
        ({"message": "Bearer abcdefghijklmnop"}, ()),
        ({"message": "contains private-material-123"}, ("private-material-123",)),
    ],
)
def test_forbidden_surfaces_reject_secret_material(value, secrets):
    with pytest.raises(SecretExposureError):
        assert_secret_free_surface(value, known_secret_values=secrets)


def test_outbound_https_requires_explicit_allowlist():
    assert (
        validate_outbound_https_url(
            "https://api.example.test/v1/resource",
            allowed_hosts=("api.example.test",),
        )
        == "https://api.example.test/v1/resource"
    )
    with pytest.raises(NetworkBoundaryViolation):
        validate_outbound_https_url(
            "https://other.example.test/v1",
            allowed_hosts=("api.example.test",),
        )


@pytest.mark.parametrize(
    "url,allowed",
    [
        ("http://api.example.test/x", ("api.example.test",)),
        ("https://localhost/x", ("localhost",)),
        ("https://127.0.0.1/x", ("127.0.0.1",)),
        ("https://10.0.0.1/x", ("10.0.0.1",)),
        ("https://169.254.169.254/latest/meta-data", ("169.254.169.254",)),
        ("https://api.example.test:8443/x", ("api.example.test",)),
        ("https://user:password@api.example.test/x", ("api.example.test",)),
    ],
)
def test_ssrf_boundary_rejects_unsafe_targets(url, allowed):
    with pytest.raises(NetworkBoundaryViolation):
        validate_outbound_https_url(url, allowed_hosts=allowed)


def test_structured_query_rejects_raw_expression_and_non_allowlisted_field():
    query = StructuredQuery(field="status", operator=QueryOperator.EQ, value="open")
    assert validate_structured_query(query, allowed_fields=("status", "title")) is query
    with pytest.raises(RequestSecurityViolation):
        validate_structured_query("status = 'open' OR 1=1", allowed_fields=("status",))
    with pytest.raises(RequestSecurityViolation):
        validate_structured_query(
            StructuredQuery(field="sql", operator=QueryOperator.EQ, value="DROP TABLE"),
            allowed_fields=("status",),
        )


def test_idor_reference_must_match_authenticated_tenant():
    ref = TenantObjectReference(
        workspace_id="workspace-a",
        project_id="project-1",
        object_type="event",
        object_id="event-1",
    )
    assert require_same_tenant_object(tenant_context=tenant(), object_ref=ref) is ref
    with pytest.raises(RequestSecurityViolation):
        require_same_tenant_object(
            tenant_context=tenant("workspace-b", "project-1"),
            object_ref=ref,
        )


def test_bearer_header_is_not_cookie_csrf_ambient_authority():
    validate_csrf(
        CsrfRequestContext(presentation=AuthPresentation.BEARER_HEADER),
        allowed_origins=(),
    )


def test_cookie_session_requires_https_origin_and_double_submit_match():
    validate_csrf(
        CsrfRequestContext(
            presentation=AuthPresentation.COOKIE_SESSION,
            origin="https://shared.example.test",
            csrf_cookie="csrf-value",
            csrf_header="csrf-value",
        ),
        allowed_origins=("https://shared.example.test",),
    )
    with pytest.raises(RequestSecurityViolation):
        validate_csrf(
            CsrfRequestContext(
                presentation=AuthPresentation.COOKIE_SESSION,
                origin="https://shared.example.test",
                csrf_cookie="csrf-value",
                csrf_header="wrong-value",
            ),
            allowed_origins=("https://shared.example.test",),
        )
    with pytest.raises(RequestSecurityViolation):
        validate_csrf(
            CsrfRequestContext(
                presentation=AuthPresentation.COOKIE_SESSION,
                origin="https://evil.example.test",
                csrf_cookie="csrf-value",
                csrf_header="csrf-value",
            ),
            allowed_origins=("https://shared.example.test",),
        )


def test_principal_security_key_is_issuer_scoped():
    a = human(issuer="https://issuer-a.example")
    b = human(issuer="https://issuer-b.example")
    assert a.principal_id == b.principal_id
    assert principal_security_key(a) != principal_security_key(b)
    assert "issuer-a.example" in principal_security_key(a)


def test_issuer_bound_membership_resolver_blocks_same_subject_from_other_issuer():
    a = human(issuer="https://issuer-a.example")
    b = human(issuer="https://issuer-b.example")
    membership = WorkspaceMembership(
        identity_kind=IdentityKind.HUMAN,
        principal_id=a.principal_id,
        workspace_id="workspace-a",
        project_ids=("project-1",),
    )
    resolver = IssuerBoundWorkspaceMembershipResolver(
        IssuerBoundWorkspaceMembership(
            issuer=a.issuer,
            membership=membership,
        )
    )
    assert derive_authenticated_tenant_context(
        principal=a,
        memberships=resolver,
        requested_workspace_id="workspace-a",
        requested_project_id="project-1",
    ) == tenant()
    with pytest.raises(UnauthorizedTenantScopeError):
        derive_authenticated_tenant_context(
            principal=b,
            memberships=resolver,
            requested_workspace_id="workspace-a",
            requested_project_id="project-1",
        )


def test_issuer_bound_rbac_blocks_same_subject_from_other_issuer():
    a = human(issuer="https://issuer-a.example")
    b = human(issuer="https://issuer-b.example")
    resolver = issuer_owner_resolver(a.issuer)
    grant = require_permission(
        principal=a,
        tenant_context=tenant(),
        resolver=resolver,
        permission=Permission.CANONICAL_MUTATE,
    )
    assert grant.permission is Permission.CANONICAL_MUTATE
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=b,
            tenant_context=tenant(),
            resolver=resolver,
            permission=Permission.CANONICAL_MUTATE,
        )


def test_session_binding_guard_rejects_credential_rebinding_but_is_issuer_scoped():
    guard = InMemorySessionBindingGuard()
    evidence_a = SessionCredentialEvidence("a" * 64)
    evidence_b = SessionCredentialEvidence("b" * 64)
    principal_a = human(issuer="https://issuer-a.example", session="shared-session-id")
    principal_b = human(issuer="https://issuer-b.example", session="shared-session-id")

    guard.validate(principal=principal_a, evidence=evidence_a)
    guard.validate(principal=principal_a, evidence=evidence_a)
    with pytest.raises(SessionBindingError):
        guard.validate(principal=principal_a, evidence=evidence_b)

    guard.validate(principal=principal_b, evidence=evidence_b)


def test_tenant_rate_limiter_isolated_by_workspace_and_project():
    limiter = InMemoryTenantRateLimiter(policy())
    at = now()
    limiter.check(tenant_context=tenant(), now=at)
    limiter.check(tenant_context=tenant(), now=at + timedelta(seconds=1))
    with pytest.raises(ResourceLimitExceeded):
        limiter.check(tenant_context=tenant(), now=at + timedelta(seconds=2))

    limiter.check(
        tenant_context=tenant("workspace-b", "project-1"),
        now=at + timedelta(seconds=2),
    )


def test_request_and_page_resource_limits_fail_closed():
    item = policy(max_request_bytes=100, max_page_size=10)
    assert validate_request_size(100, policy=item) == 100
    assert validate_page_size(10, policy=item) == 10
    with pytest.raises(ResourceLimitExceeded):
        validate_request_size(101, policy=item)
    with pytest.raises(ResourceLimitExceeded):
        validate_page_size(11, policy=item)


def test_security_event_mapping_is_truth_neutral():
    mapping = security_event_mapping(SecurityEventKind.PRIVILEGE_ESCALATION_DENIED)
    assert mapping.audit_action == "security.privilege_escalation_denied"
    assert mapping.severity == "critical"
    assert mapping.factual_verification_authority is False


def test_security_event_sink_redacts_secrets_and_is_append_only_value():
    sink = InMemorySecurityEventAuditSink()
    principal = human()
    resolver = issuer_owner_resolver(principal.issuer)
    record = sink.record(
        tenant_context=tenant(),
        principal=principal,
        event_kind=SecurityEventKind.SECRET_EXPOSURE_BLOCKED,
        occurred_at=now(),
        details={
            "authorization": "Bearer abcdefghijklmnop",
            "message": "saw super-secret-value",
        },
        known_secret_values=("super-secret-value",),
    )
    assert record.actor_security_key == principal_security_key(principal)
    assert record.factual_verification_authority is False
    assert "super-secret-value" not in record.details_json
    assert "abcdefghijklmnop" not in record.details_json
    with pytest.raises(FrozenInstanceError):
        record.severity = "low"

    records = sink.list_records(
        principal=principal,
        tenant_context=tenant(),
        role_bindings=resolver,
    )
    assert records == (record,)


def test_security_event_reads_are_exact_tenant_authorized():
    sink = InMemorySecurityEventAuditSink()
    principal = human()
    sink.record(
        tenant_context=tenant("workspace-a", "project-1"),
        principal=principal,
        event_kind=SecurityEventKind.IDOR_DENIED,
        occurred_at=now(),
        details={"object_id": "event-x"},
    )
    other_resolver = IssuerBoundRoleBindingResolver(
        IssuerBoundRoleBinding(
            issuer=principal.issuer,
            binding=owner_binding(principal.principal_id, workspace="workspace-b"),
        )
    )
    with pytest.raises(AccessDeniedError):
        sink.list_records(
            principal=principal,
            tenant_context=tenant("workspace-a", "project-1"),
            role_bindings=other_resolver,
        )
    assert sink.list_records(
        principal=principal,
        tenant_context=tenant("workspace-b", "project-1"),
        role_bindings=other_resolver,
    ) == ()


def test_p18_6_retry_identity_rejects_same_subject_from_different_issuer():
    repo = IssuerAwareAuditedOutboxRepositoryHarness()
    a = human(issuer="https://issuer-a.example")
    b = human(issuer="https://issuer-b.example")
    resolver = issuer_owner_resolver(a.issuer, b.issuer)
    repo.secure_write(
        principal=a,
        tenant_context=tenant(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
    )
    with pytest.raises(IdempotencyConflictError):
        repo.secure_write(
            principal=b,
            tenant_context=tenant(),
            role_bindings=resolver,
            command=command(),
            audit_metadata=metadata(),
        )
    assert repo.contract_counts() == (1, 1, 1, 0)


def test_p18_6_exact_retry_same_issuer_remains_idempotent():
    repo = IssuerAwareAuditedOutboxRepositoryHarness()
    principal = human()
    resolver = issuer_owner_resolver(principal.issuer)
    first = repo.secure_write(
        principal=principal,
        tenant_context=tenant(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
    )
    replay = repo.secure_write(
        principal=principal,
        tenant_context=tenant(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
    )
    assert first.replayed is False
    assert replay.replayed is True
    assert repo.contract_counts() == (1, 1, 1, 0)


def test_privilege_escalation_denial_can_be_mapped_to_private_security_audit():
    principal = human()
    viewer = RoleBinding(
        identity_kind=IdentityKind.HUMAN,
        principal_id=principal.principal_id,
        workspace_id="workspace-a",
        project_id="project-1",
        role=Role.VIEWER,
    )
    resolver = IssuerBoundRoleBindingResolver(
        IssuerBoundRoleBinding(issuer=principal.issuer, binding=viewer)
    )
    with pytest.raises(AccessDeniedError):
        require_permission(
            principal=principal,
            tenant_context=tenant(),
            resolver=resolver,
            permission=Permission.CANONICAL_MUTATE,
        )

    sink = InMemorySecurityEventAuditSink()
    event = sink.record(
        tenant_context=tenant(),
        principal=principal,
        event_kind=SecurityEventKind.PRIVILEGE_ESCALATION_DENIED,
        occurred_at=now(),
        details={"requested_permission": Permission.CANONICAL_MUTATE.value},
    )
    assert event.audit_action == "security.privilege_escalation_denied"
    assert event.severity == "critical"


def test_export_backup_and_public_surface_review_rejects_secret_bearing_fields():
    safe = {
        "workspace_id": "workspace-a",
        "project_id": "project-1",
        "summary": "public-safe",
    }
    assert_secret_free_surface(safe)
    for surface in (
        {"backup_password": "secret"},
        {"export_token": "secret"},
        {"private_key": "secret"},
        {"credential": "secret"},
    ):
        with pytest.raises(SecretExposureError):
            assert_secret_free_surface(surface)


def test_p18_6_preserves_phase18_activation_and_migration_boundaries():
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert int(state["roadmap"]["state_sync_version"].split(".")[1]) >= 30
    assert "P18_5_VALIDATED" in state["phases"]["18"]
    assert (
        "P18_6_READY" in state["phases"]["18"]
        or "P18_6_VALIDATED" in state["phases"]["18"]
    )
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert state["verification_authority"] == "P13.5/P13.6"
