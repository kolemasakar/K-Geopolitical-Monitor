import pytest

from kgeopolitical_monitor.shared_runtime_contracts import (
    RuntimeProfile,
    SharedOperationContext,
    SharedRuntimeAdapter,
    SharedRuntimeDisabledError,
    SharedRuntimeSettings,
    TenantContext,
    TenantContextError,
    require_shared_context,
)


def test_local_profile_is_default_and_shared_is_disabled_by_default():
    settings = SharedRuntimeSettings()
    assert settings.resolve_profile() is RuntimeProfile.LOCAL
    assert settings.shared_enabled is False


def test_shared_profile_requires_explicit_enablement():
    with pytest.raises(SharedRuntimeDisabledError):
        SharedRuntimeSettings(profile=RuntimeProfile.SHARED).resolve_profile()

    settings = SharedRuntimeSettings(
        profile=RuntimeProfile.SHARED,
        shared_enabled=True,
    )
    assert settings.resolve_profile() is RuntimeProfile.SHARED


@pytest.mark.parametrize(
    ("workspace_id", "project_id"),
    [
        (None, "project-a"),
        ("workspace-a", None),
        ("", "project-a"),
        ("workspace-a", "   "),
        ("*", "project-a"),
        ("workspace-a", "default"),
    ],
)
def test_missing_or_ambiguous_tenant_context_fails_closed(workspace_id, project_id):
    with pytest.raises(TenantContextError):
        TenantContext.from_optional(
            workspace_id=workspace_id,
            project_id=project_id,
        )


def test_tenant_context_normalizes_but_preserves_both_security_boundaries():
    tenant = TenantContext(workspace_id="  ws-1 ", project_id=" project-9 ")
    assert tenant.workspace_id == "ws-1"
    assert tenant.project_id == "project-9"


def test_shared_operation_requires_explicit_tenant_context():
    with pytest.raises(TenantContextError):
        require_shared_context(None)

    context = SharedOperationContext(
        tenant=TenantContext(workspace_id="ws-a", project_id="project-a")
    )
    assert require_shared_context(context) is context


def test_multi_workspace_project_fixture_scopes_are_distinct_without_provider():
    contexts = {
        (workspace, project): SharedOperationContext(
            tenant=TenantContext(workspace_id=workspace, project_id=project)
        )
        for workspace, project in [
            ("ws-a", "project-a"),
            ("ws-a", "project-b"),
            ("ws-b", "project-a"),
        ]
    }

    assert len(contexts) == 3
    assert contexts[("ws-a", "project-a")].tenant != contexts[("ws-b", "project-a")].tenant
    assert contexts[("ws-a", "project-a")].tenant != contexts[("ws-a", "project-b")].tenant


def test_adapter_contract_is_provider_neutral_and_requires_scoped_methods():
    class FakeAdapter:
        def healthcheck(self) -> bool:
            return True

        def read(self, *, context, object_id):
            require_shared_context(context)
            return {"object_id": object_id, "workspace": context.tenant.workspace_id}

        def write(self, *, context, object_id, value) -> None:
            require_shared_context(context)

    adapter = FakeAdapter()
    assert isinstance(adapter, SharedRuntimeAdapter)

    context = SharedOperationContext(
        tenant=TenantContext(workspace_id="ws-a", project_id="project-a")
    )
    assert adapter.read(context=context, object_id="obj-1")["workspace"] == "ws-a"


def test_p18_0_contract_has_no_provider_or_local_database_configuration_surface():
    fields = set(SharedRuntimeSettings.__dataclass_fields__)
    assert fields == {"profile", "shared_enabled"}
    assert "database_url" not in fields
    assert "sqlite_path" not in fields
    assert "provider" not in fields
