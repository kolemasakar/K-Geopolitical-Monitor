# Phase 18 Activation A3 — Shadow / Reconciliation / Canary Result

Date: 2026-09-09
Target gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`
Status: `VALIDATED / CLOSED`
Implementation closure SHA: `496c43367a96a73839bb58ac26b1d12729f7fac4`

## Scope

A3 converts the earlier provider-neutral P18.8 readiness contract into bounded
non-production evidence without changing canonical authority.

Validation is split deliberately:

- deterministic synthetic owner-local SQLite -> disposable PostgreSQL 16 shadow;
- credential-free live Railway non-canonical health canary.

The PostgreSQL proof validates exact reconciliation, retry/idempotency, outbox
persistence, forced tenant RLS with a NOBYPASSRLS runtime role, read-only shadow
observation, deterministic mismatch classification and a bounded mismatch
threshold. A deliberate three-class analytical mismatch is evaluated against a
budget of two and fails closed.

The Railway canary validates only observable control-plane/runtime health:
`canonical=false`, `production_live=false`, `shared_runtime_active=false`,
`synthetic_data_only=true`, `database_network=railway_private`, startup RLS PASS,
and zero alternate-tenant visibility.

## Accepted PR Evidence

PR #55 final head: `2f449a09b0484ea4c7a9ff3bf46a1d1eb7003625`.

Final-head A3 workflow run `34380601564`:

- shadow-reconciliation job `102564223817`: PASS;
- live-noncanonical-canary job `102564224517`: PASS.

Final-head full regression run `34380601640`, job `102564224089`:

- Ubuntu 24.04.4;
- Python 3.11.16 x64;
- `1164 passed in 119.47s`;
- conclusion: SUCCESS.

A2.2 and A2.3 final-head guards also completed successfully before merge.

## Canonical Merge and Exact-Main Evidence

PR #55 was guarded-merged using expected head
`2f449a09b0484ea4c7a9ff3bf46a1d1eb7003625`.

Canonical implementation closure SHA:
`496c43367a96a73839bb58ac26b1d12729f7fac4`.

The merge commit is GitHub-verified.

A concurrent docs-only PR #56 landed immediately before the guarded merge. Its
only changed path was `docs/ops/KGM_TAILSCALE_ANSIBLE_CONTROL_PLANE.md`; GitHub
preserved it as the first parent of the A3 merge and no A3 implementation path
was overwritten or conflicted.

Exact-main A3 workflow run `34381042333`:

- live-noncanonical-canary job `102565674500`: SUCCESS;
- shadow-reconciliation job `102565675011`: SUCCESS.

Exact-main x64 CI run `34381042340`, job `102565674820`:

- exact checkout: `496c43367a96a73839bb58ac26b1d12729f7fac4`;
- Ubuntu 24.04.4;
- Python 3.11.16 x64;
- `1164 passed in 118.07s`;
- SUCCESS.

Exact-main native ARM64 run `34381042372`, job `102565674719`:

- exact checkout: `496c43367a96a73839bb58ac26b1d12729f7fac4`;
- Ubuntu 24.04.5 ARM image;
- architecture: `aarch64`;
- Python 3.11.16 arm64;
- `1164 passed in 100.93s`;
- bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS (`execution_count=0`, `recovered_runs=0`);
- systemd unit contract: PASS;
- SUCCESS.

Exact-main A2.3 recovery run `34381042304`:

- logical-recovery job `102565674608`: SUCCESS;
- owner-local-rollback job `102565674779`: SUCCESS.

## PostgreSQL Shadow Evidence

The no-charge disposable PostgreSQL 16.15 proof uses synthetic data only and
validates:

- owner-local SQLite remains source of truth;
- PostgreSQL candidate remains non-canonical;
- exact deterministic reconciliation: PASS;
- retry/idempotency: PASS;
- persistent outbox evidence: PASS;
- forced tenant RLS with NOBYPASSRLS runtime role: PASS;
- cross-tenant isolation: PASS;
- read-only shadow observation: PASS;
- deterministic mismatch classes: `ROW_COUNT`, `TABLE_CONTENT`, `SEMANTIC_PROJECTION`;
- deliberate mismatch count `3` against budget `2`: outside budget / fail-closed PASS;
- ephemeral cleanup: PASS;
- automatic promotion: false;
- canonical cutover authorized: false;
- shared-runtime activation authorized: false;
- production/live: false;
- migration 033 created/authorized: false.

## Explicit Evidence Boundary

`LIVE_RAILWAY_DATA_PLANE_RECONCILIATION = NOT_EVIDENCED`

The available Railway connector does not provide safe command execution inside
the private PostgreSQL service. A3 therefore does not claim direct live
owner-local-to-Railway row reconciliation, retry/outbox mutation, or privileged
DB inspection. Those claims would require a separately available safe execution
path and are not inferred from `/health`.

The live Railway canary specifically observed:

- `A3_LIVE_CANARY_HEALTH=PASS`;
- `A3_LIVE_CANARY_NONCANONICAL=PASS`;
- `A3_LIVE_CANARY_RLS_STARTUP_EVIDENCE=PASS`;
- `A3_LIVE_RAILWAY_DATA_PLANE_RECONCILIATION=NOT_EVIDENCED`.

## Immutable Boundaries

- owner-local runtime remains canonical and independently operable;
- PostgreSQL shadow remains synthetic, disposable and non-canonical;
- canary stages remain read-only: `1% -> 5% -> 25% -> 100%` observation design;
- automatic promotion is forbidden;
- canonical cutover is unauthorized;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- existing Railway staged changes remain untouched;
- strategic machine state remains `4.34` until a separately authorized synchronization gate.

## Next Gate

A3 is formally closed. The next executable activation-readiness stage is A4:

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`

A4 is fresh exact-head launch validation only. It does not activate shared
runtime or authorize canonical cutover.
