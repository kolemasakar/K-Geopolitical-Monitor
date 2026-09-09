# PROJECT_DOCUMENTATION_GOVERNANCE

Version: 1.1
Status: APPROVED / CURRENT_STATE_SYNCHRONIZED_4_35
Project: K-Geopolitical Monitor

## Purpose

Defines project-specific documentation governance.

It supplements the canonical file standard:

`AI_general/docs/PROJECT_FILE_STANDARD.md`

## Documentation principles

Documentation must distinguish:

- proposed;
- approved;
- implemented;
- validated;
- operational.

These states are not interchangeable.

## Source of Truth

Primary documents:

- `PROJECT_CONCEPT_FOUNDATION.md` — approved product intent;
- `ROADMAP.md` — development phases and gates;
- `docs/state/CURRENT_PROJECT_STATE.json` — machine-readable current-state contract;
- `PROJECT_DOCUMENTATION_GOVERNANCE.md` — documentation rules;
- `ARCHITECTURE.md` — system architecture;
- `DATA_MODELS.md` — data structures;
- `SOURCE_POLICY.md` — information sources;
- `VERIFICATION_MODEL.md` — verification rules;
- `FORECASTING_MODEL.md` — forecast rules;
- `REPORTING_MODEL.md` — output formats;
- `TEST_PLAN.md` — validation criteria.

## Precedence

When conflicts exist:

1. explicit approved owner decision;
2. canonical source-of-truth document;
3. approved ADR/decision record;
4. validated implementation and validation evidence;
5. non-validated implementation;
6. historical/recovery materials.

For current machine-readable project position, `docs/state/CURRENT_PROJECT_STATE.json` is authoritative unless superseded by a newer explicit approved owner decision.

## Document lifecycle

Statuses:

- DRAFT;
- REVIEW_REQUIRED;
- APPROVED;
- ACTIVE;
- SUPERSEDED;
- DEPRECATED.

## Change control

Material changes require:

1. proposal;
2. impact analysis;
3. approval;
4. documentation update;
5. implementation;
6. validation.

A validation result does not silently authorize activation, production/live operation, provider spend, canonical migration or cutover.

## Architecture Decision Records

Major architectural decisions require ADR/decision records.

Accepted decision records preserve decision history and are not rewritten after acceptance; later changes are recorded in new decisions/checkpoints.

## Recovery principle

Recovery artifacts are transfer records, not permanent sources of truth.

Current canonical repository state has priority over historical recovery files.

## Documentation rule

No implementation should silently redefine approved product intent.

No documentation should claim validated behavior without validation evidence.

Provider/environment labels must not be promoted into KGM operational status. In particular, Railway's environment label `production` does not make the disposable Phase 18 A1 candidate KGM production/live.

## Current state

- Product Concept: `APPROVED`;
- Strategic Roadmap: `APPROVED / v4`, roadmap document `4.34`;
- State synchronization: `4.35`;
- Implementation: `ACTIVE / PHASES_0_18_IMPLEMENTED_TO_VALIDATED_GATES`;
- Phase 18 P18.0–P18.9: `VALIDATED`;
- Phase 18 A1 Railway/PostgreSQL RLS preflight: `VALIDATED`;
- current position: `PHASE_18_ACTIVATION_A1_VALIDATED_OWNER_ACTIVATION_GATE`;
- Phase 18 activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- canonical runtime storage: `PROJECT_LOCAL_ONLY`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- production/live: `NOT_OPERATIONAL`;
- paid providers: `NONE_APPROVED`.

Latest evidence checkpoint:
`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md`
