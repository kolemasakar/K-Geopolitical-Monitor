from hashlib import sha256
import inspect

import pytest

from kgeopolitical_monitor import shared_runtime_postgres_candidate as candidate
from kgeopolitical_monitor.shared_runtime_preflight_app import create_preflight_app


def _settings() -> candidate.PreflightCandidateSettings:
    return candidate.PreflightCandidateSettings(
        database_url="postgresql://example.invalid/kgm",
        bearer_token="synthetic-test-token",
        workspace_id="workspace-test",
        project_id="project-test",
        mode="synthetic_nonprod",
        database_network="railway_private",
    )


def test_public_api_exposes_no_client_selected_tenant_or_generic_fetch_surface() -> None:
    class Adapter:
        def __init__(self, settings):
            self.settings = settings

    app = create_preflight_app(_settings(), adapter_factory=Adapter)
    routes = {route.path: route for route in app.routes}

    assert "/preflight/fetch" not in routes
    assert "/preflight/probes/{workspace_id}/{project_id}" not in routes
    assert "/preflight/projects/{project_id}/probes" not in routes

    protected_paths = (
        "/preflight/probe",
        "/preflight/probes",
        "/preflight/rls-isolation",
    )
    for path in protected_paths:
        assert path in routes
        parameter_names = set(inspect.signature(routes[path].endpoint).parameters)
        assert "workspace_id" not in parameter_names
        assert "project_id" not in parameter_names
        assert "url" not in parameter_names
        assert "role" not in parameter_names


def test_public_safe_metadata_does_not_expose_tenant_ids_or_credentials() -> None:
    metadata = _settings().safe_metadata

    assert metadata["canonical"] is False
    assert metadata["production_live"] is False
    assert metadata["shared_runtime_active"] is False
    assert metadata["synthetic_data_only"] is True
    assert metadata["database_network"] == "railway_private"

    for forbidden in (
        "database_url",
        "bearer_token",
        "workspace_id",
        "project_id",
    ):
        assert forbidden not in metadata


def test_injection_style_probe_identifier_is_rejected_before_database_connect() -> None:
    connect_calls = 0

    def forbidden_connect(*args, **kwargs):
        nonlocal connect_calls
        connect_calls += 1
        raise AssertionError("database connection must not be attempted")

    adapter = candidate.PostgreSQLPreflightCandidate(
        _settings(),
        connect=forbidden_connect,
    )

    with pytest.raises(candidate.PreflightConfigurationError, match="probe_id is invalid"):
        adapter.write_probe(
            probe_id="x'; DROP TABLE kgm_preflight.tenant_probe; --",
            payload="synthetic",
        )

    assert connect_calls == 0


def test_adversarial_payload_is_hashed_and_never_interpolated_into_sql() -> None:
    calls: list[tuple[str, object | None]] = []
    payload = (
        "' OR 1=1 -- ; DROP TABLE tenant_probe; "
        "http://169.254.169.254/latest/meta-data/"
    )
    digest = sha256(payload.encode("utf-8")).hexdigest()

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, statement, parameters=None):
            calls.append((statement, parameters))

        def fetchone(self):
            return ("probe-safe", digest)

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def cursor(self):
            return Cursor()

        def commit(self):
            return None

    def connect(*args, **kwargs):
        return Connection()

    adapter = candidate.PostgreSQLPreflightCandidate(_settings(), connect=connect)
    result = adapter.write_probe(probe_id="probe-safe", payload=payload)

    insert_statement, insert_parameters = next(
        (statement, parameters)
        for statement, parameters in calls
        if statement.lstrip().startswith("INSERT INTO")
    )

    assert payload not in insert_statement
    assert payload not in repr(insert_parameters)
    assert digest in insert_parameters
    assert result == {"probe_id": "probe-safe", "payload_sha256": digest}


def test_runtime_role_and_rls_contract_blocks_privilege_escalation_paths() -> None:
    ddl = "\n".join(candidate.PREFLIGHT_DDL).casefold()

    assert candidate._SET_RUNTIME_ROLE_SQL == "SET LOCAL ROLE kgm_preflight_runtime"
    assert "nologin" in ddl
    assert "nosuperuser" in ddl
    assert "noinherit" in ddl
    assert "nobypassrls" in ddl
    assert "force row level security" in ddl
    assert "grant select, insert, update" in ddl

    for forbidden in (
        "grant all",
        "grant delete",
        "grant truncate",
        "grant create on",
        "create role kgm_preflight_runtime login",
        "bypassrls;",
    ):
        assert forbidden not in ddl
