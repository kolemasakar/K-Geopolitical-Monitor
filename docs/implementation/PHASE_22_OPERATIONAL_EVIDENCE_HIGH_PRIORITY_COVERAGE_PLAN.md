# Phase 22 — Operational Evidence Pilot & High-Priority Coverage Expansion — Implementation Plan

Date: 2026-09-19
Status: `APPROVED / P22_0_VALIDATED / P22_1_VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION / P22_2_VALIDATED_WITH_ONBOARDING_BLOCKERS / P22_3_B1_AUTHORIZED_IMPLEMENTATION_READY`
Decision: `docs/decisions/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_ROADMAP_DECISION_2026-09-19.md`
Parent audit: `docs/analysis/POST_PHASE_21_STRATEGIC_AUDIT_2026-09-19.md`

## Objective

Produce observed owner-local intelligence evidence while reducing the highest-priority required source gaps, without weakening the validated P13 factual-verification path or activating public/shared/production infrastructure.

## Entry state

Phase 21 is closed at:

`PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`

Current required-cell structural state:

```text
REQUIRED_TOTAL = 27
ADEQUATE = 1
DEGRADED_COLLECTION = 1
MISSING_EXPECTED_COVERAGE = 20
THIN = 5
```

Current downstream evidence state:

```text
VERIFICATION_YIELD_IMPACT = NOT_OBSERVED
CONTRADICTION_WORKLOAD_IMPACT = NOT_OBSERVED
FORECAST_INPUT_IMPACT = NOT_OBSERVED
```

## Authorization boundary

Approved now:

- Phase 22 planning and implementation;
- P22.0 entry convergence;
- repository-only/read-only preparation;
- public/free/anonymous-first candidate discovery/qualification;
- one bounded P22.1 owner-local operational pilot on `kgm-e4-owner-pilot` under `docs/decisions/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_AUTHORIZATION_2026-09-19.md`.

Not approved now:

```text
BOUNDED_P22_1_PILOT = COMPLETED
PERSISTENT_OWNER_OPERATION = NOT_ACTIVATED
WAVE_B_ONBOARDING = APPROVED_FOR_B1_INSTITUTIONAL_COHORT
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
PUBLIC_INGRESS = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
```

## Default Wave-B planning cohort

Source: P21.4 validated gap-driven plan.

`B_HIGH_REQUIRED`:

- `east_asia.zh.national_media`;
- `global.en.sanctions_regulatory`;
- `global.en.wire_service`;
- `middle_east.ar.national_media`;
- `russia.ru.official_government`;
- `united_states.en.official_government`;
- `black_sea.tr.national_media`;
- `central_europe.pl.national_media`;
- `russia.ru.national_media`.

Planning deficits:

- 9 gap cells;
- 13 source paths;
- 13 healthy-source positions;
- 16 origin-evidence positions from confirmed lower bound.

This cohort is not automatically authorized for onboarding.

## Work breakdown

### P22.0 — Entry Convergence & Owner Gates

State: `VALIDATED`
Result: `docs/implementation/P22_0_ENTRY_CONVERGENCE_OWNER_GATES_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED.md`

Deliverables:

- canonical decision/plan/state/ROADMAP/handoff convergence;
- Phase 21 closure regression protection;
- explicit owner-operational activation gate;
- explicit Wave-B onboarding gate;
- public/free-first and no-auto-independence boundaries;
- no runtime mutation.

Gate:
`P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED`

### P22.1 — Bounded Owner-Only Operational Pilot

State: `VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION`
Authorization: `docs/decisions/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_AUTHORIZATION_2026-09-19.md`
Evidence: `docs/evidence/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_2026-09-19.json`
Result: `docs/implementation/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED.md`

Execution result:

- exact-main isolated owner-local run on `kgm-e4-owner-pilot`;
- ARM64 `aarch64`;
- one supervisor execution: `COMPLETED`;
- collection: `PARTIAL`;
- Consilium: `SUCCESS / 0 items`;
- GDELT: `FAILED / HTTP 429`;
- semantic corpus: `NOT_OBSERVED`;
- deployed runtime SHA/service unchanged;
- isolated DB integrity: `ok`;
- persistent owner operation remains `NOT_ACTIVATED`.

Gate:
`P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED`

### P22.2 — Wave-B Candidate Discovery & Qualification

State: `VALIDATED_WITH_ONBOARDING_BLOCKERS`
Result: `docs/implementation/P22_2_WAVE_B_CANDIDATE_QUALIFICATION_RESULT.md`
Evidence: `docs/evidence/P22_2_WAVE_B_CANDIDATE_QUALIFICATION_2026-09-19.json`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_2_WAVE_B_CANDIDATE_QUALIFICATION_VALIDATED.md`

Candidate discovery/qualification may remain repository-only and non-activating.

Deliverables:

- public/free/anonymous-first candidates per cell;
- legal/access/collection-method metadata;
- adapter feasibility;
- provenance/origin evidence;
- health/freshness preflight;
- explicit unresolved/paid-only gaps.

Gate:
`P22_2_WAVE_B_CANDIDATE_QUALIFICATION_VALIDATED`

### P22.3 — Controlled High-Priority Onboarding

State: `AUTHORIZED_B1_IMPLEMENTATION_READY`
Authorization: `docs/decisions/P22_3_B1_CONTROLLED_ONBOARDING_OWNER_AUTHORIZATION_2026-09-19.md`

Authorized cohort: `B1_INSTITUTIONAL` = OFAC, UK Sanctions List, Government of Russia, White House.

Repository activation is conditional per source on full P20.5 PASS. The remaining 9 P22.2 candidates are not authorized.

Deliverables after approval:

- small reversible cohorts;
- fixtures/tests first;
- P20.5 onboarding validation;
- fresh health evidence;
- provenance classification;
- no automatic independence credit;
- rollback/disable evidence.

Gate:
`P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED`

### P22.4 — Operational Coverage Rebaseline

State: `PLANNED`

Deliverables:

- deterministic post-cohort coverage matrix;
- required-cell state deltas;
- freshness/health limitations;
- provenance lower bounds;
- no source-count-only success metric.

Gate:
`P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED`

### P22.5 — Semantic Corpus & Verification Observation

State: `PLANNED`

Deliverables:

- observed post-expansion semantic corpus;
- P13.5/P13.6 verification decision distribution;
- unresolved-claim distribution;
- provenance completeness;
- evidence-independence observations;
- exact cohort membership.

Gate:
`P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED`

### P22.6 — Contradiction / Analysis / Forecast-Input Impact

State: `PLANNED`

Deliverables:

- contradiction workload/resolution observations;
- analytical coverage observations;
- forecast-input evidence breadth;
- explicit sample and coverage limitations;
- no factual promotion from forecast/coverage metrics.

Gate:
`P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED`

### P22.7 — Owner Utility & Quality Observation

State: `PLANNED`

Deliverables:

- usefulness/timeliness/noise observations;
- correction-request observations;
- delivery/read-model utility;
- exact-cohort feedback metrics;
- no self-modifying policy.

Gate:
`P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED`

### P22.8 — Phase Acceptance

State: `PLANNED`

Acceptance dimensions:

- measurable required coverage improvement or explicit fail-closed reason why not;
- measured source health/freshness;
- improved provenance without invented independence;
- real semantic corpus observed;
- verification/contradiction/forecast-input impacts measured;
- owner utility evidence measured where pilot authorized;
- P13.5/P13.6 authority preserved;
- no unauthorized paid/shared/public/production dependency.

Final gate:
`PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED`

## Next executable step

P22.1 and P22.2 are validated with explicit measured limitations.

P22.3 B1 is owner-authorized. Next execute B1 fixture/adapter/health/rollback/P20.5 readiness and activate only sources that pass. Persistent owner operation remains not activated; the remaining 9 P22.2 candidates remain unauthorized.

