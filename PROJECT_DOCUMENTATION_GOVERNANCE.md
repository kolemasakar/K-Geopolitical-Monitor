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
