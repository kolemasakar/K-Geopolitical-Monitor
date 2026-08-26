# ADR M5 - Shared Infrastructure Boundary

Status: APPROVED
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Context

K-Geopolitical Monitor has implementation baselines through M4 and is starting M5 Operational Intelligence Platform work.

Related repositories contain conceptually overlapping infrastructure and models, but their domain semantics and runtime ownership differ.

The architecture review evaluated fully independent repositories, immediate extraction to a dedicated shared repository, and a hybrid model.

## Decision

Adopt a HYBRID architecture with a mandatory project-local runtime phase for M5.

- Keep project-specific domain models, algorithms and canonical storage in their owning repositories.
- Standardize narrow cross-project contracts before sharing implementations.
- Do not create a dedicated shared runtime repository merely because component names are similar.
- Prohibit implicit mixed storage and direct mutation of another project's canonical store.
- During M5 implementation and validation, all runtime state and persistent test data must remain inside K-Geopolitical Monitor project-local storage.
- No shared runtime database, cross-project canonical-store write, or mixed runtime storage is permitted before the full M5 test cycle completes successfully.
- A successful full M5 test cycle does not automatically enable shared runtime storage; it only permits a new architecture review or ADR amendment.
- Future shared infrastructure extraction requires proven multi-project use, stable semantics, versioned contracts and compatibility tests.

## Full Test Cycle Boundary

For this decision, the full M5 test cycle requires all of the following:

- unit tests for M5 components pass;
- M5 integration tests pass using project-local runtime storage;
- M5 acceptance tests pass;
- the complete repository regression suite passes in CI on the final M5 implementation commit;
- storage-boundary tests confirm that mixed runtime storage and direct external canonical-store writes remain disabled.

Until all checks pass, runtime storage mode is PROJECT_LOCAL_ONLY.

## Consequences

Positive:

- preserves project autonomy and failure isolation;
- prevents premature coupling and cross-project state corruption;
- makes the complete M5 test cycle reproducible against one canonical store;
- allows future reuse only after evidence of stable common requirements.

Tradeoffs:

- some temporary duplication may remain;
- future shared extraction requires explicit migration work;
- cross-project contracts must be versioned and tested;
- shared runtime optimization is intentionally deferred.

## Approval

Owner decision recorded 2026-08-26:

Continue M5 without mixed runtime storage until successful completion of the full test cycle.

This ADR is APPROVED for the M5 project-local implementation and validation period.

Any later introduction of shared runtime storage requires an explicit new approval after the successful full M5 test cycle.
