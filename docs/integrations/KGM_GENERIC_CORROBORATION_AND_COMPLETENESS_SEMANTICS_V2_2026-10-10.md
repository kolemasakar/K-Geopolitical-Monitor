# KGM Generic Corroboration and Completeness Semantics v2 — 2026-10-10

## Decision

**GENERIC_CORROBORATION_AND_COMPLETENESS_SEMANTICS_V2 = PASS**

Exact validated implementation/test SHA:
`b5f34a7ba8c9f30bfdd3e06eea1a5ad9c817a6b0`

Selected research/exchange regression:
**313/313 PASS in 5.83 s**

This checkpoint applies only to the bounded private owner-pilot independent-research path. It does not authorize production/live daemon operation, unattended scheduling, Sentinel transport, K-Trader integration, paid providers/fallbacks, shared runtime, public Plugin publication or HP-OMEN use.

## 1. Generic canonical corroboration

The canonical corroboration report now supports two strict association paths:

1. earthquake observations:
   - structured earthquake event parameters;
   - bounded time/distance association;

2. generic geopolitical observations:
   - exact explicit `event_identity`;
   - explicit `event_descriptor`;
   - no fuzzy matching;
   - no NLP association;
   - no synonym inference.

Generic observations sharing the exact event identity are grouped into one canonical corroboration group.

The group then reuses the existing origin/claim/verification boundary:
- SAME_ORIGIN vs DISTINCT_ORIGIN;
- independent-origin credit;
- AGREES / DIFFERS / UNKNOWN claim relation;
- ambiguity denial;
- explicit-verification eligibility;
- no automatic factual verification.

Duplicate observations from the same source inside one generic event group make the group ambiguous and deny independent-origin credit.

## 2. Generic verification-boundary behavior

Deterministic tests prove:

- exact generic event + two distinct origins + matching claim signature:
  - `DISTINCT_ORIGIN`;
  - independent-origin credit = true;
  - `ELIGIBLE_FOR_EXPLICIT_VERIFICATION`;
  - automatic verification = false;
  - factual verification credit = false.

- exact generic event + same underlying origin:
  - `SAME_ORIGIN`;
  - no independence credit;
  - `INELIGIBLE`.

- exact generic event + different claim signatures:
  - `claim_relation = DIFFERS`;
  - `EVENT_CORROBORATED_CLAIM_UNRESOLVED`;
  - no automatic verification.

Generic event records themselves continue to remain `UNVERIFIED` unless a separate explicit immutable verification decision is created.

## 3. Typed result v3

The policy-bound worker now emits:

`kgm.research.result.v3`

It preserves:
- typed records;
- canonical corroboration;

and adds:
- `source_contributions`;
- `completeness_semantics`.

The older v1/v2 validator paths remain accepted for legacy artifacts.

## 4. Explicit source contribution semantics

Each source contribution states:

- source id;
- required/optional status;
- source-run status;
- total observation count;
- evidence-bearing observation count;
- corroboration-group participation count;
- contribution status:
  - `CONTRIBUTED`
  - `EMPTY`
  - `DEGRADED`.

This makes source participation explicit rather than inferring it from the global result status.

## 5. Completeness semantics v2

Added:

`kgm.completeness.v2`

Typed fields:

- `portfolio_execution_complete`
- `all_required_sources_invoked`
- `all_required_sources_healthy`
- `all_required_sources_contributed`
- `required_source_empty_present`
- `complete_does_not_imply_all_sources_contributed = true`

The validator recomputes these relationships and rejects contradictory completeness claims.

Therefore an approved healthy-empty required source remains compatible with global `COMPLETE`, while the result explicitly states:

`all_required_sources_contributed = false`

This removes the earlier ambiguity without changing the established healthy-EMPTY source contract.

## 6. Live owner-VM generic corroboration acceptance

A fresh live owner-VM cycle used:

- Moldova MFA official page;
- NATO official public news/search path.

Event:
- 8 October 2026;
- Radmila Shekerinska / Mihai Popșoi;
- Chisinau;
- NATO–Moldova bilateral meeting.

Typed result:
- schema: `kgm.research.result.v3`;
- research status: `COMPLETE`;
- coverage: `COMPLETE`;
- source health: `HEALTHY`;
- result id:
  `result-7212e33b2de5f3bafb8936c3`;
- stage SHA:
  `d5ebca8de383d9b935b6f2622c6be9bac910c06e95377ee1130619ef66a86f48`.

Canonical generic corroboration:
- corroboration id:
  `corr-792c5926a4004f1dd1e7e65a`;
- origins:
  - `moldova-mfa`
  - `nato`;
- `DISTINCT_ORIGIN`;
- claim relation: `AGREES`;
- independent-origin credit: true;
- ambiguity: false;
- `ELIGIBLE_FOR_EXPLICIT_VERIFICATION`;
- automatic verification: false;
- factual verification credit: false.

Both required sources report:
- `CONTRIBUTED`;
- one evidence observation;
- one corroboration-group participation.

Completeness semantics:
- portfolio execution complete: true;
- all required sources invoked: true;
- all required sources healthy: true;
- all required sources contributed: true;
- required source empty present: false;
- COMPLETE does not imply all sources contributed: true.

The merged factual record remains `UNVERIFIED`.

## 7. Validation

Targeted generic-corroboration / result-v3 / worker / validator suite:
**33/33 PASS**

Selected research/exchange regression:
**313/313 PASS in 5.83 s**

## Readiness interpretation

The primary limitation found by `INDEPENDENT_RESEARCH_QUALITY_AUDIT_V1` is closed:

generic political/diplomatic/military/economic mappings now enter the canonical corroboration → explicit-verification eligibility boundary.

The completeness ambiguity is also closed at the typed-result level through explicit source-contribution semantics.

Current readiness remains conservatively:

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS`

The remaining P1 limitations are quality/coverage/operational-scale items, not blockers for bounded private owner-pilot independent research.

## Recommended next track after chat transition

`POST_READINESS_CONSOLIDATION_AND_PHASE_DECISION`

Objectives:
1. perform a consolidated audit of all owner-pilot readiness and P1 milestones;
2. decide whether `PASS_WITH_P1_LIMITATIONS` can be promoted to an owner-approved stronger readiness gate;
3. separate production-readiness work from research-quality expansion;
4. decide PR #163 closure/merge strategy;
5. define the next strategic ROADMAP phase before enabling any unattended runtime or cross-project integration.
