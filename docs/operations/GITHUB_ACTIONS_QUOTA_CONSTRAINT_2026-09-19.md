# GitHub Actions Quota Constraint — 2026-09-19

Status: `ACTIVE_OPERATIONAL_CONSTRAINT`

The owner reported that the GitHub account has consumed the full included Actions allowance for the current billing cycle:

- included: `2,000 minutes`;
- used: `2,000 minutes`;
- displayed usage: `100%`;
- displayed reset date: `2026-10-01`.

## Temporary project rule

Until Actions capacity is available again, K-Geopolitical Monitor development must avoid creating unnecessary GitHub Actions runs.

Allowed validation path:

- isolated owner-local exact-base worktree;
- native `aarch64` regression on `kgm-e4-owner-pilot`;
- deterministic fixture/integration tests;
- local commit and evidence generation;
- remote preservation only when CI is explicitly skipped.

## Canonical boundary

Owner-local validation does **not** masquerade as GitHub CI.

A pending locally validated change must not be described as canonical CI-validated merely because local tests pass. Normal protected integration evidence remains required before strategic closure unless the owner explicitly establishes a different governance decision.

This constraint does not authorize runtime deployment, service restart, production/live activation, paid/shared resources, migration 033, persistent owner operation, or Plugin publication.
