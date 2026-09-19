# Phase 22 — Operational Evidence Pilot & High-Priority Coverage Expansion — Roadmap Decision

Date: 2026-09-19
Status: `APPROVED / P22_0_READY`
Project: `K-Geopolitical Monitor`
Parent strategic position: `PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`
Audit: `docs/analysis/POST_PHASE_21_STRATEGIC_AUDIT_2026-09-19.md`
Proposal: `docs/decisions/POST_PHASE_21_ROADMAP_DECISION_PROPOSAL_2026-09-19.md`
Authorization basis: explicit owner approval on 2026-09-19.

## Decision

Approve the next strategic development block as:

`Phase 22 — Operational Evidence Pilot & High-Priority Coverage Expansion`

Approval covers Phase 22 planning and implementation under the bounded owner-local/public-free-first constraints defined below.

This approval **does not by itself activate owner operations or authorize Wave-B source onboarding**. Those remain explicit owner gates inside Phase 22.

## Strategic objective

Convert the validated Phase 12-21 architecture into observed owner-local intelligence value while reducing the highest-priority measured coverage gaps.

Primary evidence chain:

`DISCOVER -> QUALIFY -> ONBOARD -> MEASURE HEALTH/PROVENANCE -> COLLECT -> VERIFY -> ANALYZE -> FORECAST INPUT -> OWNER FEEDBACK`

Success must be evidence-based, not architecture-only.

## Entry facts

At Phase 21 closure:

```text
TARGET_CELLS = 33
REQUIRED_CELLS = 27
REQUIRED_ADEQUATE = 1
REQUIRED_DEGRADED_COLLECTION = 1
REQUIRED_MISSING_EXPECTED_COVERAGE = 20
REQUIRED_THIN = 5

VERIFICATION_YIELD_IMPACT = NOT_OBSERVED
CONTRADICTION_WORKLOAD_IMPACT = NOT_OBSERVED
FORECAST_INPUT_IMPACT = NOT_OBSERVED
```

P21.4 already defines `B_HIGH_REQUIRED` as the next default planning cohort:

- 9 high-priority required gap cells;
- minimum 13 source-path deficit;
- minimum 13 healthy-source deficit;
- minimum 16 origin-evidence deficit from confirmed lower bound.

This is a planning basis, not a blanket onboarding authorization.

## Phase 22 sequence

### P22.0 — Entry Convergence & Owner Gates

Goal: converge canonical state and bind all Phase 22 activation boundaries.

Required outputs:

- Phase 21 closure preserved as immutable historical state;
- Phase 22 roadmap decision and implementation plan recorded;
- owner-operational activation state explicit;
- Wave-B onboarding authorization state explicit;
- public/free-first constraint explicit;
- no paid/shared/public/production implication;
- no migration `033`.

Gate:
`P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED`

### P22.1 — Bounded Owner-Only Operational Pilot

Goal: use validated Phase 14/19 capabilities to accumulate timestamped, provenance-bound owner-local operational evidence.

Entry requires a separate explicit owner decision:
`OWNER_ONLY_OPERATIONAL_ACTIVATION`.

No public ingress, shared runtime or production/live declaration.

Gate:
`P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED`

### P22.2 — Wave-B Candidate Discovery & Qualification

Goal: qualify public/free/anonymous-first candidates for the P21.4 `B_HIGH_REQUIRED` gap cohort.

Candidate discovery and qualification do not activate sources.

Gate:
`P22_2_WAVE_B_CANDIDATE_QUALIFICATION_VALIDATED`

### P22.3 — Controlled High-Priority Onboarding

Goal: onboard only explicitly owner-authorized candidates in small reversible cohorts through the P20.5 contract.

Entry requires a separate explicit owner decision for Wave B or a smaller named subset.

Every cohort requires fixtures/tests, provenance classification, health/freshness evidence and rollback/disable semantics.

Gate:
`P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED`

### P22.4 — Operational Coverage Rebaseline

Goal: recompute deterministic coverage after accepted cohorts and measure required-cell status deltas rather than raw source counts.

Gate:
`P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED`

### P22.5 — Semantic Corpus & Verification Observation

Goal: observe real post-expansion semantic corpus behavior through P13.5/P13.6.

Required observations include verification decision distribution, unresolved claims, provenance completeness, evidence independence and source contribution.

Gate:
`P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED`

### P22.6 — Contradiction / Analysis / Forecast-Input Impact

Goal: measure downstream effects on contradiction workload, analytical coverage and forecast-input evidence breadth without promoting factual truth from coverage or forecast metrics.

Gate:
`P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED`

### P22.7 — Owner Utility & Quality Observation

Goal: use the Phase-16 feedback/read-model line to observe usefulness, timeliness, noise, correction requests and operator utility.

Feedback remains advisory and non-promotional for factual truth.

Gate:
`P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED`

### P22.8 — Phase Acceptance

Final gate:
`PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED`

Acceptance requires observed evidence in both coverage and intelligence-utility dimensions.

## Explicit authorization

This roadmap decision authorizes:

- creation of Phase 22;
- Phase 22 planning and implementation;
- P22.0 entry-convergence work;
- repository-only/read-only preparation needed for later Phase 22 gates;
- public/free/anonymous-first candidate discovery and qualification when reached.

## Explicit non-authorization

This roadmap decision does **not** authorize:

- owner-operational activation before the P22.1 owner gate;
- Wave-B onboarding before the P22.3 owner gate;
- runtime deployment or service restart by implication;
- paid or secret-bearing source providers;
- shared runtime activation;
- public/shared ingress;
- migration `033`;
- canonical storage cutover;
- production/live cutover;
- Plugin build/publication;
- external publication;
- Phase 17 publication activation;
- Phase 18 shared-runtime activation.

## Permanent epistemic boundaries

Preserve:

`SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT`

`COVERAGE_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE`

`COLLECTION_HEALTH != CONTENT_CREDIBILITY`

`OPERATOR_FEEDBACK != FACTUAL_TRUTH`

`FORECAST_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE`

P13.5/P13.6 remain the sole canonical factual-verification authority.

## Entry state

```text
PHASE_22_STATE = APPROVED / P22_0_READY
PHASE_22_IMPLEMENTATION_AUTHORIZED = YES
OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED
WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED
NEXT_GATE = P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED
```
