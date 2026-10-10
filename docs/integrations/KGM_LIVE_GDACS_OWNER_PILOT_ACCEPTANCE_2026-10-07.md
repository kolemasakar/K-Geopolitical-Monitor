# KGM live GDACS owner-pilot acceptance — 2026-10-07

## Decision

**LIVE_GDACS_OWNER_PILOT_E2E = PASS**

Exact code SHA: `155c8f06c5457a0988ad91c80a7ebee6d541d797`.

## Live execution

A real public/free/read-only GDACS query was executed from the isolated KGM owner VM into a temporary owner-pilot spool only. No production path, Sentinel, K-Trader transport, paid provider, daemon or unattended scheduler was used.

Canonical path proven:

`CURRENT request → ACCEPTED → PROCESSING → live GDACS → normalized source observations → typed immutable result → COMPLETE → restart reconciliation`

Observed result:
- research_status: COMPLETE
- coverage: COMPLETE
- source_health: HEALTHY
- records: 5
- result_id: `result-7f48780e2892c2926b35f0a2`
- restart reconciliation returned the same result_id
- recovery pending after restart: empty

Live evidence included GDACS flood events for Spain and France and earthquake events for Russia, South of Fiji Islands, and Papua New Guinea. Each record retained GDACS source identity, public HTTPS provenance, published timestamp and KGM-observed availability timestamp.

## Validation

- Targeted worker/source resilience suite after batch support: 20/20 PASS.
- Selected exchange/research regression: 178/178 PASS in 2.59 s.
- Real source batch is bounded to the request max_results and the worker rejects more than 100 observations.

## Scope

This proves a real external owner-pilot research cycle. It does not declare `KGM_INDEPENDENT_RESEARCH_READY` and does not authorize production activation or downstream K-Trader/Sentinel integration.
