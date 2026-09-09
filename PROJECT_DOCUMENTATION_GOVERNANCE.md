# PROJECT_DOCUMENTATION_GOVERNANCE

Version: 1.0
Status: APPROVED
Project: K-Geopolitical Monitor

## Purpose

Defines project-specific documentation governance.

It supplements the canonical file standard:

AI_general/docs/PROJECT_FILE_STANDARD.md

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

- PROJECT_CONCEPT_FOUNDATION.md - approved product intent;
- ROADMAP.md - development phases and gates;
- PROJECT_DOCUMENTATION_GOVERNANCE.md - documentation rules;
- ARCHITECTURE.md - system architecture;
- DATA_MODELS.md - data structures;
- SOURCE_POLICY.md - information sources;
- VERIFICATION_MODEL.md - verification rules;
- FORECASTING_MODEL.md - forecast rules;
- REPORTING_MODEL.md - output formats;
- TEST_PLAN.md - validation criteria.

## Precedence

When conflicts exist:

1. explicit approved owner decision;
2. canonical source of truth document;
3. approved ADR;
4. validated implementation;
5. non-validated implementation;
6. historical materials.

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

## Architecture Decision Records

Major architectural decisions require ADR records.

ADR records preserve decision history and are not rewritten after acceptance.

## Recovery principle

Recovery artifacts are transfer records, not permanent sources of truth.

Current canonical repository state has priority over historical recovery files.

## Documentation rule

No implementation should silently redefine approved product intent.

No documentation should claim validated behavior without validation evidence.

## Current state

Product Concept: APPROVED
Roadmap: APPROVED
Implementation: NOT STARTED

## Current-State Addendum — 2026-09-09

The historical `Current state` block above is retained verbatim because validated regression guards treat prior canonical documentation text as an audit contract. It is superseded for current-state interpretation by the following additive record and by `ROADMAP.md`, `docs/state/CURRENT_PROJECT_STATE.json`, accepted Phase 18 decisions and checkpoints.

- implementation has progressed through Phase 18 P18.0–P18.9 validation;
- Phase 18 architecture is approved and implementation authorized;
- activation workstream A1 concrete Railway/PostgreSQL RLS preflight is `VALIDATED`;
- exact implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- A1 gate: `PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`;
- strategic machine-state synchronization deliberately remains `4.34` at `PHASE_18_P18_9_VALIDATED_ACTIVATION_OWNER_GATE` until a separate formal activation synchronization gate is authorized;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- canonical runtime storage remains `PROJECT_LOCAL_ONLY`;
- `PAID_PROVIDERS = NONE_APPROVED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

Latest A1 evidence checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md`.
