# Phase 18 Activation A2.3 — Backup / Restore / Rollback Result

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `VALIDATED / NO-CHARGE EQUIVALENT RECOVERY PROOF / NOT_ACTIVATED`
Gate: `PHASE_18_ACTIVATION_A2_3_BACKUP_RESTORE_ROLLBACK_VALIDATED`
Parent A2 gate: `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`

## 1. Scope

A2.3 validates the strongest recovery path available during single-owner beta without authorizing paid Railway backup/PITR features, changing canonical data, or activating shared runtime.

The approved beta constraints remain authoritative:

- owner-local runtime remains canonical;
- Railway remains disposable non-production preflight infrastructure;
- paid resources are not considered / not authorized;
- migration `033` remains not created / not preauthorized;
- production/live remains not operational.

## 2. Direct Railway Observation

Existing candidate:

- Railway project: `kgm-shared-runtime-preflight`;
- PostgreSQL service: `kgm-preflight-postgres`;
- service ID: `7710abe9-942c-4e72-9eff-6a6ae26344cd`;
- image: `postgres:16-alpine`;
- active deployment: `773c74da-cfa1-48b6-83ab-a1629b6510bb`;
- deployment status: `SUCCESS`;
- persistent Railway volume attached: `NO`;
- volume mount path: none;
- configured snapshot backups: none;
- PITR: not enabled / not available under the observed current boundary;
- observed workspace plan tier: `HOBBY`;
- observed effective volume backup limit: `maxBackupsCount = 0`.

The Railway connector/agent exposed read-only container file inspection but no arbitrary command execution inside the Postgres container. Therefore a live `pg_dump -> pg_restore` loop against the private-only Railway database could not be executed without changing the approved infrastructure boundary.

This was treated as a tooling/provider-boundary limitation, not as a database recovery failure.

## 3. No-Charge Equivalent Logical Recovery Proof

Because physical snapshot/PITR proof was unavailable without changing the current plan/boundary, A2.3 used the approved equivalent no-charge path.

Workflow:

- run: `34376107585`;
- logical-recovery job: `102549196019`;
- runner: Ubuntu 24.04.5 x64;
- PostgreSQL service container: `postgres:16-alpine`;
- PostgreSQL server/client: 16.15;
- data: synthetic only;
- Railway credentials: not used;
- external/canonical data: not used.

The job executed:

1. ephemeral PostgreSQL source database creation;
2. the exact `kgm_preflight` DDL/RLS/runtime-role contract from project source;
3. deterministic synthetic rows for two tenants;
4. custom-format `pg_dump`;
5. restore into a separate ephemeral database;
6. deterministic source/restore state comparison;
7. RLS/policy/runtime-role verification after restore;
8. cross-tenant visibility validation after restore;
9. transient dump and both ephemeral databases cleanup.

Observed results:

- `A2_3_LOGICAL_DUMP_BYTES = 3866`;
- `A2_3_LOGICAL_DUMP_SHA256 = 186f555983e6c1aead1c1b253b59590560024d28eabaeafd45dbf720d916eea0`;
- `A2_3_SOURCE_ROWS = 3`;
- `A2_3_ROWS_SHA256 = 76e5756c125839229a50dd788bfedbb966ceb1b848ba94cd1269bb8c1a0649b6`;
- `A2_3_RLS_RESTORE = PASS`;
- `A2_3_LOGICAL_RECOVERY_PROOF = PASS`;
- `A2_3_EPHEMERAL_CLEANUP = PASS`.

The restored database preserved:

- table data deterministically;
- `ENABLE ROW LEVEL SECURITY`;
- `FORCE ROW LEVEL SECURITY`;
- `kgm_preflight_tenant_isolation` policy;
- runtime role restrictions including `NOLOGIN`, `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, `NOBYPASSRLS`;
- tenant visibility isolation for both seeded tenants.

## 4. Owner-Local Canonical Rollback Independence

The second A2.3 workflow job validated that the owner-local canonical path remains independently operable without Railway.

Workflow evidence:

- run: `34376107585`;
- owner-local-rollback job: `102549196325`;
- command: `python -m kgeopolitical_monitor.unattended_runner --project-root <ephemeral-local-root> --once`;
- Railway connection: none;
- local database created: `data/kgeopolitical_monitor.db`;
- SQLite tables observed: `75`;
- `PRAGMA integrity_check = ok`;
- `A2_3_OWNER_LOCAL_INTEGRITY = PASS`;
- `A2_3_OWNER_LOCAL_ROLLBACK = PASS`.

This proves that failure or disposal of the Railway candidate does not prevent the owner-local runtime from starting and maintaining its canonical local store.

## 5. Post-Proof Railway Control

After the recovery proof:

- Railway staged changes remained exactly `31`;
- `kgm-preflight-postgres` remained on deployment `773c74da-cfa1-48b6-83ab-a1629b6510bb`, `SUCCESS`;
- `kgm-preflight-api-v3` remained on deployment `52c39935-9e89-4f12-82e3-82345c606426`, `SUCCESS`;
- no Railway redeploy occurred;
- no service/domain/proxy/volume/environment was created;
- no backup or PITR feature was enabled;
- no plan change was performed;
- no secrets were read or exposed.

## 6. A2.3 Decision

A2.3 is accepted as `VALIDATED` because:

- provider backup/PITR limitations were directly observed;
- paid-resource activation was correctly avoided;
- an equivalent no-charge PostgreSQL logical recovery path was executed successfully using the same schema/RLS contract and PostgreSQL major version;
- restore correctness was deterministic;
- cleanup was verified;
- owner-local canonical rollback independence was directly exercised.

The current beta constraint means that this does **not** claim Railway snapshot/PITR production readiness. If a future post-beta activation requires shared PostgreSQL to become canonical, physical backup/PITR capability must be re-evaluated under the then-authorized provider/plan before cutover.

## 7. Parent A2 Gate

With A2.1, A2.2 and A2.3 validated, the parent gate is satisfied:

`PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`

This is a readiness/evidence gate only. It does not activate shared runtime.

Next executable stage:

`A3 — Shadow / Reconciliation / Canary Evidence`

Preserved state:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `P18_9_LAUNCH_ELIGIBLE = FALSE`;
- canonical runtime storage = `PROJECT_LOCAL_ONLY`;
- `MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- strategic machine state remains `4.34` until a later formal synchronization gate.
