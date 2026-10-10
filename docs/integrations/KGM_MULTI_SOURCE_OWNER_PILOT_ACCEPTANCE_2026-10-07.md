# KGM multi-source owner-pilot acceptance — 2026-10-07

## Decision

**MULTI_SOURCE_OWNER_PILOT_DEDUP_DISAGREEMENT_MIXED_STATUS = PASS**

Exact validated code SHA: `93701e9edc0dd5624ab7241e854908cb04700e61`.

This acceptance remains owner-pilot only. It does not declare `KGM_INDEPENDENT_RESEARCH_READY` and does not authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Sources

1. **GDACS** — public/free/read-only official disaster event source.
2. **GDELT DOC 2.0** — public/free/read-only global news discovery source, currently under durable cooldown after real HTTP 429.
3. **USGS Earthquake FDSN API** — public/free/read-only official U.S. Geological Survey event source.

## Multi-source policy

- same `observation_id` + same summary across independent source adapters:
  - one result record;
  - evidence provenance is merged and deduplicated;
- same `observation_id` + conflicting summaries:
  - separate records;
  - `verification = DISPUTED`;
  - mutual contradiction references;
  - overall result cannot be COMPLETE;
- any PARTIAL / UNAVAILABLE / INVALID source observation:
  - overall result becomes PARTIAL;
  - source health becomes DEGRADED when usable evidence remains;
- COMPLETE requires:
  - at least one usable result record;
  - no unhealthy source observations;
  - no detected disagreement;
- result selection is source-balanced so one healthy source cannot monopolize the request result budget.

No heuristic merge is performed across different observation IDs.

## Deterministic acceptance

Targeted multi-source/source/worker suite:
- **35/35 PASS**

Selected exchange/research regression:
- **184/184 PASS in 2.77 s**

Covered:
- cross-source deduplication with merged provenance;
- explicit disagreement → DISPUTED/PARTIAL;
- mixed healthy + unavailable sources → PARTIAL/DEGRADED;
- durable GDELT cooldown prevents network calls;
- USGS source normalization;
- source-balanced result budget.

## Real owner-pilot execution

A real read-only multi-source cycle ran from the isolated KGM owner VM:

`CURRENT request → GDACS live + USGS live + GDELT cooldown → normalized observations → typed result`

Observed result:
- `research_status = PARTIAL`
- `coverage = PARTIAL`
- `source_health = DEGRADED`
- typed records: 10
- evidence sources represented in the bounded result: `gdacs-events`, `usgs-earthquake`
- GDELT network calls while cooldown active: **0**
- GDELT cooldown reason: `RATE_LIMITED`
- result id: `result-5187bb617f8d17ab15799608`
- recovery pending after completion: empty

The PARTIAL result is intentional and correct because the GDELT source is unavailable/cooling down while two other official sources remain usable.

## Defect found and corrected

The first live multi-source run exposed source starvation: lexicographic record selection allowed GDACS to consume the entire bounded result budget, hiding healthy USGS evidence. The worker now applies deterministic source-balanced selection before record construction. The repeated live run included both GDACS and USGS.

## Boundaries

- production/live service unchanged;
- no persistent scheduler;
- no K-Trader or Sentinel invocation;
- no paid fallback;
- no shared runtime;
- historical no-lookahead remains unchanged;
- Phase 23 canonical strategic position is not advanced by this technical acceptance.
