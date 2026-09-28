# KGM private personal Plugin v0.1 package contract

Status: PACKAGE SPECIFICATION ONLY. Do not generate a plugin archive with invented network endpoint, create an unusable live connector, or claim ChatGPT integration before transport acceptance.

## Scope
- Personal USER scope, PRIVATE discoverability; no public publication, sharing, marketplace listing or cross-project apps.
- First capability: `kgm_get_status` only. Return sanitized state; preserve `NOT_MEASURED`, `NOT_VERIFIED`, stale and unknown rather than inferring health.
- Future tools `kgm_get_brief`, `kgm_get_events`, `kgm_get_evidence` are explicitly deferred pending real read-model mapping and separate validation.
- Never grant shell, filesystem, SQL, sudo, restarts, deployment or source activation.

## Connection
- Official MCP Streamable HTTP interface, not the older JSON-RPC-like prototype.
- Dedicated KGM-only owner credentials; never RDC, GitHub, Tailscale admin or other project tokens.
- No localhost or Tailscale URL in a hosted manifest unless actual product support for that private route is independently verified.
- Do not place tokens in plugin package, GitHub, logs, prompts or downloadable audit artifacts.
- No automatic public HTTPS ingress, Funnel or paid relay.

## Release acceptance checklist
- Exact commit and local 29/29 baseline retained; expanded tests must run against final candidate.
- Official hosted connector protocol and authentication supported by current product documentation.
- A disposable synthetic read-only endpoint reachable through an approved private transport.
- Successful authenticated hosted initialize/list/call and negative unauthenticated check.
- Confirm owner-only plugin permissions, stable secret lifecycle, fixed audit event codes, resource isolation, no production writes, and free-tier quotas.
- Archive schema validation using the current Plugin Creator contract before PRIVATE personal creation.
- Owner approval for any new network listener, secrets or production runtime modification.

## Present gate
`PACKAGE_SPEC_READY / REMOTE_TRANSPORT_UNKNOWN / PRIVATE_PLUGIN_NOT_CREATED`.
