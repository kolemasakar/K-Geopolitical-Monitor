# KGM owner-only Plugin secure transport audit — 2026-09-25

Status: **TRANSPORT DESIGN GATE / NO DEPLOYMENT**. Private status adapter and integration tests passed separately; no live plugin connectivity claimed.

## Verified live facts
- KGM-only RDC host `kgm-e4-owner-pilot` online for this inspection. `kgm-monitor.service` reported `active`. This is a point-in-time service check, **not** acquisition continuity verification.
- `tailscale` installed, `BackendState=Running`, `Self.Online=true`, `tailscale0` exists. This establishes owner-network availability on the VM, **not** that ChatGPT's Plugin runtime can route into the tailnet.
- No listener found on checked TCP ports 80, 443, 8000 or 9000. No Caddy/cloudflared binary found on PATH. No production API was started.
- Isolated TestClient against exact source checkout `071af158b3ea316e498bf250a02d7bf82ffb975b`:
  - `GET /health` unauthenticated => HTTP 200.
  - `GET /openapi.json` unauthenticated => HTTP 200; OpenAPI advertises HTTPBearer.
  - `GET /v1/private-plugin/status` without token => HTTP 401; wrong token => HTTP 401.
- Separate exact-SHA integration suite already passed: `14 passed in 9.96s`.

## Threat model and acceptance
1. **Transport:** ChatGPT Plugin execution network reachability is **UNVERIFIED**. Do not assume Tailscale-only addresses can be reached from the Plugin. Do not configure public Tailscale Funnel, a public tunnel, public load balancer or public ingress without separate explicit owner authorization.
2. **Authentication:** existing app uses single static owner Bearer token and constant-time comparison. This is an app-level boundary, not complete private transport, owner identity federation, rate limiting, token lifecycle, or audit logging. Never reuse RDC credentials, Tailscale node keys, GitHub tokens or another project's secrets.
3. **Information exposure:** `/health` and `/openapi.json` currently have no auth. If external routing is eventually approved, restrict or remove their unauthenticated exposure at the adapter/gateway. Public availability of an OpenAPI schema is not itself proof of a secret leak, but is unnecessary for owner-only scope.
4. **Least privilege:** launch future adapter as dedicated non-privileged identity, project-local read-only state, explicit endpoint allowlist, no arbitrary shell/SQL, no canonical DB mount to Plugin runtime. Keep acquisition service independent.
5. **Operational security:** bounded response and rate limits, secret-free structured audit, generic error handling and denial tests must pass before connectivity acceptance. SQL upstream bounded optimization remains owner-deferred until public/multi-user stage unless measured contention occurs.

## Proposed FREE_ONLY proof sequence
- **A (local, no ingress):** isolated FastAPI test harness and negative-path security tests on exact SHA. Done for existing auth/read-only checks; gateway-specific protections remain to implement.
- **B (network feasibility):** inspect the installed Plugin/connector's supported outbound transport/auth without granting credentials or deploying a server. Decide whether a private supported path exists. If not, report blocker and seek explicit approval for any restricted internet-facing gateway design.
- **C (only after separate approval):** provision dedicated adapter identity and short-scope credentials, configure narrow route, test deny-by-default, rotate/revoke, bound response and logs; then owner-only Plugin read test.
- No merge, production deployment, public publication or sharing is authorized by this audit.

**Gate result:** `LOCAL_AUTH_PASS / TAILSCALE_HOST_ONLINE / PLUGIN_NETWORK_REACHABILITY_UNKNOWN / PRIVATE_TRANSPORT_NOT_APPROVED`.
