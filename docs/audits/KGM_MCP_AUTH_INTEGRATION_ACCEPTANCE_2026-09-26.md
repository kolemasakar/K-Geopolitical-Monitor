# KGM integrated authenticated MCP gateway acceptance — 2026-09-26

## Exact-SHA isolated result
- Validation host: KGM-owned `kgm-e4-owner-pilot`; disposable checkout `/home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/repo`.
- Exact tested commit: `533946b77547ce4b8f59b7b249bad8d8224ee96b`.
- Command: `PYTHONPATH=src .../mcp-http-venv/bin/python -m pytest -q -o filterwarnings= tests/test_private_mcp_gateway_integrated.py tests/test_private_mcp_http.py tests/test_private_mcp_server.py tests/test_private_mcp_adapter.py tests/test_private_plugin_status.py tests/test_backend_action_api.py`.
- Result: **23 passed, 1 warning in 10.00s; exit 0**. Warning is the Starlette test client's deprecated anyio BlockingPortal alias.
- The warning override is required because repository pytest warning configuration references a Starlette warning class absent from the deliberately pinned isolated test version. It overrides warning configuration only, not test outcomes.

## Integrated gateway
- `private_mcp_gateway_v2.py` wraps official FastMCP Streamable HTTP ASGI app with dedicated bearer token, origin denial, bounded pre-forward request buffering (including absent Content-Length), per-process rate limit, fixed-code audit callback and restricted /mcp POST route.
- The official SDK's own DNS rebinding protection remains active. No production reader or listener is created.
- The preceding `private_mcp_gateway.py` is an **obsolete draft** with a body-overflow response handling defect and must be removed before merge or packaging. Do not import or deploy it.
- Existing custom MCP-style adapter `private_mcp_adapter.py` is a separately tested prototype, not a substitute for the official SDK gateway.

## Remaining gates
1. Remove obsolete gateway draft and rerun exact-SHA suite on cleanup commit.
2. Additional security tests: chunked oversized body, duplicate Authorization, absent/invalid bearer, upstream exceptions, audit behavior, and local-only socket if deployment packaging is pursued.
3. Dedicated owner token provisioning/rotation, trusted HTTPS transport, persistent audit sink, actual private hosted-ChatGPT reachability, and credential-independent operation remain unverified.
4. PR #161 remains draft; no merge, production deployment, public ingress, Funnel, paid resource, or plugin publication authorized.

Gate: `INTEGRATED_LOCAL_ASGI_PASS / CLEANUP_AND_HARDENING_PENDING / TRANSPORT_UNVERIFIED / NO_DEPLOYMENT`.
