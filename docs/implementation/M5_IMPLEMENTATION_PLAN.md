# M5 Operational Intelligence Platform - Implementation Plan

Status: ACTIVE
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Goal

Turn the validated M0-M4 analytical baseline into a controlled project-local operational monitoring platform without introducing mixed runtime storage.

## Governing Constraints

- ADR_M5_SHARED_INFRASTRUCTURE.md is authoritative for runtime storage boundaries.
- Runtime storage mode is PROJECT_LOCAL_ONLY through the complete M5 implementation and test cycle.
- No direct writes to another project's canonical store.
- No shared runtime database.
- No implicit dependency on K_Research_Critic, K-Trader, VoiceBridge or AI_general runtime state.
- External integrations remain contract-bound and are not required for the first M5 baseline.

## M5 Work Packages

### M5.1 Operational Runtime Foundation

Implement:

- project-local runtime storage policy;
- monitoring watch model;
- monitoring run lifecycle;
- SQLite persistence for watches and runs;
- deterministic due-watch selection;
- unit and integration tests;
- storage-boundary regression tests.

Gate:

M5_1_RUNTIME_FOUNDATION_VALIDATED

### M5.2 Monitoring Cycle Orchestration

Implement:

- controlled execution cycle over due watches;
- ingestion/analysis adapter boundaries using project-local contracts;
- run outcome recording;
- failure isolation and retry metadata;
- no external canonical-store writes.

Gate:

M5_2_MONITORING_CYCLE_VALIDATED

### M5.3 Operational Intelligence Output

Implement:

- ranked operational findings;
- monitoring summaries;
- traceable evidence references;
- run-to-output linkage;
- explainability checks.

Gate:

M5_3_OPERATIONAL_OUTPUT_VALIDATED

### M5.4 Controlled Pilot Test Cycle

Validate:

- unit suite;
- integration suite;
- M5 acceptance suite;
- project-local storage isolation;
- restart/recovery behavior;
- deterministic repeat execution;
- full repository regression suite in GitHub Actions.

Gate:

M5_FULL_TEST_CYCLE_PASS

## Storage Boundary Test Requirement

The M5 acceptance suite must prove that runtime database paths outside the configured project-local data directory are rejected by the M5 operational runtime layer.

Generic lower-level database helpers may remain testable with temporary paths, but the M5 operational runtime must enforce the project-local boundary.

## Completion Rule

M5 is not complete and must not be called operational until M5.1-M5.4 gates pass and the final full repository CI run succeeds.

A successful M5_FULL_TEST_CYCLE_PASS does not authorize shared runtime storage. Any such change requires a new explicit architecture approval.
