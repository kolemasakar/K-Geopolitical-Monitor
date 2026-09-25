# P23.4 — Government.ru non-Ukraine VPN route readiness

Date: 2026-09-25
State: `OWNER_ALLOWED_VPN / EGRESS_NOT_CONFIGURED / SOURCE_NOT_ACTIVE`

## Observed network access on kgm-e4-owner-pilot

- `https://government.ru/news/`: HTTPS/443 connect timeout in a fresh direct (no-proxy) HEAD check.
- `https://services.government.ru/en/subscribe/`: HTTPS/443 connect timeout in a fresh direct (no-proxy) HEAD check. The first-party page publicly describes news RSS subscriptions, but its runtime endpoint is not usable from this owner node.
- `https://t.me/s/government_rus`: public HTTPS HEAD 200 from the owner node. The channel describes itself as official, but it is a distinct platform and NOT an authorized replacement for the canonical source.
- Tailscale is present but `tailscale exit-node list` reports no exit nodes. No foreign VPN endpoint is currently available for this path.

Public reference URLs:
- `https://services.government.ru/en/subscribe/`
- `https://telegram.me/government_rus`

## Permitted source-scoped transport design, NOT yet activated

1. Obtain an explicitly authorized, trusted non-Ukraine VPN exit supplied/owned by the project owner. Do not silently use HP-OMEN, krc-cobalt or other project-owned infrastructure, unknown free proxy relays, paid providers or credentials.
2. Prefer per-source tunnel/isolated retrieval. A supported authenticated VPN plus source-bound connector must route DNS through the same exit to avoid leaks; do not change the owner VM's default route or unrelated collectors.
3. Keep HTTPS certificate validation and canonical hostname; fail closed on HTTPS timeout, redirects outside authorized first-party hosts, or tunnel absence. No HTTP/80 fallback.
4. Run a bounded read-only HEAD/GET and parser validation using the isolated source-specific transport only; document actual external exit region without collecting or exposing unrelated sensitive network metadata.
5. Full P20.5 readiness and separate source activation gate still apply. The alternative official-channel candidate, if considered, also requires its own rights, provenance, freshness and governance review, and cannot earn automatic factual-independence credit.

Current next dependency: owner-supplied existing non-Ukrainian VPN exit details or explicit authorization for an appropriate dedicated owned egress resource. Never paste private keys, passwords or VPN credentials into chat.
