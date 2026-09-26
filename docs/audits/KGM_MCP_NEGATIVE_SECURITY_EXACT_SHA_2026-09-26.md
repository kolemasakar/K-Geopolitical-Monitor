# KGM MCP negative security acceptance — 2026-09-26

Isolated KGM host: `kgm-e4-owner-pilot`.
Exact validated commit: `545f132fc506b66091236ca51f57c12d61723eec`.
Disposable venv: `private-plugin-gate/mcp-http-venv`.
Executed seven focused test modules including newly added `tests/test_private_mcp_gateway_security.py`.
Observed: **26 passed, 1 warning in 9.98s**, exit 0.
Warning: Starlette test client's deprecated anyio BlockingPortal alias. The pytest warning filter configuration was overridden because repository config references a Starlette warning class absent in the pinned isolated version; no tests were disabled.

New checks: denied requests do not read backend state; invalid bearer, missing bearer, invalid Origin, oversized request, denied GET, duplicate Authorization, and short-token configuration rejection.

**Security review findings requiring work before any network deployment:**
- Token is an immutable argument; external secret provisioning, rotation, revocation and token lifecycle are not implemented.
- Per-process in-memory request rate limiting is not shared across multiple processes.
- Gateway's origin policy rejects every Origin; deployment client compatibility is unverified.
- Chunked body size enforcement is implemented but dedicated multi-chunk regression tests have not been run.
- Production-grade exception handling, timeout/backpressure, audit persistence, TLS and authenticated hosted ChatGPT connectivity are not validated.
- `private_mcp_gateway_v2.py` is local-only prototype. No socket, production reader, public ingress or hosted plugin activation.

Gate: `LOCAL_MCP_SECURITY_REGRESSION_PASS / DEPLOYMENT_SECURITY_REVIEW_PENDING`.
PR #161 remains draft and unmerged. No production or paid resources modified.
