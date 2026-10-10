# Project checkpoint — 2026-10-10 — Independent research readiness v3

## Gate

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS`

Validated implementation SHA:
`322c55f8f47f62aca19fd563b3d7eb73538b1b52`

Current synchronized branch state includes:
- policy-bound required source portfolios;
- adapter source-id binding;
- immutable durable observation staging;
- crash/restart reuse without provider re-query;
- canonical Consilium official political/diplomatic source;
- mixed-domain live execution;
- immutable first-seen evidence archive;
- no-network `HISTORICAL_AS_OF` replay;
- verification/corroboration stack from earlier owner-pilot milestones.

## Historical replay proof

Fresh live CURRENT source portfolio:
- Consilium 10 / OBSERVED
- GDACS 10 / OBSERVED
- GDELT 1 / DEGRADED under cooldown
- GFZ 10 / OBSERVED
- USGS 10 / OBSERVED
- total observations: 41
- stage SHA:
  `ec9c2c4a28df332b52e6d265b780e21a7474b1b778dee3c68aa36f6be2a62743`

Archive-backed historical replay:
- provider calls: 0;
- observations: 41;
- same source snapshot: true;
- max available_at: `2026-10-10T08:59:42Z`;
- cutoff: `2026-10-10T08:59:44Z`;
- historical stage SHA:
  `377811baccb993660879d6f75ee6b282f1cb8916713556025454e2e9733d696f`;
- historical result:
  `result-7e93b41aa7c742826a5be357`;
- recovery pending: empty.

## Regression

Selected isolated exchange/research regression:
`249 passed in 4.65s`

## Remaining P1

- generic non-earthquake identity families;
- typed PARTIAL reason semantics;
- canonical evidence fingerprint deduplication.

## Boundaries

This checkpoint does not authorize production/live daemon activation, persistent unattended scheduling, Sentinel or K-Trader integration, paid provider fallback, shared runtime, public Plugin publication, or HP-OMEN use.

Next:
`P1_RESEARCH_QUALITY_HARDENING`
