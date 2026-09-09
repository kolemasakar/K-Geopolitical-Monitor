import asyncio

import pytest

from kgeopolitical_monitor.shared_runtime_postgres_candidate import (
    PreflightCandidateSettings,
    PreflightDatabaseError,
)
from kgeopolitical_monitor.shared_runtime_preflight_app import create_preflight_app


def _settings() -> PreflightCandidateSettings:
    return PreflightCandidateSettings(
        database_url="postgresql://example.invalid/kgm",
        bearer_token="synthetic-test-token",
        workspace_id="workspace-test",
        project_id="project-test",
        mode="synthetic_nonprod",
        database_network="railway_private",
    )


def _health_endpoint(app):
    return next(route.endpoint for route in app.routes if route.path == "/health")


def test_startup_selfcheck_publishes_only_safe_positive_evidence() -> None:
    class Adapter:
        def __init__(self, settings):
            self.settings = settings
            self.initialized = False

        def initialize(self):
            self.initialized = True

        def observe_rls_isolation(self):
            assert self.initialized is True
            return {
                "alternate_tenant_visible_rows": 0,
                "rls_isolation_observed": True,
            }

    app = create_preflight_app(_settings(), adapter_factory=Adapter)

    async def run() -> dict[str, object]:
        async with app.router.lifespan_context(app):
            return _health_endpoint(app)()

    health = asyncio.run(run())

    assert health["status"] == "ok"
    assert health["database_initialized"] is True
    assert health["rls_isolation_observed"] is True
    assert health["alternate_tenant_visible_rows"] == 0
    assert health["database_network"] == "railway_private"
    assert "database_url" not in health
    assert "bearer_token" not in health


def test_startup_selfcheck_fails_closed_when_rls_is_not_observed() -> None:
    class Adapter:
        def __init__(self, settings):
            self.settings = settings

        def initialize(self):
            return None

        def observe_rls_isolation(self):
            return {
                "alternate_tenant_visible_rows": 1,
                "rls_isolation_observed": False,
            }

    app = create_preflight_app(_settings(), adapter_factory=Adapter)

    async def run() -> None:
        async with app.router.lifespan_context(app):
            raise AssertionError("lifespan must not yield after failed RLS self-check")

    with pytest.raises(PreflightDatabaseError, match="RLS startup self-check"):
        asyncio.run(run())
