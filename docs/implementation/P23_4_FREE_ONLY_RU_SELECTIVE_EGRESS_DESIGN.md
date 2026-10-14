# P23.4 — Free-only selective .ru egress design

Status: DESIGN ONLY / NO DEPLOYMENT / NO SOURCE ACTIVATION
Owner authorization: separate non-UA free-only VPN egress for the entire DNS .ru zone, superseding government.ru-only scope.
Baseline main: 1d6873e85fb5cb5327a9e8193e5090c815affa38; ROADMAP v4.66.

## Architecture
- Provision a dedicated, isolated non-UA VM only if genuinely free ongoing capacity is verified in the provider's eligible home region and quota. No trials, paid fallback, or new billable resources.
- Connect KGM host and dedicated egress VM through a private Tailscale tunnel (or equivalent free self-hosted WireGuard). Prefer a narrowly scoped authenticated HTTP CONNECT proxy reachable only via the private tunnel, rather than a global OS exit node.
- Route all approved KGM HTTP(S) fetches whose URL host is exactly ru or ends with .ru through the private proxy. Matching must normalize case, IDNA, and trailing dot, and reject malformed/untrusted hostnames. Do not mistake .ru suffix on other TLDs for a match.
- Proxy must resolve destination DNS remotely for .ru; forbid direct local .ru DNS fallback. Keep other domains on existing direct routes. Domain-based HTTP CONNECT is preferable to brittle IP routes, given shared CDNs and changing IPs.
- Fail closed: unavailable proxy, DNS failure or tunnel loss means .ru requests fail without direct fallback. No global routing changes. Protect against redirects from .ru to non-.ru and vice versa by re-evaluating each request target under policy; log redirects without expanding authorization to unrelated sources.
- Enforce outbound proxy destination policy (only .ru hosts and explicitly reviewed supporting endpoints if separately approved); prevent private IP, loopback, metadata-service, link-local or internal-network access and DNS rebinding. Restrict tunnel identity, ports and firewall to KGM service only; no public proxy listener.
- Use existing KGM project-local logs/storage only, with secrets outside repository. Preserve provenance, truth-neutral source health, and all owner activation gates. VPN routing authorization does not activate any new source.

## Acceptance before deployment
1. Verify no-cost eligible capacity, foreign region, account constraints, and no billable network/egress exposure. Stop if free-only cannot be proven.
2. Record threat model and explicit routing rules. Add tests for apex .ru, subdomains, uppercase, trailing dots, IDNs, lookalike domains, redirects, DNS leaks, IPv4/IPv6, private-IP/metadata SSRF and proxy outage.
3. Validate .ru egress public IP from foreign node, HTTPS certificate validation, TLS SNI, DNS via remote proxy, non-.ru unchanged direct route, and fail-closed under outage.
4. Conduct bounded read-only fetch for government.ru and other separately authorized .ru candidates; do not infer content truth or activate sources from reachability.
5. Produce exact-SHA ARM64 tests and operational evidence, owner review before production mutation, and separate documentation/state-sync PR for verified results.

Constraints: HP-OMEN out of scope; existing owner-only runtime unchanged; PROJECT_LOCAL_ONLY; GitHub Actions quota contingency through 2026-10-01. No deployment or source activation in this design PR.
