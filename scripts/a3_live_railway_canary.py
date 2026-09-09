#!/usr/bin/env python3
"""Credential-free A3 live Railway non-canonical canary."""

from __future__ import annotations

import json
import os
import ssl
import urllib.request

EXPECTED_FALSE = ("canonical", "production_live", "shared_runtime_active")
EXPECTED_TRUE = ("synthetic_data_only", "rls_isolation_observed")


def main() -> int:
    url = os.environ.get(
        "KGM_A3_CANARY_URL",
        "https://kgm-preflight-api-v3-production.up.railway.app/health",
    )
    request = urllib.request.Request(url, headers={"User-Agent": "kgm-a3-canary/1"})
    with urllib.request.urlopen(request, timeout=30, context=ssl.create_default_context()) as response:
        if response.status != 200:
            raise RuntimeError(f"health status={response.status}")
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("status") != "ok":
        raise RuntimeError("health status is not ok")
    for field in EXPECTED_FALSE:
        if payload.get(field) is not False:
            raise RuntimeError(f"{field} must remain false")
    for field in EXPECTED_TRUE:
        if payload.get(field) is not True:
            raise RuntimeError(f"{field} must remain true")
    if payload.get("alternate_tenant_visible_rows") != 0:
        raise RuntimeError("alternate tenant rows must remain zero")
    if payload.get("database_network") != "railway_private":
        raise RuntimeError("database network marker is not railway_private")

    print("A3_LIVE_CANARY_HEALTH=PASS")
    print("A3_LIVE_CANARY_NONCANONICAL=PASS")
    print("A3_LIVE_CANARY_RLS_STARTUP_EVIDENCE=PASS")
    print("A3_LIVE_RAILWAY_DATA_PLANE_RECONCILIATION=NOT_EVIDENCED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
