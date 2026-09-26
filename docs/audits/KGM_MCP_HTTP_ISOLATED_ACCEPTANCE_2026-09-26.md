# KGM official MCP HTTP isolated acceptance — 2026-09-26

## Restored control and exact-SHA test
- Owner ran existing `/home/kgmops/.local/bin/kgm-rdc-watchdog.sh` in the KGM SSH session; RDC subsequently reported `kgm-e4-owner-pilot=online`. This verifies current connectivity, not unattended recovery from revoked credentials.
- Dedicated disposable environment: `/home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/mcp-http-venv`. Dependency check: `No broken requirements found`.
- Pinned dependencies in `tests/requirements-private-mcp.txt`; `pytest` repository warning filter references a newer Starlette warning type absent from this isolated pin. Validation therefore used `-o filterwarnings=` to override **warning configuration only**, not tests.
- Official MCP SDK's DNS rebinding defense rejected test `Host: testserver` and `Host: 127.0.0.1` (HTTP 421). Corrected TestClient base URL to `http://127.0.0.1:8000`, matching the SDK's configured loopback host and port. Security protection remained enabled.
- Exact validated commit: `a68bfaa7f03b74c41fa3d12587530e8018e51e6e`.
- Executed in isolated checkout:
```bash
PYTHONPATH=src /home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/mcp-http-venv/bin/python -m pytest -q -o filterwarnings= tests/test_private_mcp_http.py tests/test_private_mcp_server.py tests/test_private_mcp_adapter.py tests/test_private_plugin_status.py tests/test_backend_action_api.py
```
- Observed: **21 passed, 1 warning in 10.08s; exit 0**. Warning: deprecated `anyio.abc.BlockingPortal` alias in isolated Starlette test client.

## Security and deployment interpretation
- In-memory official MCP SDK handshake/discovery/call and localhost-only ASGI Streamable HTTP handshake/discovery/call are validated.
- The original custom MCP-style adapter's bearer checks, rate limits, request bounds and allowlist were separately tested. **The official FastMCP HTTP app is not yet protected by that adapter's authentication/rate limits**. Never imply the separate checks compose into an authenticated production MCP gateway.
- No live socket listener, TLS, externally reachable endpoint, production reader, owner credential, remote ChatGPT connector or external Plugin connection was tested.
- No production service modification, ingress, Tailscale Funnel, public publication or PR merge.

Gate: `OFFICIAL_MCP_PROTOCOL_AND_ASGI_HTTP_PASS / INTEGRATED_AUTH_GATEWAY_PENDING / HOSTED_CHATGPT_REACHABILITY_UNKNOWN / NO_DEPLOYMENT`.
