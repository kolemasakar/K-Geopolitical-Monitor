# Checkpoint — free dedicated non-Ukraine egress design

Date: 2026-09-25
State: `DESIGN_PREPARED / NEW_NODE_NOT_PROVISIONED / COST_PREFLIGHT_REQUIRED`
Canonical baseline: `1d6873e85fb5cb5327a9e8193e5090c815affa38`.

Scope:
- KGM-exclusive non-Ukraine free OCI VM proposal; verify free-tier capacity per tenancy/home region.
- Prefer Always Free E2.1.Micro (50 GB boot) if capacity exists; alternative A1.Flex 1 OCPU / 3–6 GB if free quota permits.
- Tailscale private mesh plus source-specific, Tailscale-bound authenticated-by-mesh HTTPS CONNECT egress restricted by KGM source address and government.ru host/443.
- No ordinary Tailscale global exit node on existing owner VM and no public open proxy.
- No existing or other project VM reuse; no HP-OMEN; no paid trial-only services or unknown public proxy.
- OCI resources created: **zero**.
- VPN routes installed/changed: **zero**.
- Blocked/new source activations: **zero**.
- Persistent owner operation and production/live remain inactive.
- Current project position remains P23.3 validated; next strategic gate remains P23.4 expansion.

Design: `docs/implementation/P23_4_GOVRU_DEDICATED_FREE_EGRESS_DESIGN_2026-09-25.md`.
Missing prerequisite: owner-confirmed OCI tenancy home region + remaining free compute/block/storage capacity, then explicit approval to provision exactly one eligible new VM.
