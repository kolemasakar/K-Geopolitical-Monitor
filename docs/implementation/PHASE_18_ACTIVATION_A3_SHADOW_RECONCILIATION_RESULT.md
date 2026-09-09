# Phase 18 Activation A3 — Shadow / Reconciliation / Canary Result

Date: 2026-09-09
Target gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`
Status: `IMPLEMENTATION_CANDIDATE / VALIDATION_PENDING`

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
budget of two and must fail closed.

The Railway canary validates only observable control-plane/runtime health:
`canonical=false`, `production_live=false`, `shared_runtime_active=false`,
`synthetic_data_only=true`, `database_network=railway_private`, startup RLS PASS,
and zero alternate-tenant visibility.

## Explicit Evidence Boundary

`LIVE_RAILWAY_DATA_PLANE_RECONCILIATION = NOT_EVIDENCED`

The available Railway connector does not provide safe command execution inside
the private PostgreSQL service. A3 therefore does not claim direct live
owner-local-to-Railway row reconciliation, retry/outbox mutation, or privileged
DB inspection. Those claims would require a separately available safe execution
path and are not inferred from `/health`.

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
- existing Railway staged changes must remain untouched.

Final workflow/run identifiers and exact-main regression evidence are recorded
in the closure checkpoint after all gates pass.
