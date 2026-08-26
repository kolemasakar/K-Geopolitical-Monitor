# M6 Controlled Pilot Monitoring Plan

Status: ACTIVE
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Goal

Validate the M5 operational baseline under a controlled pilot workload while preserving project-local runtime ownership and explicit source provenance.

M6 is an engineering milestone aligned with ROADMAP Phase 5 - Controlled Pilot Monitoring. Engineering milestone labels and ROADMAP phase numbers remain separate tracking systems.

## Governing Constraints

- Runtime storage mode remains PROJECT_LOCAL_ONLY.
- No shared runtime database or cross-project canonical-store writes.
- No implicit runtime dependency on another project.
- The first controlled pilot baseline uses deterministic project-local source fixtures.
- Production external integrations remain REVIEW_REQUIRED and are not enabled by this milestone.
- Source provenance must remain traceable from operational finding to raw item and source.
- Coverage limitations must be reported explicitly rather than inferred from source count.

## Work Packages

### M6.1 Controlled Source Adapter

Implement:

- project-local JSONL source adapter;
- approved source-class validation;
- source and raw-item persistence;
- project-local input path boundary;
- deterministic watch-query matching.

Gate:

M6_1_CONTROLLED_SOURCE_ADAPTER_VALIDATED

### M6.2 Coverage Contract Reporting

Implement:

- observed source-class reporting;
- required source-class comparison;
- coverage confidence;
- explicit coverage gaps;
- run-to-coverage linkage;
- persistent pilot coverage reports.

Gate:

M6_2_COVERAGE_REPORTING_VALIDATED

### M6.3 Pilot Execution

Validate:

- due-watch execution through the operational runtime;
- source provenance persistence;
- ranked findings with evidence references;
- repeat execution determinism inside cadence windows;
- restart-safe project-local persistence;
- failure isolation inherited from the M5 operational layer.

Gate:

M6_3_CONTROLLED_PILOT_EXECUTION_VALIDATED

### M6.4 Full Regression Gate

Validate:

- M6 acceptance tests;
- M5 regression tests;
- canonical migrations;
- project-local runtime and source boundaries;
- complete repository regression suite in GitHub Actions.

Gate:

M6_CONTROLLED_PILOT_BASELINE_PASS

## External Integration Boundary

M6 baseline does not approve or activate any production external source, API, AI service or cross-project runtime resource.

A live public-source pilot requires an explicit integration record covering purpose, provider, data exchanged, authentication mode, Source of Truth, fallback, failure isolation and approval status.

## Completion Rule

M6 controlled pilot baseline is complete only when all M6.1-M6.4 gates pass and the final repository CI run succeeds.

Completion of M6 does not change the PROJECT_LOCAL_ONLY runtime-storage decision and does not by itself authorize production/live operation.
