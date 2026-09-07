import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from kgeopolitical_monitor.runtime_storage import RuntimeStoragePolicy
from kgeopolitical_monitor.shared_runtime_contract import (
    AmbiguousTenantContextError,
    MissingTenantContextError,
    RuntimeProfile,
    RuntimeProfileConfig,
    SharedRuntimeBoundaryError,
    SharedRuntimeDisabledError,
    StorageScope,
    TenantContext,
    bind_shared_adapter,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "p18_0" / "tenant_scopes.json"


@dataclass(frozen=True)
class _Adapter:
    adapter_id: str
    storage_scope: StorageScope


def _tenant_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_default_runtime_profile_remains_owner_local_and_disabled_for_shared():
    config = RuntimeProfileConfig()

    assert config.profile is RuntimeProfile.OWNER_LOCAL
    assert config.shared_enabled is False


def test_selecting_shared_profile_without_explicit_contract_enablement_fails_closed():
    with pytest.raises(SharedRuntimeDisabledError, match="shared/team runtime profile is disabled"):
        RuntimeProfileConfig(profile=RuntimeProfile.SHARED_TEAM)


def test_tenant_context_requires_workspace_and_project_scope():
    with pytest.raises(MissingTenantContextError, match="workspace_id is required"):
        TenantContext(workspace_id=" ", project_id="project-red")

    with pytest.raises(MissingTenantContextError, match="project_id is required"):
        TenantContext(workspace_id="workspace-alpha", project_id="")


def test_tenant_context_normalizes_explicit_scope_values():
    context = TenantContext(
        workspace_id="  workspace-alpha  ",
        project_id="  project-red  ",
    )

    assert context.workspace_id == "workspace-alpha"
    assert context.project_id == "project-red"


def test_tenant_context_resolution_rejects_missing_or_ambiguous_scope():
    with pytest.raises(MissingTenantContextError, match="workspace_id is required"):
        TenantContext.resolve(workspace_ids=[], project_ids=["project-red"])

    with pytest.raises(AmbiguousTenantContextError, match="workspace_id is ambiguous"):
        TenantContext.resolve(
            workspace_ids=["workspace-alpha", "workspace-beta"],
            project_ids=["project-red"],
        )

    with pytest.raises(AmbiguousTenantContextError, match="project_id is ambiguous"):
        TenantContext.resolve(
            workspace_ids=["workspace-alpha"],
            project_ids=["project-red", "project-blue"],
        )


def test_multi_workspace_project_fixture_proves_distinct_scopes_exist():
    fixture = _tenant_fixture()
    workspaces = fixture["workspaces"]

    assert {workspace["workspace_id"] for workspace in workspaces} == {
        "workspace-alpha",
        "workspace-beta",
    }
    assert workspaces[0]["projects"] == ["project-red", "project-blue"]
    assert workspaces[1]["projects"] == ["project-green"]

    contexts = {
        TenantContext(workspace["workspace_id"], project_id)
        for workspace in workspaces
        for project_id in workspace["projects"]
    }
    assert len(contexts) == 3


def test_owner_local_profile_cannot_bind_shared_adapter():
    adapter = _Adapter("test-shared", StorageScope.SHARED_CANONICAL)

    with pytest.raises(SharedRuntimeDisabledError, match="explicitly enabled shared/team profile"):
        bind_shared_adapter(config=RuntimeProfileConfig.owner_local(), adapter=adapter)


def test_shared_profile_rejects_project_local_sqlite_adapter():
    config = RuntimeProfileConfig.shared_team_for_contract_test()
    local_adapter = _Adapter("forbidden-local-sqlite", StorageScope.PROJECT_LOCAL_SQLITE)

    with pytest.raises(SharedRuntimeBoundaryError, match="cannot bind project-local SQLite"):
        bind_shared_adapter(config=config, adapter=local_adapter)


def test_shared_profile_contract_accepts_only_explicit_shared_canonical_scope():
    config = RuntimeProfileConfig.shared_team_for_contract_test()
    adapter = _Adapter("in-memory-contract-double", StorageScope.SHARED_CANONICAL)

    assert bind_shared_adapter(config=config, adapter=adapter) is adapter


def test_shared_profile_rejects_blank_adapter_identity():
    config = RuntimeProfileConfig.shared_team_for_contract_test()
    adapter = _Adapter("  ", StorageScope.SHARED_CANONICAL)

    with pytest.raises(SharedRuntimeBoundaryError, match="adapter_id is required"):
        bind_shared_adapter(config=config, adapter=adapter)


def test_existing_project_local_sqlite_storage_contract_is_unchanged(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    policy = RuntimeStoragePolicy(project_root)

    assert policy.resolve_database() == (
        project_root / "data" / "kgeopolitical_monitor.db"
    ).resolve()

    with pytest.raises(ValueError, match="project-local data directory"):
        policy.resolve_database(tmp_path / "shared" / "canonical.db")
