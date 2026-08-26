# Phase 11 Global Operational Coverage Implementation Plan

Status: COMPLETED
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 11 - Global Operational Coverage

## Goal

Implement measurable, durable and reproducible operational coverage contracts and coverage confidence by converging existing M6 source-class coverage, M7 collection health, M10 region/language coverage and M13 reporting surfaces.

No new engineering milestone number is assigned by this plan.

## Architecture Rule

Phase 11 is a coverage measurement layer, not a verification engine, discovery engine or report truth store.

Canonical upstream ownership remains:
- M6 historical pilot source-class coverage;
- M7 live source collection/audit state;
- M8 evidence and verification truth;
- M10 region/language scope/attribution truth;
- M13 report presentation.

Phase 11 may reference and summarize these stores but must not rewrite their truth semantics.

## Mandatory Boundaries

- runtime storage remains PROJECT_LOCAL_ONLY;
- no shared/mixed runtime DB;
- no external coverage provider required;
- no external translation provider approved;
- coverage ratio cannot modify claim verification;
- coverage confidence cannot modify evidence confidence;
- source count is not coverage;
- report count is not coverage;
- graph degree is not coverage;
- forecast count/probability is not coverage;
- a GLOBAL scope key is not a claim of universal coverage;
- unsupported dimensions remain explicit UNMEASURED limitations;
- production/live operational status remains NOT_OPERATIONAL unless separately approved.

## Durable Schema

Implemented migrations:
- `016_global_operational_coverage.sql`;
- `017_source_collection_attempts.sql`.

### `operational_coverage_contracts`

Durable identity for an explicitly declared coverage scope, including scope key, optional watch scope, assessment window and freshness requirement.

### `operational_coverage_requirements`

Normalized required coverage units with deterministic requirement identity and typed dimensions.

Initial measurable dimensions:
- SOURCE_CLASS;
- SOURCE_ID / SOURCE_AVAILABILITY;
- REGION_LANGUAGE;
- FRESHNESS.

Declared dimensions without canonical measurement state evaluate as UNMEASURED.

### `operational_coverage_snapshots`

Immutable reproducible coverage assessment at a specific time/window, preserving aggregate status counts, coverage_ratio, coverage_confidence and limitations.

### `operational_coverage_requirement_results`

Per-requirement explanation, evidence references, measured time and explicit status.

Allowed baseline statuses:
- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE;
- UNKNOWN;
- UNMEASURED.

### `source_collection_attempts`

Per-source collection-attempt identity/state used to distinguish successful zero-item acquisition, failed/unavailable acquisition, stale acquisition and absence of assessment.

## Metric Definitions

### Coverage ratio

`coverage_ratio = satisfied_count / required_count`

A zero-required-unit contract is invalid. UNAVAILABLE, STALE, UNKNOWN and UNMEASURED are not satisfied.

### Coverage confidence

`coverage_confidence = known_assessment_count / required_count`

Known assessment statuses:
- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE.

UNKNOWN and UNMEASURED reduce coverage confidence.

Coverage confidence is confidence in the coverage assessment, not geopolitical factual confidence.

## Measurement Adapters

### M6/M7 source-class adapter

SOURCE_CLASS requirements converge historical source-class coverage and live per-source attempt state without reusing M6 source-class completeness as cross-dimensional confidence.

### M7 source availability adapter

Per-source collection attempts distinguish successful acquisition, unavailable/failed source, unknown/no assessment and stale acquisition. A successful zero-item fetch remains a successful availability attempt.

### M10 region/language adapter

REGION_LANGUAGE requirements use watch-scoped configured requirements and persisted attribution/coverage state. Stale observations remain STALE. Translation attribution remains metadata and never creates source independence.

### Freshness evaluator

Freshness is evaluated from persisted measurement timestamps against the explicit freshness requirement.

## Source Identity Integrity

LiveSourceCollector fails closed when a returned LiveSourceItem source_id, source_name or source_class does not match the declaring adapter. Identity mismatch is rejected before ingestion.

## Phase 11 Engineering Gates

### P11.1 Coverage Contract and Durable Snapshot Foundation

Gate:
`P11_1_COVERAGE_CONTRACT_FOUNDATION_VALIDATED = PASS`

Evidence:
- run `32996565227`;
- `203 passed in 15.48s`.

### P11.2 Source Availability and Identity Integrity

Gate:
`P11_2_SOURCE_AVAILABILITY_VALIDATED = PASS`

Evidence:
- run `32997440380`;
- `210 passed in 16.63s`.

### P11.3 Region, Language, Source-Class and Freshness Convergence

Gate:
`P11_3_DIMENSION_CONVERGENCE_VALIDATED = PASS`

Evidence:
- run `32997961490`;
- `217 passed in 27.46s`.

### P11.4 Coverage Ratio and Coverage Confidence

Gate:
`P11_4_COVERAGE_METRICS_VALIDATED = PASS`

Evidence:
- run `32999092257`;
- `219 passed in 20.55s`.

### P11.5 Historical Query and Reporting Integration

Gate:
`P11_5_COVERAGE_REPORTING_VALIDATED = PASS`

Evidence:
- run `32999835225`;
- `223 passed in 83.96s`.

### P11.6 Isolation and Global-Claim Boundary

Validated:
- Phase 11 does not change M8 verification status/confidence/origin count;
- region/language metadata does not create source independence;
- M11 graph state remains unchanged;
- M12 forecast state remains unchanged;
- M13 report snapshots remain immutable;
- runtime DB remains project-local;
- GLOBAL scope retains explicit gaps and limitations;
- Phase 11 does not set production/live status to OPERATIONAL.

Gate:
`PHASE_11_GLOBAL_OPERATIONAL_COVERAGE_BASELINE_PASS = PASS`

Evidence:
- commit `40dfaa40869a547a3889ab18750676e8b84b4885`;
- run `33000478908`;
- job `98280686810`;
- `226 passed in 17.67s`.

## Reporting Semantics

Phase 11 reporting exposes:
- scope key;
- assessment window;
- freshness requirement;
- required/satisfied counts;
- coverage ratio;
- coverage confidence;
- gaps;
- unavailable requirements;
- stale requirements;
- unknown requirements;
- unmeasured limitations;
- typed evidence references;
- metric definitions.

M13 remains the renderer/presentation layer and existing M13 report tables remain the canonical report store.

## Non-Goals

This baseline does not add:
- universal/global source coverage;
- new global source providers;
- paid data providers;
- automatic translation;
- canonical actor coverage domain;
- canonical storyline truth domain;
- separate country taxonomy;
- shared runtime infrastructure;
- production dashboards;
- production/global OPERATIONAL approval.

## Completion Result

All P11.1-P11.6 gates are green.

`PHASE_11_GLOBAL_OPERATIONAL_COVERAGE_BASELINE_PASS = PASS`

ROADMAP Phase 11 is an engineering BASELINE_VALIDATED capability. The phrase Global Operational Coverage means the system can explicitly define, measure, persist, query and report coverage state; it is not a claim that the entire world is already monitored completely or in real time.
