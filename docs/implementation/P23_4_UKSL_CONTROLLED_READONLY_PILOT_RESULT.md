# P23.4 — UKSL controlled read-only pilot and identity remediation

Date: 2026-09-25
Decision: `CONTROLLED_READONLY_PILOT_PASS_WITH_MATERIAL_LIMITATIONS`
Strategic gate: `P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED` — **NOT VALIDATED**.

## Real bounded observation

The owner-approved read-only pilot retrieved the official UKSL CSV with HTTPS `206 Partial Content`, exact range `0–1,499,999`, 1,500,000 bytes, existing 2,000,000-byte transport ceiling intact. The full remote document advertised 49,927,316 bytes. The initial slice contained 1,827 fully terminated CSV data rows but only **38 distinct official Unique IDs**. Its Report Date and HTTP Last-Modified were 21 September 2026.

The pre-remediation adapter returned 100 first rows as 100 items although they shared **one** stable item ID. Rows are exploded across aliases/other fields, not distinct designations. The repaired adapter discards the incomplete trailing physical line, parses complete rows strictly, and deduplicates by mandatory official Unique ID. Offline replay from the captured official range and a second governed live bounded HTTPS acquisition both returned **38 distinct items / 38 distinct item IDs / 0 duplicate inflation**. Current targeted tests for the fix: 11 PASS before the documentation update.

## Acceptance limits and rollback

This pilot establishes **bounded collection and correct identity**, NOT comprehensive coverage. It has only a partial initial range of a much larger document. Freshness credit is unavailable: the observed report date / Last-Modified predate the 25 September pilot by several days. Production/repository source activation, deployed runtime, acquisition-limit relaxation and persistent owner operations remain unchanged. An empty enabled adapter selection is verified as the non-activating rollback.

Before a future repository activation, explicitly review the bounded full-coverage policy, enforce HTTP 206 and Content-Range in the acquisition transport (the existing simple transport currently discards response status/headers), verify freshness against governed P20.5, and revalidate activation. No unsupported 100-designation or freshness claim is allowed.

## Russian official source

Owner permits non-Ukrainian VPN egress solely for a controlled route to `https://government.ru/news/`. On the owner node the canonical HTTPS endpoint and first-party RSS-hint subdomain both timed out. Tailscale has no configured exit nodes, so VPN transport remains unconfigured. The public official-channel candidate `https://t.me/s/government_rus` returned HTTPS HEAD 200, but it is a different delivery path and must pass its own governance/onboarding gate; it gives no independence credit.

VPN proposal: dedicated trusted non-Ukraine egress for this source only, remote DNS through the tunnel, verified HTTPS to the canonical host, no host-wide default-route change, no HTTP downgrade, and no unrelated project resources without separate approval. See `docs/implementation/P23_4_GOVRU_NON_UA_VPN_READINESS_2026-09-25.md`.

P13.5/P13.6 remain sole factual-verification authority.
