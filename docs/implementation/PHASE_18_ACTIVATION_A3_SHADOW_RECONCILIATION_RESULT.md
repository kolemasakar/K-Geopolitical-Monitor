# Phase 18 Activation A3 — Shadow / Reconciliation / Canary Result

Date: 2026-09-09
Target gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`
Status: `VALIDATED / MERGE_PENDING`

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

## Accepted Pre-Merge Evidence

PR #55 initial evidence head: `1c5f9bd3e161dda52cbae8fcc1fda9ef4441a23f`.

A3 workflow run `34379541994`:

- shadow-reconciliation job `102560691267`: PASS;
- live-noncanonical-canary job `102560691011`: PASS;
- PostgreSQL version: 16.15;
- exact reconciliation: PASS;
- retry/idempotency: PASS;
- outbox persistence: PASS;
- tenant isolation: PASS;
- read-only observation: PASS;
- deliberate mismatch classes: `ROW_COUNT`, `TABLE_CONTENT`, `SEMANTIC_PROJECTION`;
- mismatch count/budget behavior: `3 > 2`, fail-closed as required;
- ephemeral cleanup: PASS.

Full PR regression run `34379541997`, job `102560691416`:

- Ubuntu 24.04.5;
- Python 3.11.16 x64;
- `1164 passed in 98.42s`;
- conclusion: SUCCESS.

The documentation commit that records this evidence must itself receive fresh PR
CI before guarded merge. Post-merge exact-main evidence is recorded only after
the canonical merge SHA exists.

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

- owner-local runtime remains canonical;
- PostgreSQL shadow remains synthetic, disposable and non-canonical;
- canary stages remain read-only: `1% -> 5% -> 25% -> 100%` observation design;
- automatic promotion is forbidden;
- canonical cutover is unauthorized;
- shared-runtime activation remains `NO`;
- production/live remains `NOT_OPERATIONAL`;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid resources remain not authorized during beta;
- existing Railway staged changes must remain untouched;
- strategic machine state remains `4.34` until a separately authorized synchronization gate.
