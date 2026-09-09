from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from kgeopolitical_monitor.shared_runtime_postgres_candidate import (
    PREFLIGHT_DDL,
    PREFLIGHT_MODE,
    PREFLIGHT_PROFILE,
    PRIVATE_NETWORK_MARKER,
    PostgreSQLPreflightCandidate,
    PreflightCandidateError,
    PreflightCandidateSettings,
    PreflightConfigurationError,
    PreflightDatabaseError,
)
from kgeopolitical_monitor.shared_runtime_preflight_app import (
    create_preflight_app,
    settings_from_environment,
)


TOKEN = "synthetic-preflight-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def _settings(**overrides):
    values = {
        "database_url": "postgresql://synthetic.invalid/preflight",
        "bearer_token": TOKEN,
        "workspace_id": "kgm-preflight-workspace",
        "project_id": "kgm-preflight-project",
        "mode": PREFLIGHT_MODE,
        "database_network": PRIVATE_NETWORK_MARKER,
    }
    values.update(overrides)
    return PreflightCandidateSettings(**values)


class FakeAdapter:
    def __init__(self, *, fail=False):
        self.initialized = False
        self.fail = fail
        self.probes = []

    def initialize(self):
        if self.fail:
            raise PreflightDatabaseError("synthetic failure")
        self.initialized = True

    def write_probe(self, *, probe_id, payload):
        if self.fail:
            raise PreflightDatabaseError("synthetic failure")
        item = {
            "probe_id": probe_id,
            "payload_sha256": sha256(payload.encode("utf-8")).hexdigest(),
        }
        self.probes = [row for row in self.probes if row["probe_id"] != probe_id]
        self.probes.append(item)
        return item

    def list_probes(self):
        if self.fail:
            raise PreflightDatabaseError("synthetic failure")
        return tuple(sorted(self.probes, key=lambda row: row["probe_id"]))

    def observe_rls_isolation(self):
        if self.fail:
            raise PreflightDatabaseError("synthetic failure")
        return {
            "alternate_tenant_visible_rows": 0,
            "rls_isolation_observed": True,
        }


class FakeCursor:
    def __init__(self):
        self.executions = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.executions.append((str(sql), params))

    def fetchone(self):
        return ("probe-a", "a" * 64)

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.commits = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


def test_settings_require_postgresql_and_fail_closed_mode_and_network():
    with pytest.raises(PreflightConfigurationError):
        _settings(database_url="sqlite:///not-allowed.db")
    with pytest.raises(PreflightConfigurationError):
        _settings(mode="production")
    with pytest.raises(PreflightConfigurationError):
        _settings(database_network="public")


def test_settings_reject_blank_secret_and_invalid_tenant_identifiers():
    with pytest.raises(PreflightConfigurationError):
        _settings(bearer_token="")
    with pytest.raises(PreflightConfigurationError):
        _settings(workspace_id="contains spaces")
    with pytest.raises(PreflightConfigurationError):
        _settings(project_id="")


def test_safe_metadata_never_exposes_dsn_token_or_tenant_identifiers():
    settings = _settings()
    metadata = settings.safe_metadata
    serialized = repr(metadata)
    assert metadata["profile"] == PREFLIGHT_PROFILE
    assert metadata["canonical"] is False
    assert metadata["production_live"] is False
    assert metadata["shared_runtime_active"] is False
    assert metadata["synthetic_data_only"] is True
    assert settings.database_url not in serialized
    assert settings.bearer_token not in serialized
    assert settings.workspace_id not in serialized
    assert settings.project_id not in serialized


def test_preflight_ddl_is_isolated_forced_rls_and_fail_closed():
    ddl = "\n".join(PREFLIGHT_DDL)
    assert "kgm_preflight.tenant_probe" in ddl
    assert "ENABLE ROW LEVEL SECURITY" in ddl
    assert "FORCE ROW LEVEL SECURITY" in ddl
    assert "current_setting('kgm.workspace_id', true)" in ddl
    assert "current_setting('kgm.project_id', true)" in ddl
    assert "WITH CHECK" in ddl
    assert "CREATE POLICY kgm_preflight_tenant_isolation" in ddl
    assert "migration" not in ddl.casefold()


def test_candidate_initialize_executes_only_bounded_preflight_ddl():
    connection = FakeConnection()
    calls = []

    def connect(dsn, **kwargs):
        calls.append((dsn, kwargs))
        return connection

    candidate = PostgreSQLPreflightCandidate(_settings(), connect=connect)
    candidate.initialize()

    assert len(calls) == 1
    assert calls[0][0] == _settings().database_url
    assert calls[0][1] == {"connect_timeout": 5, "autocommit": False}
    assert [sql for sql, _ in connection.cursor_instance.executions] == list(PREFLIGHT_DDL)
    assert all(params is None for _, params in connection.cursor_instance.executions)
    assert connection.commits == 1


def test_candidate_probe_uses_parameterized_tenant_context_and_payload_digest():
    connection = FakeConnection()

    def connect(*args, **kwargs):
        return connection

    candidate = PostgreSQLPreflightCandidate(_settings(), connect=connect)
    result = candidate.write_probe(probe_id="probe-a", payload="synthetic payload")
    executions = connection.cursor_instance.executions

    assert result == {"probe_id": "probe-a", "payload_sha256": "a" * 64}
    assert executions[0] == ("SET LOCAL ROLE kgm_preflight_runtime", None)
    assert executions[1][1] == (_settings().workspace_id,)
    assert executions[2][1] == (_settings().project_id,)
    insert_sql, insert_params = executions[3]
    assert "%s" in insert_sql
    assert insert_params[:3] == (
        _settings().workspace_id,
        _settings().project_id,
        "probe-a",
    )
    assert insert_params[3] == sha256(b"synthetic payload").hexdigest()
    assert "synthetic payload" not in insert_sql


def test_candidate_rejects_invalid_probe_identifier_before_database_access():
    touched = False

    def connect(*args, **kwargs):
        nonlocal touched
        touched = True
        raise AssertionError("must not connect")

    candidate = PostgreSQLPreflightCandidate(_settings(), connect=connect)
    with pytest.raises(PreflightConfigurationError):
        candidate.write_probe(probe_id="bad probe id", payload="synthetic")
    assert touched is False


def test_environment_loader_has_no_unsafe_defaults(monkeypatch):
    keys = [
        "KGM_SHARED_DATABASE_URL",
        "KGM_PREFLIGHT_BEARER_TOKEN",
        "KGM_PREFLIGHT_WORKSPACE_ID",
        "KGM_PREFLIGHT_PROJECT_ID",
        "KGM_SHARED_PREFLIGHT_MODE",
        "KGM_SHARED_DATABASE_NETWORK",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(PreflightConfigurationError):
        settings_from_environment()


def test_environment_loader_accepts_explicit_nonproduction_settings(monkeypatch):
    monkeypatch.setenv("KGM_SHARED_DATABASE_URL", _settings().database_url)
    monkeypatch.setenv("KGM_PREFLIGHT_BEARER_TOKEN", TOKEN)
    monkeypatch.setenv("KGM_PREFLIGHT_WORKSPACE_ID", _settings().workspace_id)
    monkeypatch.setenv("KGM_PREFLIGHT_PROJECT_ID", _settings().project_id)
    monkeypatch.setenv("KGM_SHARED_PREFLIGHT_MODE", PREFLIGHT_MODE)
    monkeypatch.setenv("KGM_SHARED_DATABASE_NETWORK", PRIVATE_NETWORK_MARKER)
    assert settings_from_environment() == _settings()


def test_health_is_public_safe_and_explicitly_noncanonical():
    fake = FakeAdapter()
    app = create_preflight_app(_settings(), adapter_factory=lambda _: fake)
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["profile"] == PREFLIGHT_PROFILE
    assert body["canonical"] is False
    assert body["production_live"] is False
    assert body["shared_runtime_active"] is False
    assert _settings().database_url not in response.text
    assert TOKEN not in response.text
    assert fake.initialized is True


def test_probe_endpoints_are_bearer_protected():
    fake = FakeAdapter()
    app = create_preflight_app(_settings(), adapter_factory=lambda _: fake)
    with TestClient(app) as client:
        assert client.get("/preflight/probes").status_code == 401
        assert client.get(
            "/preflight/probes",
            headers={"Authorization": "Bearer wrong-token"},
        ).status_code == 401
        assert client.post(
            "/preflight/probe",
            json={"probe_id": "probe-a", "payload": "synthetic"},
        ).status_code == 401
        assert client.get("/preflight/rls-isolation").status_code == 401


def test_authenticated_probe_round_trip_returns_digest_not_payload():
    fake = FakeAdapter()
    app = create_preflight_app(_settings(), adapter_factory=lambda _: fake)
    with TestClient(app) as client:
        write = client.post(
            "/preflight/probe",
            headers=AUTH,
            json={"probe_id": "probe-a", "payload": "synthetic payload"},
        )
        listing = client.get("/preflight/probes", headers=AUTH)
    assert write.status_code == 200
    assert write.json()["payload_sha256"] == sha256(b"synthetic payload").hexdigest()
    assert "synthetic payload" not in write.text
    assert listing.status_code == 200
    assert listing.json()["count"] == 1
    assert listing.json()["probes"][0]["probe_id"] == "probe-a"


def test_authenticated_rls_observation_reports_zero_cross_tenant_rows():
    fake = FakeAdapter()
    app = create_preflight_app(_settings(), adapter_factory=lambda _: fake)
    with TestClient(app) as client:
        response = client.get("/preflight/rls-isolation", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {
        "alternate_tenant_visible_rows": 0,
        "rls_isolation_observed": True,
    }


def test_database_failures_are_redacted_from_http_response():
    fake = FakeAdapter()
    app = create_preflight_app(_settings(), adapter_factory=lambda _: fake)
    with TestClient(app) as client:
        fake.fail = True
        response = client.get("/preflight/probes", headers=AUTH)
    assert response.status_code == 503
    assert response.json() == {"detail": "candidate database unavailable"}
    assert _settings().database_url not in response.text


def test_candidate_module_contains_no_sqlite_or_activation_transition():
    import inspect
    import kgeopolitical_monitor.shared_runtime_postgres_candidate as module

    source = inspect.getsource(module)
    assert "import sqlite3" not in source
    assert "PHASE_18_SHARED_RUNTIME_ACTIVE = YES" not in source
    assert "033_" not in source
