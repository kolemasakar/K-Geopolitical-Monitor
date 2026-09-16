# Phase 21 — Source Network Operational Adequacy & Evidence Population — Implementation Plan

Date: 2026-09-16
Status: `APPROVED / NOT_STARTED`
Decision: `docs/decisions/PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_ROADMAP_DECISION_2026-09-16.md`

## Objective

Turn the Phase 20 deterministic coverage framework into a policy-bound, evidence-populated operational source-network assessment, then use measured gaps to drive controlled source expansion and intelligence-quality validation.

## Entry facts from Phase 20

```text
GOVERNED_SOURCES = 10
OBSERVED_COVERAGE_CELLS = 17
TARGET_COVERAGE_POLICY = UNSET
KNOWN_ORIGIN_SOURCES = 0
CURRENT_REPOSITORY_HEALTH_MEASUREMENTS = 0
UNKNOWN_CELLS = 17
ADEQUATE_CELLS = 0
CONFIRMED_GAP_CELLS = 0
```

These are evidence states, not claims of good or bad coverage.

## Work breakdown

### P21.0 — Coverage Policy Definition & Criticality Contract

Deliverables:

- canonical policy schema/contract for `REQUIRED / OPTIONAL / NOT_REQUIRED / UNSET`;
- explicit geography/language/source-type requirements;
- criticality tiers where justified;
- freshness/latency expectations separated from factual credibility;
- deterministic validation and fail-closed handling for unspecified policy;
- no live acquisition mutation.

Gate:
`P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

### P21.1 — Existing Portfolio Provenance Resolution

Deliverables:

- evidence-backed source-level underlying-origin records where determinable;
- explicit syndication/copy/derivation relationships where determinable;
- origin groups only when supported;
- unresolved origin retained as `UNKNOWN`;
- no independence credit from domain/language/source counts.

Gate:
`P21_1_SOURCE_PROVENANCE_RESOLUTION_VALIDATED`

### P21.2 — Fresh Operational Health Baseline

Deliverables:

- bounded measurement procedure for the current 10 governed source paths;
- timestamped reachability/adapter/parser evidence;
- collection/content latency where measurable;
- recovery/degradation semantics using existing P12/P19/P20 machinery;
- no source expansion.

Gate:
`P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED`

### P21.3 — Coverage Adequacy Baseline v1

Deliverables:

- deterministic recomputation using policy + provenance + fresh health;
- operator and machine reports;
- explainable cell states and reasons;
- explicit unknowns where evidence remains insufficient;
- delta against P20 closure baseline.

Gate:
`P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_VALIDATED`

### P21.4 — Gap-Driven Source Expansion Plan

Deliverables:

- ranked gap inventory without opaque aggregate scoring;
- candidate source requirements derived from each measured gap;
- public/free-first constraint;
- legal/access/collection-method metadata;
- expected coverage contribution stated without assuming independence;
- rollback/disable plan;
- no live activation.

Gate:
`P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED`

### P21.5 — Controlled Public/Free Source Onboarding

Entry condition:

`LIVE_SOURCE_EXPANSION = EXPLICIT_OWNER_DECISION_REQUIRED`

Deliverables after separate approval:

- onboarding through P20.5 contract;
- fixtures/tests before activation;
- bounded deployment/change procedure;
- fresh health evidence after activation;
- rollback validation;
- no paid/shared dependency without separate authorization.

Gate:
`P21_5_CONTROLLED_SOURCE_ONBOARDING_VALIDATED`

### P21.6 — Intelligence Quality Impact Validation

Deliverables:

- before/after exact-cohort analysis where feasible;
- verification decision yield and unresolved-claim distribution;
- provenance completeness changes;
- contradiction detection/resolution workload changes;
- coverage of analytical outputs;
- forecast cohort/input coverage observations;
- no promotion of factual verification from coverage/performance metrics.

Gate:
`P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED`

### P21.7 — Phase Acceptance

Acceptance criteria:

- target policy is explicit enough to evaluate required coverage;
- current governed sources have fresh health evidence or explicit measurement limitations;
- origin evidence is improved without invented independence;
- measured gaps are explicit;
- any source expansion is gap-driven, controlled and separately authorized;
- factual verification authority remains P13.5/P13.6;
- no unapproved paid/shared/runtime/publication dependency is introduced.

Final gate:
`PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED`

## Safety and activation boundaries

Until separately approved:

```text
LIVE_SOURCE_EXPANSION = NO
LIVE_INGEST_CHANGE = NO
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
```

## First executable step

Begin P21.0 with a repository-only audit of existing coverage-policy schemas, region/language coverage contracts and P20.2 semantics. Produce an explicit policy proposal and validation matrix before modifying any live source/runtime state.
