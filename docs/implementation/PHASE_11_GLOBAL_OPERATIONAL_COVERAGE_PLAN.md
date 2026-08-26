# Phase 11 Global Operational Coverage Implementation Plan

Status: ACTIVE
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
- unsupported dimensions must remain explicit UNMEASURED limitations;
- production/live operational status remains NOT_OPERATIONAL unless separately approved.

## Proposed Durable Schema

Use migration `016_global_operational_coverage.sql` if implementation confirms no existing table can safely hold these contracts.

### `operational_coverage_contracts`

Purpose:
- durable identity for an explicitly declared coverage scope.

Minimum fields:
- coverage_contract_id;
- scope_key;
- name;
- watch_id or explicit project scope;
- assessment_window_seconds;
- freshness_requirement_seconds;
- active;
- created_at;
- updated_at.

Identity must be deterministic for the normalized contract definition or otherwise versioned explicitly. Updating material requirements must never silently rewrite historical assessment meaning.

### `operational_coverage_requirements`

Purpose:
- normalized required coverage units.

Minimum fields:
- requirement_id;
- coverage_contract_id;
- dimension;
- requirement_key;
- required;
- parameters_json;
- created_at.

Initial measurable requirement dimensions should converge existing canonical state rather than invent new domains:

- SOURCE_CLASS;
- SOURCE_ID / SOURCE_AVAILABILITY where an approved source identity exists;
- REGION_LANGUAGE;
- FRESHNESS.

Approved Coverage Contract dimensions that lack canonical measurement state may be declared but must evaluate as UNMEASURED until separately implemented.

### `operational_coverage_snapshots`

Purpose:
- immutable reproducible coverage assessment at a specific time/window.

Minimum fields:
- coverage_snapshot_id;
- coverage_contract_id;
- assessed_at;
- window_start;
- window_end;
- required_count;
- satisfied_count;
- gap_count;
- unavailable_count;
- stale_count;
- unknown_count;
- unmeasured_count;
- coverage_ratio;
- coverage_confidence;
- limitations_json;
- created_at.

### `operational_coverage_requirement_results`

Purpose:
- explain every aggregate number with per-requirement state.

Minimum fields:
- coverage_snapshot_id;
- requirement_id;
- status;
- evidence_refs_json;
- explanation;
- measured_at.

Allowed baseline statuses:

- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE;
- UNKNOWN;
- UNMEASURED.

## Metric Definitions

### Coverage ratio

For an assessment with N required units:

`coverage_ratio = satisfied_count / N`

If N is zero, the contract is invalid rather than automatically 100 percent covered.

UNAVAILABLE, STALE, UNKNOWN and UNMEASURED requirements are not satisfied.

### Coverage confidence

Coverage confidence is confidence in the coverage assessment, not in geopolitical truth.

Baseline deterministic definition:

`coverage_confidence = known_assessment_count / N`

Known assessment statuses:
- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE.

UNKNOWN and UNMEASURED reduce coverage confidence.

This allows high confidence in a poor coverage result and prevents false equivalence between completeness and confidence.

## Measurement Adapters

### M6 source-class adapter

Read existing source/source-class and pilot coverage state to evaluate explicit SOURCE_CLASS requirements.

Do not reuse the old M6 source-class coverage_confidence as cross-dimensional Phase 11 confidence.

### M7 source availability adapter

Use source collection audit state within the assessment window to distinguish:

- successful acquisition;
- unavailable/failed source;
- unknown/no assessment;
- stale prior acquisition.

A zero-item successful source fetch is not automatically equivalent to source failure.

### M10 region/language adapter

Use configured watch requirements and persisted attribution/coverage reports to evaluate REGION_LANGUAGE units.

A region/language unit that is historically observed but outside the freshness window must be STALE rather than SATISFIED.

Translation attribution remains coverage metadata and never creates source independence.

### Freshness evaluator

Evaluate relevant persisted collection/attribution timestamps against the explicit contract freshness requirement.

Freshness status must be reproducible from persisted timestamps only.

## Source Identity Hardening Prerequisite

Before M7 source availability can be accepted as Phase 11 coverage evidence, LiveSourceCollector must fail closed if a returned LiveSourceItem source identity does not match the declaring adapter:

- source_id;
- source_name;
- source_class.

Add regression coverage for adapter/item identity mismatch.

This hardening must not modify the meaning of existing successful M7 collections.

## Phase 11 Engineering Gates

### P11.1 Coverage Contract and Durable Snapshot Foundation

Deliver:
- migration 016;
- deterministic/version-safe contract identity;
- typed requirements;
- immutable assessment snapshots;
- per-requirement result persistence;
- restart/idempotence tests.

Gate:
`P11_1_COVERAGE_CONTRACT_FOUNDATION_VALIDATED`

### P11.2 Source Availability and Identity Integrity

Deliver:
- M7 adapter/item source-identity fail-closed hardening;
- source availability measurement from collection audits;
- COMPLETED/PARTIAL/FAILED history interpreted without hiding individual failures;
- UNKNOWN/UNAVAILABLE/STALE distinction.

Gate:
`P11_2_SOURCE_AVAILABILITY_VALIDATED`

### P11.3 Region, Language, Source-Class and Freshness Convergence

Deliver:
- M6 SOURCE_CLASS adapter;
- M10 REGION_LANGUAGE adapter;
- explicit freshness evaluation;
- no cross-watch leakage;
- explicit UNMEASURED state for unsupported declared dimensions.

Gate:
`P11_3_DIMENSION_CONVERGENCE_VALIDATED`

### P11.4 Coverage Ratio and Coverage Confidence

Deliver:
- deterministic aggregate counts;
- coverage_ratio;
- coverage_confidence as assessment observability;
- gap/unavailable/stale/unknown/unmeasured breakdown;
- no source-count based inflation;
- exact explanation/evidence refs for every requirement result.

Gate:
`P11_4_COVERAGE_METRICS_VALIDATED`

### P11.5 Historical Query and Reporting Integration

Deliver:
- latest snapshot query;
- snapshot history;
- persistent gap/limitation visibility over time;
- M13 COVERAGE_METADATA integration using explicit coverage snapshot references;
- Global/Regional report output that never hides UNKNOWN/UNMEASURED limitations.

Gate:
`P11_5_COVERAGE_REPORTING_VALIDATED`

### P11.6 Isolation and Global-Claim Boundary

Cross-layer regression must prove:

- Phase 11 coverage evaluation does not change M8 verification status/confidence/origin count;
- region/language metadata still cannot create source independence;
- M11 graph state is unchanged;
- M12 forecast state is unchanged;
- M13 report snapshots remain immutable;
- runtime DB remains project-local;
- GLOBAL scope does not suppress explicit gaps or limitations;
- completion of this engineering phase does not automatically set production/live status to OPERATIONAL.

Gate:
`PHASE_11_GLOBAL_OPERATIONAL_COVERAGE_BASELINE_PASS`

## Acceptance Scenarios

At minimum test:

1. all measurable required units satisfied and fresh;
2. one source unavailable while other requirements are measurable;
3. stale region/language observation;
4. unknown source because no collection exists in the assessment window;
5. unsupported actor/storyline dimension remains UNMEASURED;
6. identical contract/snapshot evaluation is deterministic and restart-safe;
7. materially changed contract requirements preserve old snapshot meaning;
8. cross-watch observations cannot satisfy another watch contract;
9. graph/forecast/report quantity cannot increase coverage;
10. coverage evaluation leaves M8 truth unchanged;
11. returned live item with mismatched adapter source identity fails closed;
12. GLOBAL scope with explicit gaps renders those gaps rather than claiming completeness.

## Reporting Semantics

Phase 11 coverage output should expose at least:

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
- explanation of the metric definitions.

M13 remains the renderer/presentation layer.

## Non-Goals

This baseline does not itself add:

- new global source providers;
- paid data providers;
- automatic translation;
- canonical actor coverage domain;
- canonical storyline truth domain;
- a country taxonomy separate from the existing region registry;
- shared runtime infrastructure;
- production dashboards;
- production/global OPERATIONAL approval.

These require separate explicit decisions where needed.

## Completion Rule

Phase 11 may be recorded as an engineering `BASELINE_VALIDATED` only after P11.1-P11.6 are green in the full deterministic regression suite.

Even then, the phrase `Global Operational Coverage` refers to the validated coverage measurement capability, not proof that the system already monitors the entire world with complete real-time source coverage.
