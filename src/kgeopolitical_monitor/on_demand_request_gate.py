"""Owner-only manual on-demand request validation; offline synthetic mode exclusively."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from .on_demand_dispatcher import OnDemandRequest

AUTHORIZED_REPOSITORY = "kolemasakar/K-Geopolitical-Monitor"
AUTHORIZED_OWNER = "kolemasakar"
ALLOWED_MODE = "OFFLINE_SYNTHETIC"


@dataclass(frozen=True)
class AuthorizedRequest:
    mode: str
    topic_sha256: str
    request_id: str


def authorize_manual_request(
    *, repository: str, actor: str, ref: str, event_name: str,
    mode: str, topic: str, request_id: str,
) -> AuthorizedRequest:
    """Reject all untrusted event sources and all live execution modes.

    GitHub Actions supplies repository/actor/ref/event from host context, not
    user-configurable workflow inputs. Not a replacement for GitHub RBAC.
    """
    if (repository != AUTHORIZED_REPOSITORY or actor != AUTHORIZED_OWNER
            or ref != "refs/heads/main" or event_name != "workflow_dispatch"):
        raise PermissionError("manual owner execution context not authorized")
    if mode != ALLOWED_MODE:
        raise PermissionError("live/external mode is not authorized")
    req = OnDemandRequest(
        topic=topic, requested_at=datetime.now(timezone.utc), request_id=request_id
    )
    return AuthorizedRequest(
        mode=mode,
        topic_sha256=sha256(req.topic.encode("utf-8")).hexdigest(),
        request_id=req.request_id,
    )


def authorize_public_probe(
    *, repository: str, actor: str, ref: str, event_name: str,
    mode: str, topic: str, request_id: str,
) -> AuthorizedRequest:
    """Separate owner-only authorization for bounded external public GETs.

    This never relaxes authorize_manual_request(), which remains OFFLINE-only.
    The live source executor has no external sends, credentials or prod storage.
    """
    if (repository != AUTHORIZED_REPOSITORY or actor != AUTHORIZED_OWNER
            or ref != "refs/heads/main" or event_name != "workflow_dispatch"):
        raise PermissionError("owner public probe context not authorized")
    if mode != "PUBLIC_SOURCE_READONLY":
        raise PermissionError("unsupported public-source probe mode")
    req = OnDemandRequest(
        topic=topic, requested_at=datetime.now(timezone.utc), request_id=request_id
    )
    return AuthorizedRequest(
        mode=mode,
        topic_sha256=sha256(req.topic.encode("utf-8")).hexdigest(),
        request_id=req.request_id,
    )
