"""FastAPI surface for the disposable shared-runtime activation preflight.

The service is intentionally synthetic, non-canonical and non-production.  It
contains no owner-local SQLite integration and exposes no provider credentials,
private endpoints or secret material.
"""

from contextlib import asynccontextmanager
import os
import secrets
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from .shared_runtime_postgres_candidate import (
    PostgreSQLPreflightCandidate,
    PreflightCandidateError,
    PreflightCandidateSettings,
    PreflightDatabaseError,
)


API_VERSION = "0.1.0-a1-preflight"


class ProbeRequest(BaseModel):
    probe_id: str = Field(min_length=1, max_length=128)
    payload: str = Field(min_length=1, max_length=4096)


class ProbeResponse(BaseModel):
    probe_id: str
    payload_sha256: str


def settings_from_environment() -> PreflightCandidateSettings:
    """Load required candidate settings without defaulting unsafe values."""

    return PreflightCandidateSettings(
        database_url=os.environ.get("KGM_SHARED_DATABASE_URL", ""),
        bearer_token=os.environ.get("KGM_PREFLIGHT_BEARER_TOKEN", ""),
        workspace_id=os.environ.get("KGM_PREFLIGHT_WORKSPACE_ID", ""),
        project_id=os.environ.get("KGM_PREFLIGHT_PROJECT_ID", ""),
        mode=os.environ.get("KGM_SHARED_PREFLIGHT_MODE", ""),
        database_network=os.environ.get("KGM_SHARED_DATABASE_NETWORK", ""),
    )


AdapterFactory = Callable[[PreflightCandidateSettings], PostgreSQLPreflightCandidate]


def create_preflight_app(
    settings: PreflightCandidateSettings,
    *,
    adapter_factory: AdapterFactory = PostgreSQLPreflightCandidate,
) -> FastAPI:
    """Create the protected non-production preflight app."""

    adapter = adapter_factory(settings)
    startup_evidence: dict[str, object] = {
        "database_initialized": False,
        "rls_isolation_observed": False,
        "alternate_tenant_visible_rows": None,
    }

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        adapter.initialize()
        isolation = adapter.observe_rls_isolation()
        observed = isolation.get("rls_isolation_observed") is True
        alternate_rows = isolation.get("alternate_tenant_visible_rows")
        if not observed or alternate_rows != 0:
            raise PreflightDatabaseError("candidate RLS startup self-check failed")
        startup_evidence.update(
            {
                "database_initialized": True,
                "rls_isolation_observed": True,
                "alternate_tenant_visible_rows": 0,
            }
        )
        yield

    app = FastAPI(
        title="K-Geopolitical Monitor Shared Runtime Preflight",
        version=API_VERSION,
        description=(
            "Disposable synthetic non-production PostgreSQL candidate. "
            "Not canonical and not an activation endpoint."
        ),
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    bearer = HTTPBearer(auto_error=False)

    def authorize(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ) -> str:
        if credentials is None or credentials.scheme.casefold() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not secrets.compare_digest(
            credentials.credentials,
            settings.bearer_token,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials.credentials

    @app.get("/health", operation_id="getSharedRuntimePreflightHealth")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "api_version": API_VERSION,
            **settings.safe_metadata,
            **startup_evidence,
        }

    @app.post(
        "/preflight/probe",
        response_model=ProbeResponse,
        operation_id="writeSharedRuntimeSyntheticProbe",
    )
    def write_probe(
        request: ProbeRequest,
        _: str = Depends(authorize),
    ) -> dict[str, str]:
        try:
            return adapter.write_probe(probe_id=request.probe_id, payload=request.payload)
        except PreflightCandidateError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="candidate database unavailable",
            ) from exc

    @app.get("/preflight/probes", operation_id="listSharedRuntimeSyntheticProbes")
    def list_probes(_: str = Depends(authorize)) -> dict[str, object]:
        try:
            probes = adapter.list_probes()
        except PreflightCandidateError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="candidate database unavailable",
            ) from exc
        return {"count": len(probes), "probes": list(probes)}

    @app.get("/preflight/rls-isolation", operation_id="observeSharedRuntimeRLSIsolation")
    def rls_isolation(_: str = Depends(authorize)) -> dict[str, object]:
        try:
            return adapter.observe_rls_isolation()
        except PreflightCandidateError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="candidate database unavailable",
            ) from exc

    return app


def create_app_from_env() -> FastAPI:
    """Uvicorn ``--factory`` entrypoint for the disposable preflight service."""

    return create_preflight_app(settings_from_environment())
