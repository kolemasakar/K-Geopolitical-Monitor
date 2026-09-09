# Project Checkpoint — Phase 18 Activation A3 Shadow / Reconciliation / Canary Evidence

Date: 2026-09-09
Project: K-Geopolitical Monitor
Gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`
Status: `VALIDATED / CLOSED`
Strategic state sync: `4.34` unchanged
Implementation closure SHA: `496c43367a96a73839bb58ac26b1d12729f7fac4`

## Scope

A3 validates bounded non-production shadow/reconciliation/canary evidence while
preserving owner-local canonical authority and all beta restrictions.

## Final PR Evidence

PR #55 final head:
`2f449a09b0484ea4c7a9ff3bf46a1d1eb7003625`.

Final-head A3 run `34380601564`:

- shadow-reconciliation job `102564223817`: SUCCESS;
- live-noncanonical-canary job `102564224517`: SUCCESS.

Final-head full regression run `34380601640`, job `102564224089`:

- Ubuntu 24.04.4;
- Python 3.11.16 x64;
- `1164 passed in 119.47s`;
- SUCCESS.

PR #55 was then guarded-merged using the exact final head SHA.

## Canonical Closure Evidence

Canonical implementation closure SHA:
`496c43367a96a73839bb58ac26b1d12729f7fac4`.

The merge commit is GitHub-verified.

A concurrent docs-only PR #56 changed only
`docs/ops/KGM_TAILSCALE_ANSIBLE_CONTROL_PLANE.md` and was preserved as the first
parent of the A3 merge. No A3 path was overwritten or conflicted.

Exact-main A3 run `34381042333`:

- live-noncanonical-canary job `102565674500`: SUCCESS;
- shadow-reconciliation job `102565675011`: SUCCESS.

Exact-main x64 CI run `34381042340`, job `102565674820`:

- exact SHA: `496c43367a96a73839bb58ac26b1d12729f7fac4`;
- Ubuntu 24.04.4;
- Python 3.11.16 x64;
- `1164 passed in 118.07s`;
- SUCCESS.

Exact-main native ARM64 run `34381042372`, job `102565674719`:

- exact SHA: `496c43367a96a73839bb58ac26b1d12729f7fac4`;
- Ubuntu 24.04.5 ARM image;
- architecture: `aarch64`;
- Python 3.11.16 arm64;
- `1164 passed in 100.93s`;
- bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS (`execution_count=0`, `recovered_runs=0`);
- systemd unit contract: PASS;
- SUCCESS.

Exact-main recovery guard run `34381042304`:

- logical-recovery job `102565674608`: SUCCESS;
- owner-local-rollback job `102565674779`: SUCCESS.

## PostgreSQL Shadow Evidence

The no-charge disposable PostgreSQL 16.15 proof used synthetic data only and
validated:

- owner-local SQLite remains source of truth;
- PostgreSQL candidate remains non-canonical;
- exact deterministic reconciliation: PASS;
- retry/idempotency: PASS;
- persistent outbox evidence: PASS;
- forced RLS and NOBYPASSRLS runtime role: PASS;
- cross-tenant isolation: PASS;
- read-only shadow observation: PASS;
- deterministic mismatch classes: `ROW_COUNT`, `TABLE_CONTENT`, `SEMANTIC_PROJECTION`;
- deliberate mismatch count `3` against budget `2`: outside budget / fail-closed PASS;
- automatic promotion: false;
- canonical cutover authorized: false;
- shared-runtime activation authorized: false;
- production/live: false;
- migration 033 created/authorized: false;
- ephemeral cleanup: PASS.

## Live Railway Canary Evidence

Credential-free external observation returned:

- `A3_LIVE_CANARY_HEALTH=PASS`;
- `A3_LIVE_CANARY_NONCANONICAL=PASS`;
- `A3_LIVE_CANARY_RLS_STARTUP_EVIDENCE=PASS`;
- `A3_LIVE_RAILWAY_DATA_PLANE_RECONCILIATION=NOT_EVIDENCED`.

The canary confirms the existing disposable candidate remains healthy,
non-canonical, non-production, synthetic-only, on `railway_private`, with startup
RLS isolation evidence and zero alternate-tenant visibility.

## Explicit Evidence Boundary

`LIVE_RAILWAY_DATA_PLANE_RECONCILIATION = NOT_EVIDENCED`

No direct private Railway PostgreSQL command execution was available through the
current connector boundary. A3 therefore does not infer direct row-level live
Railway reconciliation, outbox mutation, retry persistence or privileged database
inspection from `/health`.

This bounded limitation does not invalidate the A3 gate because the approved beta
strategy requires no-charge non-production readiness evidence, not canonical
cutover, and the deterministic PostgreSQL data-plane proof is separately real and
reproducible on an ephemeral PostgreSQL service.

## Immutable Boundaries

- owner-local runtime remains canonical and independently operable;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- canary stages are read-only `1% -> 5% -> 25% -> 100%` observation design;
- automatic promotion/cutover remains forbidden;
- existing Railway staged changes remain untouched;
- strategic machine state remains `4.34`.

## Next Gate

A3 is formally closed. A4 is `READY_TO_BEGIN` at:

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`

A4 is a fresh launch-candidate validation gate only and does not authorize shared
runtime activation.
