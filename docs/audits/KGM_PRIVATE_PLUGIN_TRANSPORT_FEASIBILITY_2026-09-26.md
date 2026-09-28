# KGM private Plugin transport feasibility decision gate — 2026-09-26

## Current verified host/network state
- KGM-only VM online via RDC; Tailscale is Running/Online, `kgm-monitor.service` active.
- Read-only commands `tailscale serve status` and `tailscale funnel status` both returned `No serve config`.
- `ss -lnt` showed SSH, Tailscale's internal listeners and local DNS only; no KGM API listener. No tunnel or ingress was created.
- Isolated checkout of exact integration-tested SHA `071af158b3ea316e498bf250a02d7bf82ffb975b` exists; 14/14 focused tests passed previously.

## Supported transport distinction
- Tailscale Serve is tailnet-only HTTPS reverse proxy. This may be suitable for owner-admin browser tests but does not establish that hosted ChatGPT Plugin tools can access a tailnet IP/DNS.
- Tailscale Funnel provides an internet-reachable HTTPS URL. A private personal Plugin does not make Funnel's URL private. Do not enable it or expose the current FastAPI app as-is.
- Native plugin tool integrations require a supported connection/auth mechanism. Plugin Creator's local archive import and app mappings alone do not provide an inbound connection to KGM; check supported custom MCP integration, credential lifecycle and hosted runtime network reachability before selection.
- Existing static Bearer token is suitable for local negative-path tests but not by itself a completed production owner identity, rate limit or token rotation design.

## FREE_ONLY no-ingress next engineering slice
1. Keep current private status route as tested. Add a **separate isolated narrow adapter** with a single status tool/route, explicit no shell/SQL passthrough, generic errors, audit metadata without secrets, request bounds and denial tests. Do not bind it to public interfaces or start it on production.
2. Inspect currently supported custom MCP server/plugin connector configuration and outbound auth; prove feasibility in a disposable environment without providing secrets. If private tailnet-only connectivity cannot be supported, require owner approval for any internet-facing authenticated gateway.
3. Before any ingress: dedicated nonprivileged identity, read-only access to project-local KGM state, per-request owner authorization, TLS, rate limit, secret-free audit, negative tests, credential revocation, and no unauthenticated health/schema exposure on gateway.
4. Do not share/publish Plugin, merge PR, enable Funnel, add paid resources or modify monitoring service at this gate.

Sources reviewed: https://tailscale.com/docs/features/tailscale-serve and https://tailscale.com/docs/features/tailscale-funnel .
Gate: `HOST_TAILNET_READY / NO_SERVE_CONFIG / NO_FUNNEL_CONFIG / HOSTED_PLUGIN_REACHABILITY_UNVERIFIED / INGRESS_REQUIRES_APPROVAL`.
