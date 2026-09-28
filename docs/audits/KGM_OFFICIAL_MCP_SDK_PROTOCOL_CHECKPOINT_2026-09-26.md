# Official MCP SDK protocol checkpoint — 2026-09-26

- Exact source commit: `7337a709e7df3f7cac30a54421b8ae9a4a2da97f` on draft PR #161.
- Added `src/kgeopolitical_monitor/private_mcp_server.py`: official `mcp==1.30.0` FastMCP factory, stateless JSON response, localhost configuration, max request body 4096, one read-only `kgm_get_status` tool. This factory does not start a listener or supply a production reader.
- Added `tests/test_private_mcp_server.py`: official SDK in-memory ClientSession handshake, tools/list, tools/call, and unknown tool rejection.
- KGM VM isolated venv `/home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/mcp-venv` installed `mcp==1.30.0`; isolated exact-SHA test `1 passed in 0.51s` (exit 0).
- Existing 19/19 earlier adapter/status/API tests passed at previous exact SHA `ab9c0a2b8eca800df4983c1007ba504f2c8b2898`. **Combined test suite at new exact SHA NOT YET PASS**: isolated SDK environment initially lacked FastAPI; after installing FastAPI/httpx, newly resolved Starlette test client raised a missing `httpx2` and a deprecation warning during collection. An attempt to add the compatibility package was blocked by tool security. Do not claim 20/20.
- **Protocol caveat:** in-memory official SDK negotiation verified. Streamable HTTP localhost handshake, gateway bearer enforcement, header/origin protection, token lifecycle and actual ChatGPT Plugin reachability are NOT YET VALIDATED. The new FastMCP factory has no authentication by itself and MUST NOT be exposed or deployed.
- No production modification, public ingress, Tailscale Funnel, paid services, PR merge or plugin publication.
- Next: pin compatible isolated dependencies and run combined exact-SHA suite, then localhost-only Streamable HTTP tests behind an authenticated gateway. Require separate owner authorization for any internet-facing gateway.
