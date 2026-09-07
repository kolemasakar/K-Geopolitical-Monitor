import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.identity_tenant_context import (
    HumanIdentity,
    IdentityKind,
    ServiceIdentity,
    UnauthenticatedError,
)
from kgeopolitical_monitor.rbac_authorization import (
    AccessDeniedError,
    Permission,
    Role,
    RoleBinding,
)
from kgeopolitical_monitor.shared_repository_concurrency import (
    IdempotencyConflictError,
    InMemorySharedRepositoryHarness,
    InvalidRepositoryCommandError,
    SharedObjectNotFoundError,
    TenantScopedSharedRepository,
    VersionConflictError,
    WriteCommand,
)
from kgeopolitical_monitor.shared_runtime_contract import StorageScope, TenantContext


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"


class BindingResolver:
    def __init__(self, *bindings: RoleBinding):
        self.bindings = bindings

    def bindings_for(self, principal):
        return self.bindings


def human(subject: str = "human-owner") -> HumanIdentity:
    issued = datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc)
    return HumanIdentity(
        subject_id=subject,
        issuer="test-issuer",
        session_id=f"session-{subject}",
        issued_at=issued,
        expires_at=issued + timedelta(minutes=30),
    )


def service(service_id: str = "service-reader") -> ServiceIdentity:
    issued = datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc)
    return ServiceIdentity(
        service_id=service_id,
        issuer="test-issuer",
        session_id=f"session-{service_id}",
        issued_at=issued,
        expires_at=issued + timedelta(minutes=30),
    )


def context(workspace: str = "workspace-a", project: str = "project-1") -> TenantContext:
    return TenantContext(workspace_id=workspace, project_id=project)


def binding(
    principal,
    *,
    workspace: str = "workspace-a",
    project: str | None = None,
    role: Role = Role.OWNER,
    service_permissions: tuple[Permission, ...] = (),
) -> RoleBinding:
    return RoleBinding(
        identity_kind=principal.identity_kind,
        principal_id=principal.principal_id,
        workspace_id=workspace,
        project_id=project,
        role=role,
        service_permissions=service_permissions,
    )


def command(
    *,
    object_id: str = "obj-1",
    payload=None,
    key: str = "idem-1",
    expected: int = 0,
    object_type: str = "event",
) -> WriteCommand:
    return WriteCommand(
        object_type=object_type,
        object_id=object_id,
        payload={"value": 1} if payload is None else payload,
        idempotency_key=key,
        expected_version=expected,
    )


def test_p18_4_harness_satisfies_provider_neutral_repository_protocol():
    repo = InMemorySharedRepositoryHarness()
    assert isinstance(repo, TenantScopedSharedRepository)
    assert repo.storage_scope is StorageScope.SHARED_CANONICAL
    assert repo.provider_id is None
    assert repo.persistent is False
    assert repo.contract_only is True


def test_create_requires_authenticated_principal():
    repo = InMemorySharedRepositoryHarness()
    with pytest.raises(UnauthenticatedError):
        repo.write(
            principal=None,
            tenant_context=context(),
            role_bindings=BindingResolver(),
            command=command(),
        )


def test_read_requires_authenticated_principal():
    repo = InMemorySharedRepositoryHarness()
    with pytest.raises(UnauthenticatedError):
        repo.get(
            principal=None,
            tenant_context=context(),
            role_bindings=BindingResolver(),
            object_type="event",
            object_id="obj-1",
        )


def test_write_requires_canonical_mutate_permission():
    principal = human("analyst")
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(
        binding(principal, role=Role.ANALYST, project="project-1")
    )
    with pytest.raises(AccessDeniedError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(),
        )


def test_admin_can_mutate_inside_exact_project_scope():
    principal = human("admin")
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(
        binding(principal, role=Role.ADMIN, project="project-1")
    )
    result = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
    )
    assert result.record.version == 1
    assert result.replayed is False


def test_service_can_receive_explicit_read_scope_but_not_canonical_mutate():
    principal = service()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(
        binding(
            principal,
            role=Role.SERVICE,
            project="project-1",
            service_permissions=(Permission.CANONICAL_READ,),
        )
    )
    with pytest.raises(AccessDeniedError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(),
        )


def test_create_if_absent_contract_uses_expected_version_zero():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    result = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(expected=0),
    )
    assert result.record.version == 1
    assert result.record.payload == {"value": 1}


def test_create_with_nonzero_expected_version_conflicts_deterministically():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    with pytest.raises(VersionConflictError) as exc_info:
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(expected=4),
        )
    assert exc_info.value.expected_version == 4
    assert exc_info.value.current_version == 0


def test_update_requires_last_observed_version_and_increments_once():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    first = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
    )
    second = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(payload={"value": 2}, key="idem-2", expected=first.record.version),
    )
    assert second.record.version == 2
    assert second.record.payload == {"value": 2}


def test_stale_writer_reports_expected_and_current_version():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
    )
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(payload={"value": 2}, key="idem-2", expected=1),
    )
    with pytest.raises(VersionConflictError) as exc_info:
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(payload={"value": 3}, key="idem-3", expected=1),
        )
    assert (exc_info.value.expected_version, exc_info.value.current_version) == (1, 2)


def test_two_concurrent_writers_from_same_version_have_one_winner_and_one_conflict():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
    )

    def writer(value: int):
        try:
            result = repo.write(
                principal=principal,
                tenant_context=context(),
                role_bindings=resolver,
                command=command(
                    payload={"value": value},
                    key=f"idem-race-{value}",
                    expected=1,
                ),
            )
            return ("success", result.record.version)
        except VersionConflictError as exc:
            return ("conflict", exc.current_version)

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(writer, (2, 3)))

    assert sorted(status for status, _ in outcomes) == ["conflict", "success"]
    current = repo.get(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        object_type="event",
        object_id="obj-1",
    )
    assert current.version == 2


def test_exact_duplicate_retry_is_replayed_without_duplicate_mutation():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    cmd = command()
    first = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=cmd,
    )
    replay = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=cmd,
    )
    assert first.replayed is False
    assert replay.replayed is True
    assert replay.record.version == 1
    assert replay.command_fingerprint == first.command_fingerprint
    assert repo.contract_counts() == (1, 1)


def test_reusing_idempotency_key_for_different_payload_fails_closed():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(payload={"value": 1}),
    )
    with pytest.raises(IdempotencyConflictError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(payload={"value": 9}),
        )


def test_reusing_idempotency_key_for_different_object_fails_closed():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(object_id="obj-1"),
    )
    with pytest.raises(IdempotencyConflictError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(object_id="obj-2"),
        )


def test_idempotency_key_is_scoped_by_workspace():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(
        binding(principal, workspace="workspace-a"),
        binding(principal, workspace="workspace-b"),
    )
    a = repo.write(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
        command=command(key="same-key"),
    )
    b = repo.write(
        principal=principal,
        tenant_context=context("workspace-b", "project-1"),
        role_bindings=resolver,
        command=command(key="same-key"),
    )
    assert a.record.tenant_context.workspace_id == "workspace-a"
    assert b.record.tenant_context.workspace_id == "workspace-b"
    assert repo.contract_counts() == (2, 2)


def test_idempotency_key_is_scoped_by_project():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal, workspace="workspace-a"))
    one = repo.write(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
        command=command(key="same-key"),
    )
    two = repo.write(
        principal=principal,
        tenant_context=context("workspace-a", "project-2"),
        role_bindings=resolver,
        command=command(key="same-key"),
    )
    assert one.record.tenant_context.project_id == "project-1"
    assert two.record.tenant_context.project_id == "project-2"
    assert repo.contract_counts() == (2, 2)


def test_same_object_id_is_isolated_across_workspaces():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(
        binding(principal, workspace="workspace-a"),
        binding(principal, workspace="workspace-b"),
    )
    for workspace, value in (("workspace-a", 1), ("workspace-b", 2)):
        repo.write(
            principal=principal,
            tenant_context=context(workspace, "project-1"),
            role_bindings=resolver,
            command=command(payload={"value": value}, key=f"key-{workspace}"),
        )
    a = repo.get(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
        object_type="event",
        object_id="obj-1",
    )
    b = repo.get(
        principal=principal,
        tenant_context=context("workspace-b", "project-1"),
        role_bindings=resolver,
        object_type="event",
        object_id="obj-1",
    )
    assert a.payload == {"value": 1}
    assert b.payload == {"value": 2}


def test_same_object_id_is_isolated_across_projects():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal, workspace="workspace-a"))
    for project, value in (("project-1", 1), ("project-2", 2)):
        repo.write(
            principal=principal,
            tenant_context=context("workspace-a", project),
            role_bindings=resolver,
            command=command(payload={"value": value}, key=f"key-{project}"),
        )
    assert repo.get(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
        object_type="event",
        object_id="obj-1",
    ).payload == {"value": 1}
    assert repo.get(
        principal=principal,
        tenant_context=context("workspace-a", "project-2"),
        role_bindings=resolver,
        object_type="event",
        object_id="obj-1",
    ).payload == {"value": 2}


def test_cross_workspace_context_without_binding_is_denied_before_lookup():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal, workspace="workspace-a"))
    with pytest.raises(AccessDeniedError):
        repo.get(
            principal=principal,
            tenant_context=context("workspace-b", "project-1"),
            role_bindings=resolver,
            object_type="event",
            object_id="guessed-id",
        )


def test_identifier_guess_in_another_authorized_project_cannot_escape_scope():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal, workspace="workspace-a"))
    repo.write(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
        command=command(object_id="secret-id"),
    )
    with pytest.raises(SharedObjectNotFoundError):
        repo.get(
            principal=principal,
            tenant_context=context("workspace-a", "project-2"),
            role_bindings=resolver,
            object_type="event",
            object_id="secret-id",
        )


def test_list_by_type_returns_only_exact_workspace_project_and_type():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(
        binding(principal, workspace="workspace-a"),
        binding(principal, workspace="workspace-b"),
    )
    cases = (
        ("workspace-a", "project-1", "event", "a1"),
        ("workspace-a", "project-1", "event", "a2"),
        ("workspace-a", "project-2", "event", "p2"),
        ("workspace-b", "project-1", "event", "b1"),
        ("workspace-a", "project-1", "forecast", "f1"),
    )
    for index, (workspace, project, object_type, object_id) in enumerate(cases):
        repo.write(
            principal=principal,
            tenant_context=context(workspace, project),
            role_bindings=resolver,
            command=command(
                object_id=object_id,
                object_type=object_type,
                key=f"key-{index}",
            ),
        )
    records = repo.list_by_type(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
        object_type="event",
    )
    assert [record.object_id for record in records] == ["a1", "a2"]


def test_duplicate_retry_returns_original_result_even_after_later_update():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    original_command = command(key="create-key")
    original = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=original_command,
    )
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(payload={"value": 2}, key="update-key", expected=1),
    )
    replay = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=original_command,
    )
    assert replay.replayed is True
    assert replay.record.version == original.record.version == 1
    current = repo.get(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        object_type="event",
        object_id="obj-1",
    )
    assert current.version == 2


def test_semantically_identical_mapping_order_has_same_command_fingerprint():
    left = command(payload={"b": 2, "a": 1})
    right = command(payload={"a": 1, "b": 2})
    assert left.payload_json == right.payload_json
    assert left.fingerprint == right.fingerprint


@pytest.mark.parametrize(
    "payload",
    [
        {"value": float("nan")},
        {"value": object()},
    ],
)
def test_nondeterministic_or_non_json_payload_is_rejected(payload):
    with pytest.raises(InvalidRepositoryCommandError):
        command(payload=payload)


@pytest.mark.parametrize("field", ["object_type", "object_id", "key"])
def test_blank_command_identity_fields_are_rejected(field):
    values = {"object_type": "event", "object_id": "obj-1", "key": "idem-1"}
    values[field] = "   "
    with pytest.raises(InvalidRepositoryCommandError):
        command(**values)


def test_negative_expected_version_is_rejected():
    with pytest.raises(InvalidRepositoryCommandError):
        command(expected=-1)


def test_record_payload_property_returns_detached_copy():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    result = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(payload={"nested": {"value": 1}}),
    )
    detached = result.record.payload
    detached["nested"]["value"] = 999
    assert result.record.payload == {"nested": {"value": 1}}


def test_failed_version_conflict_does_not_publish_idempotency_receipt():
    principal = human()
    repo = InMemorySharedRepositoryHarness()
    resolver = BindingResolver(binding(principal))
    with pytest.raises(VersionConflictError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(key="retryable", expected=5),
        )
    assert repo.contract_counts() == (0, 0)
    successful = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(key="retryable", expected=0),
    )
    assert successful.record.version == 1


def test_p18_4_contract_preserves_current_activation_provider_and_migration_boundaries():
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
