# KGM O1 P4 — Source transport qualification (2026-10-25)

Status: **ISOLATED_POLICY_IMPLEMENTED / NO_LIVE_COLLECTION / PRODUCTION_NO_GO**.

## Audited existing adapters

- GDELT DOC 2.0: `GdeltDoc2Adapter`, HTTPS `api.gdeltproject.org/api/v2/doc/doc`. It is a discovery feed; returned publisher URL is third-party metadata, not an independent original-source verification. All individual articles still require evidence review. The adapter's `source_id` is `gdelt-doc-2`.
- EU Council: `ConsiliumRssAdapter`, HTTPS `www.consilium.europa.eu/en/rss/pressreleases.ashx`, primary official institutional RSS. Source ID `consilium-press-releases`.
- GDACS: **not present in the deployed disk `unattended_runner.build_unattended_service` adapter list**; no approved production GDACS adapter established. Do not claim three-source capability on the basis of two adapters.

The loaded in-memory service identity is still NOT ATTESTED. No source activation or endpoint access has been performed.

## New transport defense-in-depth

`src/kgeopolitical_monitor/on_demand_source_policy.py` adds a bounded HTTPS fetch transport with exact domain-and-path allowlisting (only GDELT and Consilium), refusal of redirects, opt-out from inherited proxy environment, no credential headers, fixed per-request timeout, maximum response bytes and total request budget. The transport is **not plugged into any live request handler** and is not initialized automatically.

Caveats: Python in-process policy is NOT an external egress firewall, host DNS pinning or prevention of malicious injected adapters. A hard process-wide deadline / OS memory budget and isolated network policy remain required before any real user-requested live collection. An allowlisted GDELT endpoint is not independent verification of each publisher article. There is no asserted GDACS availability or proof of live freshness from offline tests.

## Next acceptance gates

1. Test exact endpoint/redirect/size/budget behavior in CI without making network calls.
2. Qualify source idempotence, independence, evidence origin and item-level freshness in offline fixtures.
3. Design process-level egress/CPU/time boundaries and a user authorization surface, with NO_SEND preserved.
4. Only with separate owner release gate run one approved live user request and return an auditable report.
5. Keep both persisted watches disabled and preserve Oct17 snapshot.

FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
