from pathlib import Path

from kgeopolitical_monitor import shared_runtime_postgres_candidate as candidate


ROOT = Path(__file__).resolve().parents[1]


def test_preflight_runtime_role_is_nonlogin_nonsuperuser_nobypassrls() -> None:
    ddl = "\n".join(candidate.PREFLIGHT_DDL).casefold()

    assert candidate.PREFLIGHT_RUNTIME_ROLE == "kgm_preflight_runtime"
    assert "create role kgm_preflight_runtime" in ddl
    assert "nologin" in ddl
    assert "nosuperuser" in ddl
    assert "nocreatedb" in ddl
    assert "nocreaterole" in ddl
    assert "noinherit" in ddl
    assert "nobypassrls" in ddl
    assert "login password" not in ddl
    assert "password" not in ddl


def test_preflight_runtime_role_has_only_required_schema_and_table_grants() -> None:
    ddl = "\n".join(candidate.PREFLIGHT_DDL).casefold()

    assert "grant kgm_preflight_runtime to current_user" in ddl
    assert "grant usage on schema kgm_preflight to kgm_preflight_runtime" in ddl
    assert (
        "grant select, insert, update on kgm_preflight.tenant_probe "
        "to kgm_preflight_runtime"
    ) in ddl
    for forbidden in (
        "grant all",
        "grant create on",
        "grant delete on",
        "grant truncate on",
        "grant references on",
        "grant trigger on",
    ):
        assert forbidden not in ddl


def test_tenant_context_switches_role_before_setting_tenant_gucs() -> None:
    calls: list[tuple[str, object | None]] = []

    class Cursor:
        def execute(self, statement, parameters=None):
            calls.append((statement, parameters))

    candidate.PostgreSQLPreflightCandidate._set_tenant(
        Cursor(),
        workspace_id="workspace-test",
        project_id="project-test",
    )

    assert calls == [
        ("SET LOCAL ROLE kgm_preflight_runtime", None),
        ("SELECT set_config('kgm.workspace_id', %s, true)", ("workspace-test",)),
        ("SELECT set_config('kgm.project_id', %s, true)", ("project-test",)),
    ]


def test_runtime_role_is_not_exposed_as_a_new_secret_or_configuration_surface() -> None:
    text = (
        ROOT / "src/kgeopolitical_monitor/shared_runtime_postgres_candidate.py"
    ).read_text(encoding="utf-8").casefold()

    assert "kgm_preflight_runtime_password" not in text
    assert "runtime_role_password" not in text
    assert "runtime_role_dsn" not in text
    assert "create role kgm_preflight_runtime login" not in text
