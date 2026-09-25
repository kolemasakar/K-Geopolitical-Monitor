# Phase 23 — Evidence Depth, Corroboration & Operational Yield — Implementation Plan

Date: 2026-09-20
Status: `APPROVED / P23_0_VALIDATED / P23_1_VALIDATED_WITH_PARTIAL_REMEDIATION / P23_2_VALIDATED_WITH_ZERO_UNDERLYING_ORIGIN_RESOLUTION / P23_3_VALIDATED_WITH_ZERO_CORROBORATION_POPULATION / P23_4_PRESELECTION_COMPLETE_OWNER_DECISION_REQUIRED / UKSL_CONTROLLED_PILOT_PASS_WITH_MATERIAL_LIMITATIONS`
Decision: `docs/decisions/PHASE_23_EVIDENCE_DEPTH_CORROBORATION_OPERATIONAL_YIELD_ROADMAP_DECISION_2026-09-20.md`

## Objective

Increase evidence yield per source path by combining selective coverage work with underlying-origin resolution, corroboration, downstream intelligence measurement and an explicitly gated owner-facing sample.

## P23.0 — Entry Convergence & Owner Gates

State: `VALIDATED`
Gate: `P23_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED`

Outputs: owner decision, Phase 23 ROADMAP/state/handoff convergence, evidence-yield success rule, explicit source/resource/delivery gates, HP-OMEN exclusion and Actions quota contingency.

## P23.1 — B1 Blocker Remediation & Selective Source Readiness

State: `VALIDATED_WITH_PARTIAL_REMEDIATION`
Gate: `P23_1_B1_BLOCKER_REMEDIATION_READINESS_VALIDATED`

UKSL bounded Range acquisition/parser remediation is validated and ready only for a later owner-gated activation revalidation. Government of Russia remains blocked on HTTPS transport timeout. No source activation, runtime mutation or acquisition-limit relaxation occurred.

## P23.2 — Underlying-Origin / Provenance Resolution
State: `VALIDATED_WITH_ZERO_UNDERLYING_ORIGIN_RESOLUTION`
Gate: `P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED`

A read-only fail-closed observer now distinguishes first-party publication provenance from actual underlying-origin resolution. The exact reference cohort remains 0 resolved / 28 unresolved; no independence credit is created.

## P23.3 — Corroboration & Evidence Relations
State: `VALIDATED_WITH_ZERO_CORROBORATION_POPULATION`
Gate: `P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED`

Exact 28-claim cohort: 28 ATTRIBUTION_ONLY, 0 supporting relations, 0 current independence assessments and 0 corroborated claims. Validation records observation of absence, not factual refutation or independence credit.

## P23.4 — Selective Evidence-Yield Coverage Expansion
State: `PRESELECTION_COMPLETE / OWNER_DECISION_REQUIRED_FOR_EXPANSION`
Gate: `P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED` — **NOT YET VALIDATED**

Selection-readiness package: `docs/evidence/P23_4_EVIDENCE_YIELD_SELECTION_READINESS_2026-09-21.json`.

Owner-gated activation-revalidation candidate: `uk-sanctions-list-en`. Rights-review preparation cohort: `cctv-news-zh`, `anadolu-en`, `trt-haber-tr`. No source or repository activation occurred.

2026-09-25 controlled UKSL pilot: observed HTTPS 206, exact 1.5 MB range, 1,827 complete physical data rows and 38 distinct official designation IDs. Duplicate-ID inflation remediated; staged captured/live runs each return 38 unique items. This partial range is NOT comprehensive coverage; report and Last-Modified 2026-09-21 do not establish policy freshness. Transport-level HTTP 206/Content-Range enforcement and explicit completeness policy review remain prerequisites to any repository activation. Owner permits foreign VPN for `government.ru`, but no Tailscale exit node is configured. Details: `docs/implementation/P23_4_UKSL_CONTROLLED_READONLY_PILOT_RESULT.md`. P23.4 full gate remains NOT VALIDATED.

## P23.5 — Downstream Intelligence-Yield Observation
State: `PLANNED`
Gate: `P23_5_DOWNSTREAM_INTELLIGENCE_YIELD_VALIDATED`

## P23.6 — Bounded Owner-Facing Delivery & Feedback
State: `OWNER_DECISION_REQUIRED_BEFORE_EXECUTION`
Gate: `P23_6_BOUNDED_OWNER_DELIVERY_FEEDBACK_VALIDATED`

## P23.7 — Phase Acceptance
State: `PLANNED`
Final gate: `PHASE_23_EVIDENCE_DEPTH_CORROBORATION_OPERATIONAL_YIELD_VALIDATED`

## Constraints

- `HP_OMEN = OUT_OF_SCOPE`;
- `GITHUB_HOSTED_ACTIONS = DO_NOT_INTENTIONALLY_TRIGGER_UNTIL_2026-10-01`;
- `PERSISTENT_OWNER_OPERATION = NOT_ACTIVATED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- `MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- paid/shared resources and Plugin publication remain unauthorized;
- P13.5/P13.6 remain factual-verification authority.
