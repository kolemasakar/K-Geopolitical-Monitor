"""Credential-free live A2.2 security negative-matrix probe.

This probe is intentionally read-only. It targets only the existing disposable
Railway Phase 18 preflight candidate, uses no bearer/database credential, and
performs no canonical-data or provider mutation.
"""

from __future__ import annotations

import http.client
import json
import ssl
from urllib.parse import quote


API_HOST = "kgm-preflight-api-v3-production.up.railway.app"
TIMEOUT_SECONDS = 15
USER_AGENT = "kgm-a2.2-live-negative-matrix/1"


def _request(
    method: str,
    path: str,
    *,
    authorization: str | None = None,
    body: bytes | None = None,
) -> tuple[int, dict[str, str], bytes]:
    headers = {"User-Agent": USER_AGENT}
    if authorization is not None:
        headers["Authorization"] = authorization
    if body is not None:
        headers["Content-Type"] = "application/json"

    connection = http.client.HTTPSConnection(
        API_HOST,
        443,
        timeout=TIMEOUT_SECONDS,
        context=ssl.create_default_context(),
    )
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    payload = response.read()
    response_headers = {
        key.casefold(): value for key, value in response.getheaders()
    }
    status = response.status
    connection.close()
    return status, response_headers, payload


def _assert_safe_unauthorized(
    label: str,
    method: str,
    path: str,
    *,
    authorization: str | None = None,
    body: bytes | None = None,
) -> None:
    status, headers, payload = _request(
        method,
        path,
        authorization=authorization,
        body=body,
    )
    if status != 401:
        raise RuntimeError(f"{label}: expected 401, got {status}")
    if headers.get("www-authenticate", "").casefold() != "bearer":
        raise RuntimeError(f"{label}: missing Bearer challenge")

    decoded = json.loads(payload.decode("utf-8"))
    if decoded != {"detail": "unauthorized"}:
        raise RuntimeError(f"{label}: unsafe or unexpected unauthorized body")

    lowered = payload.casefold()
    for forbidden in (
        b"postgres",
        b"railway.internal",
        b"database_url",
        b"bearer_token",
        b"workspace_id",
        b"project_id",
        b"traceback",
    ):
        if forbidden in lowered:
            raise RuntimeError(f"{label}: response leaked private/security material")


def _assert_live_rls_evidence() -> None:
    status, _, body = _request("GET", "/health")
    if status != 200:
        raise RuntimeError(f"health expected 200, got {status}")
    payload = json.loads(body.decode("utf-8"))
    expected = {
        "status": "ok",
        "canonical": False,
        "production_live": False,
        "shared_runtime_active": False,
        "synthetic_data_only": True,
        "database_network": "railway_private",
        "rls_isolation_observed": True,
        "alternate_tenant_visible_rows": 0,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise RuntimeError(
                f"health field {key!r} expected {value!r}, got {payload.get(key)!r}"
            )
    for forbidden_key in (
        "database_url",
        "bearer_token",
        "workspace_id",
        "project_id",
    ):
        if forbidden_key in payload:
            raise RuntimeError(f"health leaked forbidden field {forbidden_key!r}")
    print("LIVE_RLS_ISOLATION_PASS alternate_tenant_visible_rows=0")


def _assert_authn_and_privilege_escalation_matrix() -> None:
    cases = (
        ("missing", None),
        ("basic", "Basic YWRtaW46YWRtaW4="),
        ("wrong", "Bearer definitely-not-the-real-token"),
        ("admin-word", "Bearer admin"),
        ("jwt-like-admin", "Bearer eyJhbGciOiJub25lIn0.eyJyb2xlIjoiYWRtaW4ifQ."),
        ("sql-like-token", "Bearer ' OR '1'='1' --"),
        ("url-like-token", "Bearer http://169.254.169.254/latest/meta-data/"),
    )
    for label, authorization in cases:
        _assert_safe_unauthorized(
            f"auth-{label}",
            "GET",
            "/preflight/probes",
            authorization=authorization,
        )
    print(f"AUTH_PRIV_ESC_NEGATIVE_MATRIX_PASS cases={len(cases)}")


def _assert_protected_mutation_gate() -> None:
    adversarial_body = json.dumps(
        {
            "probe_id": "probe-unauthorized-negative-matrix",
            "payload": (
                "' OR 1=1 -- ; DROP TABLE tenant_probe; "
                "http://169.254.169.254/latest/meta-data/"
            ),
        },
        separators=(",", ":"),
    ).encode("utf-8")
    _assert_safe_unauthorized(
        "protected-post-missing-auth",
        "POST",
        "/preflight/probe",
        body=adversarial_body,
    )
    _assert_safe_unauthorized(
        "protected-post-wrong-auth",
        "POST",
        "/preflight/probe",
        authorization="Bearer admin",
        body=adversarial_body,
    )
    _assert_safe_unauthorized(
        "rls-observation-missing-auth",
        "GET",
        "/preflight/rls-isolation",
    )
    print("PROTECTED_MUTATION_AND_RLS_GATE_PASS")


def _assert_idor_and_ssrf_surface_boundaries() -> None:
    # The candidate does not expose tenant/project selectors or a generic fetch
    # primitive. These probes verify that guessed IDOR/SSRF-style routes are not
    # accidentally reachable on the live deployment.
    nonexistent_paths = (
        "/preflight/probes/other-workspace/other-project",
        "/preflight/projects/other-project/probes",
        "/preflight/rls-isolation/other-project",
        "/preflight/fetch?url="
        + quote("http://169.254.169.254/latest/meta-data/", safe=""),
    )
    for path in nonexistent_paths:
        status, _, payload = _request("GET", path)
        if status != 404:
            raise RuntimeError(f"unexpected IDOR/SSRF-like route {path!r}: {status}")
        lowered = payload.casefold()
        if b"railway.internal" in lowered or b"postgres" in lowered:
            raise RuntimeError("404 surface leaked private endpoint material")

    tenant_query = (
        "/preflight/probes?workspace_id=other-workspace&project_id=other-project"
    )
    _assert_safe_unauthorized(
        "tenant-selector-query-still-authenticated",
        "GET",
        tenant_query,
    )
    print("IDOR_SSRF_PUBLIC_SURFACE_NEGATIVE_PASS")


def main() -> int:
    _assert_live_rls_evidence()
    _assert_authn_and_privilege_escalation_matrix()
    _assert_protected_mutation_gate()
    _assert_idor_and_ssrf_surface_boundaries()
    print("A2_2_LIVE_SECURITY_NEGATIVE_MATRIX=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
