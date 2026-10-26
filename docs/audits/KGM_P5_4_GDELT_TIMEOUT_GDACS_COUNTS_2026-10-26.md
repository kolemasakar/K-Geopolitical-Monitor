# KGM P5.4 — bounded GDELT timeout and GDACS source-level counts

Date: 2026-10-26. Proposal: one-off owner-authorized validation after CI.

## Evidence-driven adjustment

Previous owner run [40267647566](https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/40267647566) showed:
- GDACS: successful RSS retrieval, zero query matches, feed-count unobserved.
- Consilium: 20 RSS items, zero query matches.
- GDELT: network timeout after existing 7-second request budget.

This patch adds a separately bounded 12-second timeout **only** for the fixed GDELT API endpoint. GDACS/Consilium retain 7 seconds; no automatic retries, no wider endpoint allowlist, and no changed TLS requirements. Policy validation rejects a dedicated GDELT timeout above 15 seconds. The overall one-shot workflow already has a 75-second wall timeout.

The GDACS response is inspected *after* bounded transport returns. Aggregate total RSS item count and keyword matches are recorded, alongside the existing Consilium counters. Raw source content is neither printed nor persisted beyond ephemeral collection SQLite. Counts are diagnostic and cannot by themselves prove event relevance, completeness or truth.

## Critic and evidence criteria

PASS requires CI validation of per-source timeouts, error classification and pre/post-filter counters, then separate manual owner dispatch. Code CI does not prove that the GDELT API responds within 12 seconds or that live source items exist.

If the next live result is still a GDELT timeout, keep PARTIAL and evaluate provider-side availability/limits separately; do not retry in a loop. If a feed has entries but zero matches, do not claim source emptiness or that the geopolitical event does not exist. If any items are returned, P5.5 still requires freshness, provenance, independence and an actual human-readable brief with Critic.

Production server, persistent watches, external sending and scheduled source polls remain unchanged.

Gate: P5_4_BOUNDED_GDELT_TIMEOUT_AND_GDACS_COUNTS_CI_PENDING / P5_5_REPORT_BLOCKED / PRODUCTION_NO_GO.

Policy: FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD.
