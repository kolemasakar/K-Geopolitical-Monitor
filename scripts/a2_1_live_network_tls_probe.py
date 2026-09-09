"""Credential-free external A2.1 network/TLS/exposure probe.

The probe is read-only and targets only the disposable Railway non-production
candidate. It never uses bearer/database credentials and never mutates Railway
or canonical project state.
"""

from __future__ import annotations

import http.client
import json
import socket
import ssl
from urllib.parse import urlparse


API_HOST = "kgm-preflight-api-v3-production.up.railway.app"
DB_INTERNAL_HOST = "kgm-preflight-postgres.railway.internal"
TIMEOUT_SECONDS = 15


def _https_get(path: str) -> tuple[int, dict[str, str], bytes]:
    context = ssl.create_default_context()
    connection = http.client.HTTPSConnection(
        API_HOST,
        443,
        timeout=TIMEOUT_SECONDS,
        context=context,
    )
    connection.request("GET", path, headers={"User-Agent": "kgm-a2.1-live-probe/1"})
    response = connection.getresponse()
    body = response.read()
    headers = {key.casefold(): value for key, value in response.getheaders()}
    status = response.status
    connection.close()
    return status, headers, body


def _assert_tls() -> None:
    context = ssl.create_default_context()
    with socket.create_connection((API_HOST, 443), timeout=TIMEOUT_SECONDS) as raw:
        with context.wrap_socket(raw, server_hostname=API_HOST) as tls:
            certificate = tls.getpeercert()
            if not certificate:
                raise RuntimeError("TLS peer certificate missing")
            version = tls.version()
            if not version or not version.startswith("TLS"):
                raise RuntimeError(f"unexpected TLS version: {version!r}")
            cipher = tls.cipher()
            print(f"TLS_PASS version={version} cipher={cipher[0] if cipher else 'unknown'}")


def _assert_https_health() -> None:
    status, _, body = _https_get("/health")
    if status != 200:
        raise RuntimeError(f"HTTPS /health expected 200, got {status}")
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
                f"HTTPS /health field {key!r} expected {value!r}, got {payload.get(key)!r}"
            )
    print("HTTPS_HEALTH_PASS status=200 safe_metadata_and_rls=PASS")


def _assert_http_redirect() -> None:
    connection = http.client.HTTPConnection(API_HOST, 80, timeout=TIMEOUT_SECONDS)
    connection.request("GET", "/health", headers={"User-Agent": "kgm-a2.1-live-probe/1"})
    response = connection.getresponse()
    response.read()
    status = response.status
    location = response.getheader("Location")
    connection.close()
    if status not in {301, 302, 307, 308}:
        raise RuntimeError(f"HTTP /health expected HTTPS redirect, got {status}")
    if not location:
        raise RuntimeError("HTTP redirect missing Location header")
    parsed = urlparse(location)
    if parsed.scheme.casefold() != "https" or parsed.hostname != API_HOST:
        raise RuntimeError(f"HTTP redirect target is not the expected HTTPS host: {location!r}")
    print(f"HTTP_TO_HTTPS_PASS status={status}")


def _assert_public_surface() -> None:
    docs_status, _, _ = _https_get("/docs")
    redoc_status, _, _ = _https_get("/redoc")
    protected_status, protected_headers, protected_body = _https_get("/preflight/probes")
    if docs_status != 404 or redoc_status != 404:
        raise RuntimeError(
            f"interactive docs expected disabled: /docs={docs_status}, /redoc={redoc_status}"
        )
    if protected_status != 401:
        raise RuntimeError(
            f"protected endpoint without bearer expected 401, got {protected_status}"
        )
    if protected_headers.get("www-authenticate", "").casefold() != "bearer":
        raise RuntimeError("protected endpoint missing Bearer challenge")
    lowered = protected_body.lower()
    if b"postgres" in lowered or b"railway.internal" in lowered:
        raise RuntimeError("protected error body exposed private endpoint material")
    print("PUBLIC_SURFACE_PASS docs_disabled=PASS protected_unauthenticated=401")


def _assert_private_db_dns_not_public() -> None:
    try:
        resolved = socket.getaddrinfo(DB_INTERNAL_HOST, 5432)
    except socket.gaierror:
        print("DB_PUBLIC_DNS_ABSENCE_PASS railway_internal_hostname_not_publicly_resolvable")
        return
    addresses = sorted({item[4][0] for item in resolved})
    raise RuntimeError(
        "Railway-internal PostgreSQL hostname unexpectedly resolved from public runner: "
        + ",".join(addresses)
    )


def main() -> int:
    _assert_tls()
    _assert_https_health()
    _assert_http_redirect()
    _assert_public_surface()
    _assert_private_db_dns_not_public()
    print("A2_1_EXTERNAL_NETWORK_TLS_EXPOSURE_PROBE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
