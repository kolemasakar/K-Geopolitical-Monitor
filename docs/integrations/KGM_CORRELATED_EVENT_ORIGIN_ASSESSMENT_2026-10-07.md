# KGM correlated-event underlying-origin assessment — 2026-10-07

## Decision

**KGM_CORRELATED_EVENT_ORIGIN_ASSESSMENT = PASS_WITH_ZERO_INDEPENDENT_ORIGIN_CREDIT**

Exact validated code SHA: `7d04b132ea16c90bd7d532fa9c1f09c0dc3b3bc1`.

This checkpoint remains owner-pilot only. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, change the canonical Phase 23 gate, or authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Implemented origin model

Source observations may carry an explicit `origin_group`.

Fail-closed assessment rules:
- any missing origin group → `UNKNOWN`, no independence credit;
- all correlated observations share one explicit origin group → `SAME_ORIGIN`, no independence credit;
- multiple distinct explicit origin groups → `DISTINCT_ORIGIN`, origin-level independence credit permitted;
- origin assessment is separate from event correlation and claim verification.

## Source mappings

For this earthquake owner-pilot:
- USGS Earthquake FDSN observations → `origin_group = usgs-neic`;
- GDACS earthquake observations reporting `source = NEIC` → `origin_group = usgs-neic`;
- GDACS observations without explicit NEIC provenance remain origin-unknown rather than inferred.

## Real correlated-event assessment

Live 24-hour GDACS + USGS earthquake cohort:

- correlated events: **16**
- `SAME_ORIGIN`: **16**
- `DISTINCT_ORIGIN`: **0**
- `UNKNOWN`: **0**
- events receiving independent-origin credit: **0**

All 16 correlated GDACS/USGS earthquake events resolved to the same `usgs-neic` origin group.

This confirms that two distinct public source paths are not automatically independent corroboration. GDACS is acting as a downstream presentation/aggregation path for these NEIC-origin earthquake records.

## Validation

Targeted origin/identity/multi-source/source/worker suite:
- **34/34 PASS**

Selected exchange/research regression:
- **192/192 PASS in 2.88 s**

## Consequence

KGM may keep:
- event-correlation credit: YES;
- multiple provenance-path evidence: YES.

KGM must not grant:
- automatic independent-origin corroboration credit;
- automatic factual verification credit.

The next meaningful source expansion should target a genuinely independent earthquake or event origin if independence/corroboration yield is the goal.
