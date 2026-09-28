# KGM owner-only Plugin: transport decision gate — 2026-09-26

Status: DESIGN / NO NETWORK DEPLOYMENT / FREE_ONLY. This document does not authorize opening an ingress.

## Verified local capability
- Official MCP SDK in-memory and local ASGI Streamable HTTP tests passed.
- Integrated bearer/Origin/body/rate controls passed 29 focused tests at exact SHA `f8b823c5ae499059e16d0f266e3ba371513e8de7`.
- No production listener, hosted ChatGPT-to-tailnet route, TLS certificate, remote owner identity verification or persistent audit integration has been validated.

## Reachability boundary
- PRIVATE plugin discoverability controls *who can install or see the plugin*, not which network routes hosted ChatGPT can reach.
- Owner Tailscale/SSH/RDC access to the VM is not evidence that a hosted ChatGPT connector can reach the private tailnet address.
- Do not put RDC bearer/device tokens or tailnet credentials in a plugin manifest.
- A local MCP ASGI test with `127.0.0.1:8000` does not prove remote access. Never advertise this as a plugin endpoint.
- A public DNS name with TLS, even when authenticated, is still internet-reachable ingress and requires a separate explicit owner approval. Tailscale Funnel is not a private-only substitute.

## Options requiring capability verification (not ranked)
- Supported hosted connector with native private-network connectivity: require authoritative documentation and a successful *non-production* handshake from the actual hosted connector to a disposable authenticated KGM test endpoint. Do not assume support.
- Owner-operated outbound-only relay: only if the connector product supports the specific protocol and server-side identity model, with free-tier quotas and independently audited relay isolation. No third-party paid relay.
- Public HTTPS endpoint with strict bearer/OAuth and allowlist: explicitly out of current scope without a separate owner ingress decision; do not auto-select.
- Local-only CLI/SSH access: valid for owner development and acceptance tests, **not** proof of ChatGPT hosted Plugin functionality.

## Required acceptance sequence
1. Confirm product-supported connector transport, authentication and whether the private Plugin can reference it. Record authoritative evidence and free-tier costs.
2. If private outbound-only transport exists, design a dedicated non-production sandbox using KGM-only credentials and synthetic status data. Obtain owner approval before any network or credential changes.
3. Prove connector handshake, authenticated `kgm_get_status` call, deny-without-token, source redaction and audit persistence on the actual connector path.
4. Review token provisioning/rotation/revocation, process restarts, Origin behavior, proxy header handling, per-process rate limits, timeouts and TLS trust.
5. Only then create/activate a PRIVATE USER Plugin with `kgm_get_status` alone. No publication, sharing, broad data access or production listener until separate approval.

## Current blocker
KGM RDC may be intermittently offline; status of RDC is not evidence of KGM service health. No periodic polling or unrelated machine fallback. The isolated tests already passed; transport product capability and actual hosted connectivity remain unverified.
