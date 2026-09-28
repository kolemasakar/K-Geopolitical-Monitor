# KGM isolated owner-only MCP-style adapter acceptance — 2026-09-26

## Implementation
- `src/kgeopolitical_monitor/private_mcp_adapter.py` adds a standalone FastAPI factory; no server is launched or network listener configured.
- One allowlisted `kgm_get_status` operation; JSON-RPC-style `tools/list` and `tools/call`. This is a **protocol prototype**, not a claim of full MCP Streamable HTTP/initialization/session negotiation compliance.
- Dedicated bearer token (>=32 characters), constant-time comparison, request/response bounds, in-memory per-process 30-request/60-second limit, fixed-code audit callback, generic errors, OpenAPI/docs disabled.
- No arbitrary SQL, shell, filesystem, RDC operations, or cross-project access exposed. Reader supplied by caller; production read-only identity/transport not provisioned.

## Exact-SHA isolated tests
- KGM VM: `kgm-e4-owner-pilot`, owner user `kgmops`.
- Isolated repo: `/home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/repo`.
- Checked out detached exact commit `ab9c0a2b8eca800df4983c1007ba504f2c8b2898`.
- Command:
```bash
PYTHONPATH=src /home/kgmops/validation/kgeopolitical-monitor/p23-4/venv/bin/python -m pytest -q tests/test_private_mcp_adapter.py tests/test_private_plugin_status.py tests/test_backend_action_api.py
```
- Observed: `19 passed in 9.53s`, exit code 0.

## Remaining mandatory gates
1. Protocol compatibility: use supported MCP library/transport, initialize negotiation, tool discovery/call contract, required headers and error semantics; current prototype is **not yet production MCP compliant**.
2. Threat-model completion: trusted proxy/TLS, credential provisioning/rotation/revocation, audit sink, shared/distributed rate limiting as appropriate, generic failures, dedicated least-privileged runtime, upstream query contention measurements if needed.
3. Hosted ChatGPT Plugin reachability and authentication are **unverified**; private Tailscale route alone does not prove access. Any internet-facing ingress needs separate owner approval.
4. Keep PR draft, no merge, public sharing, production deployment or Funnel. No changes to existing `kgm-monitor.service`.

Gate: `ISOLATED_ADAPTER_TESTS_PASS / MCP_PROTOCOL_INCOMPLETE / PRIVATE_TRANSPORT_UNVERIFIED / NO_DEPLOYMENT`.
