# KGM private MCP stream/token security checkpoint — 2026-09-26

- Exact validated SHA: `f8b823c5ae499059e16d0f266e3ba371513e8de7`.
- KGM VM isolated checkout, disposable `mcp-http-venv`.
- Eight focused test modules, including `tests/test_private_mcp_gateway_stream.py`.
- **29 passed, 1 warning in 10.17s; exit 0**.
- Added checks: oversized multipart ASGI request with no Content-Length is rejected before backend access; old token rejected by a newly configured gateway; duplicate raw ASGI Authorization headers rejected.
- Warning: pinned Starlette test client uses deprecated anyio BlockingPortal alias. Test warning filter override addresses an incompatible repo warning category; no tests disabled.
- **Limitations:** token replacement in a new gateway is not live token revocation/rotation; gateway still has immutable in-memory owner token. Hosted ChatGPT Plugin private reachability, TLS, secret provisioning, persistent audit, timeouts, and production ingress remain unverified. No public transport or paid resources.
- PR #161 remains draft. No merge, production deploy, plugin publication or production reader.
