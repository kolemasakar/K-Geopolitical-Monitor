# Phase 22 — Operational Evidence Pilot & High-Priority Coverage Expansion — Implementation Plan

Date: 2026-09-19
Status: `APPROVED / P22_0_READY`
Decision: `docs/decisions/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_ROADMAP_DECISION_2026-09-19.md`

## Objective

Generate observed owner-local intelligence evidence while reducing high-priority required source-network gaps, using the validated Phase 13-16 and Phase 19-21 contracts.

## Entry facts

Phase 21 closed at:

`PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`

Current required-cell structural projection:

```text
REQUIRED_CELLS = 27
ADEQUATE = 1
DEGRADED_COLLECTION = 1
MISSING_EXPECTED_COVERAGE = 20
THIN = 5
```

P21.6 semantic downstream effects remain:

```text
VERIFICATION_YIELD_IMPACT = NOT_OBSERVED
CONTRADICTION_WORKLOAD_IMPACT = NOT_OBSERVED
FORECAST_INPUT_IMPACT = NOT_OBSERVED
```

P21.4 Wave-B planning cohort:

- wave: `B_HIGH_REQUIRED`;
- gap cells: `9`;
- minimum source-path deficit: `13`;
- minimum healthy-source deficit: `13`;
- origin-evidence deficit lower bound: `16`.

Wave-B cells:

- `east_asia.zh.national_media`;
- `global.en.sanctions_regulatory`;
- `global.en.wire_service`;
- `middle_east.ar.national_media`;
- `russia.ru.official_government`;
- `united_states.en.official_government`;
- `black_sea.tr.national_media`;
- `central_europe.pl.national_media`;
- `russia.ru.national_media`.

## Work breakdown

### P22.0 — Entry Convergence & Owner Gates

State: `READY_TO_BEGIN`

Validate:

- canonical Phase-21 closure and current main;
- Phase-14 owner-operational readiness remains `VALIDATED_READY / NOT_ACTIVATED`;
- Phase-19 normal monitoring/recovery baseline remains valid;
- Phase-16 operator/quality path remains provider-neutral and non-promotional;
- P13.5/P13.6 remain factual-verification authority;
- owner-operational activation remains separately gated;
- Wave-B discovery/qualification is permitted, but onboarding remains separately gated;
- paid/shared/public/production/plugin/migration-033 boundaries remain closed.

Gate:
`P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED`

### P22.1 — Bounded Owner-Only Operational Pilot

State: `BLOCKED_BY_OWNER_GATE`

Required entry decision:
`OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`

No activation is implied by Phase-22 approval.

### P22.2 — Wave-B Candidate Discovery & Qualification

State: `AUTHORIZED_AFTER_P22_0`

Public/free/anonymous-first research and qualification only.

No onboarding mutation.

Gate:
`P22_2_WAVE_B_CANDIDATE_QUALIFICATION_VALIDATED`

### P22.3 — Controlled High-Priority Onboarding

State: `BLOCKED_BY_OWNER_GATE`

Required entry decision:
`WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED`

Use small reversible cohorts and P20.5 onboarding contract.

### P22.4 — Operational Coverage Rebaseline

State: `SEQUENTIAL`

Recompute health, provenance and coverage after approved onboarding.

### P22.5 — Semantic Corpus & Verification Observation

State: `SEQUENTIAL`

Require actual corpus evidence; do not infer downstream quality from structural coverage.

### P22.6 — Downstream Intelligence Impact

State: `SEQUENTIAL`

Measure contradiction, analytical and forecast-input effects.

### P22.7 — Owner Utility & Quality Observation

State: `SEQUENTIAL`

Use Phase-16 delivery/operator-quality semantics. Feedback remains advisory.

### P22.8 — Phase Acceptance

State: `SEQUENTIAL`

Final gate:
`PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED`

## Current activation/resource boundaries

```text
OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED
WAVE_B_CANDIDATE_DISCOVERY_QUALIFICATION = AUTHORIZED_AFTER_P22_0
WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
PUBLIC_INGRESS = NOT_APPROVED / NOT_DEPLOYED
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
```

## Next executable step

Begin P22.0 Entry Convergence & Owner Gates. P22.0 is read-only/governance validation and must not activate owner monitoring or Wave-B onboarding.
