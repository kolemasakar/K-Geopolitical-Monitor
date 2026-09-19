# Phase 21 — Source Network Operational Adequacy & Evidence Population — Implementation Plan

Date: 2026-09-16
Status: `IN_PROGRESS / P21_0_VALIDATED / P21_1_VALIDATED / P21_2_VALIDATED_WITH_MEASURED_DEGRADATION / P21_3_VALIDATED / P21_4_VALIDATED / P21_5_VALIDATED / P21_6_VALIDATED / P21_7_READY`
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

## Current Phase 21 state

Validated sequence: `P21.0 -> P21.1 -> P21.2 -> P21.3 -> P21.4 -> P21.5 -> P21.6`.

P21.4 gate: `P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED`.
Implementation merge anchor: `277b219726008c70671cf4d804c857c98f8ab0c4`.
Validation: GitHub CI #1710 — `1281 passed in 115.53s / SUCCESS`.

Current boundary: `P21_6_VALIDATED / P21_7_READY`. Wave A structural impact is validated without inventing semantic-quality evidence: one required missing cell is removed, no adequate-cell gain is observed, and verification/contradiction/forecast effects remain `NOT_OBSERVED`. Runtime deployment, paid/shared providers, additional source waves, production/live cutover and Plugin/publication remain unauthorized.

## ChatGPT / Plugin architecture boundary

OpenAI's Custom GPT retirement changes the future ChatGPT-facing deployment wrapper, not Phase 21 evidence semantics.

Canonical decision:
`docs/decisions/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md`.

Phase 21 requirements:

- core source, provenance, health, coverage and verification contracts remain deployment-wrapper independent;
- no new long-term KGM integration is to be designed around legacy Custom GPT Actions;
- future ChatGPT-facing workflow is Plugin-first;
- external capabilities must later be classified as supported App / Connector / custom MCP integration candidates where needed;
- Plugin permissions/sharing/build capability must be revalidated on the actual launch account/workspace;
- model-specific ChatGPT configuration is not a canonical KGM dependency;
- P21.6 regression evidence should be reusable later as Plugin skill/reference/integration regression cases;
- Plugin/App/Connector/MCP routing never creates provenance, independence, health or factual-verification credit.

This architecture rebase does not activate a Plugin or change Phase 21 runtime boundaries.

## Work breakdown

### P21.0 — Coverage Policy Definition & Criticality Contract

State: `VALIDATED`

Gate:
`P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

Validated outputs:

- canonical policy schema/contract for `REQUIRED / OPTIONAL / NOT_REQUIRED / UNSET`;
- explicit geography/language/source-type requirements;
- criticality tiers;
- freshness/latency expectations separated from factual credibility;
- deterministic validation and fail-closed handling for unspecified policy;
- global macroregional baseline with 33 targets / 20 geography scopes / 15 language labels;
- immutable owner approval bound to the reviewed manifest Git blob;
- no live acquisition mutation.

### P21.1 — Existing Portfolio Provenance Resolution

State: `VALIDATED`

Deliverables:

- evidence-backed source-level underlying-origin records where determinable;
- explicit syndication/copy/derivation relationships where determinable;
- origin groups only when supported;
- unresolved origin retained as `UNKNOWN`;
- no independence credit from domain/language/source counts.

Gate:
`P21_1_SOURCE_PROVENANCE_RESOLUTION_VALIDATED`

### P21.2 — Fresh Operational Health Baseline

State: `VALIDATED_WITH_MEASURED_DEGRADATION`

Deliverables:

- bounded measurement procedure for the current 10 governed source paths;
- timestamped reachability/adapter/parser evidence;
- collection/content latency where measurable;
- recovery/degradation semantics using existing P12/P19/P20 machinery;
- no source expansion.

Gate:
`P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED`

### P21.3 — Coverage Adequacy Baseline v1

State: `VALIDATED`

Deliverables:

- deterministic recomputation using approved policy + provenance + fresh health;
- operator and machine reports;
- explainable cell states and reasons;
- explicit unknowns where evidence remains insufficient;
- delta against P20 closure baseline.

Gate:
`P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_VALIDATED`

### P21.4 — Gap-Driven Source Expansion Plan

State: `VALIDATED`
Gate: `P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED`
Merge anchor: `277b219726008c70671cf4d804c857c98f8ab0c4`
Validation: GitHub CI #1710 / run `35138511971`, job `104936832558`: `1281 passed in 115.53s / SUCCESS`.

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

State: `VALIDATED_WITH_MEASURED_CONTENT_STALENESS`

Owner authorization: `docs/evidence/P21_5_CONTROLLED_SOURCE_ONBOARDING_OWNER_AUTHORIZATION_2026-09-16.json`

Entry condition: `SATISFIED / EXPLICIT_OWNER_DECISION_2026-09-16`

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

State: `VALIDATED_WITH_STRUCTURAL_IMPACT_ONLY`
Gate: `P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED`
Evidence: `docs/evidence/P21_6_INTELLIGENCE_QUALITY_IMPACT_2026-09-17.json`
Result: `docs/implementation/P21_6_INTELLIGENCE_QUALITY_IMPACT_RESULT.md`
Merge anchor: `c7a29377457b338d8ddc55f7e989dd13557f36b7`
Validation: GitHub CI #1793 / run `35437681811`, job `105883018288`: `1305 passed in 89.63s / SUCCESS`.

Deliverables:

- before/after exact-cohort analysis where feasible;
- verification decision yield and unresolved-claim distribution;
- provenance completeness changes;
- contradiction detection/resolution workload changes;
- coverage of analytical outputs;
- forecast cohort/input coverage observations;
- reusable regression cases for future Plugin skill/reference/integration validation;
- no promotion of factual verification from coverage/performance metrics.

Gate:
`P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED`

### P21.7 — Phase Acceptance

State: `READY_TO_BEGIN`

Acceptance criteria:

- target policy is explicit enough to evaluate required coverage;
- current governed sources have fresh health evidence or explicit measurement limitations;
- origin evidence is improved without invented independence;
- measured gaps are explicit;
- any source expansion is gap-driven, controlled and separately authorized;
- factual verification authority remains P13.5/P13.6;
- no unapproved paid/shared/runtime/publication dependency is introduced;
- future ChatGPT-facing delivery remains Plugin-first and separate from factual authority.

Final gate:
`PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED`

## Safety and activation boundaries

Current bounded authorization and preserved deployment boundaries:

```text
P21_5_BOUNDED_PUBLIC_FREE_ONBOARDING = AUTHORIZED_WAVE_A
DEPLOYED_RUNTIME_SOURCE_EXPANSION = NO
DEPLOYED_LIVE_INGEST_CHANGE = NO
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
PHASE_17_PLUGIN_CAPABILITY_REVALIDATION_REQUIRED = YES
```

## Next executable step

Begin P21.7 Phase Acceptance against the validated P21.0-P21.6 evidence chain. Confirm policy adequacy, measured health limitations, provenance boundaries, explicit gaps, controlled Wave-A effects and preserved P13.5/P13.6 factual-verification authority. Do not authorize additional source waves, deploy/restart the stale `/opt` runtime, authorize paid/shared resources, create migration `033`, or activate Plugin/publication surfaces.
