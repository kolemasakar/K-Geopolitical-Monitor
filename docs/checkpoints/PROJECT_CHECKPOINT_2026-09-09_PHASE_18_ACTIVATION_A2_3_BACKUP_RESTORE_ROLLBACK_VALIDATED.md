# Project Checkpoint — Phase 18 Activation A2.3 Backup / Restore / Rollback Validated

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `VALIDATED / NO-CHARGE EQUIVALENT RECOVERY PROOF / NOT_ACTIVATED`
Gate: `PHASE_18_ACTIVATION_A2_3_BACKUP_RESTORE_ROLLBACK_VALIDATED`
Parent gate: `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`

## Canonical Context

A2.3 was executed under the approved beta boundary:

- exactly one user: owner;
- owner-local runtime remains canonical;
- Railway remains disposable non-production preflight infrastructure;
- paid resources are not considered / not authorized;
- shared runtime is not active;
- migration `033` is not created / not preauthorized;
- production/live remains not operational.

## Railway Recovery Capability Observation

Direct inspection of `kgm-preflight-postgres` established:

- image: `postgres:16-alpine`;
- service ID: `7710abe9-942c-4e72-9eff-6a6ae26344cd`;
- active deployment: `773c74da-cfa1-48b6-83ab-a1629b6510bb`, `SUCCESS`;
- persistent Railway volume: none;
- snapshot backup configuration: none;
- PITR: not enabled / unavailable under the observed current boundary;
- observed plan tier: `HOBBY`;
- observed effective backup count limit: `maxBackupsCount = 0`.

The available Railway connector could inspect container files but could not execute `pg_dump`, `psql` or `pg_restore` in the private Postgres container. No public DB exposure or paid upgrade was introduced to bypass that boundary.

## Accepted Recovery Evidence

Workflow run: `34376107585`

### Logical recovery job

Job: `102549196019`

- ephemeral PostgreSQL 16-alpine service: healthy;
- PostgreSQL client/server version: 16.15;
- source data: synthetic only;
- exact project preflight DDL/RLS contract applied;
- `pg_dump` custom-format output: `3866` bytes;
- dump SHA-256: `186f555983e6c1aead1c1b253b59590560024d28eabaeafd45dbf720d916eea0`;
- source rows: `3`;
- deterministic rows SHA-256: `76e5756c125839229a50dd788bfedbb966ceb1b848ba94cd1269bb8c1a0649b6`;
- restore data comparison: PASS;
- ENABLE/FORCE RLS after restore: PASS;
- tenant-isolation policy after restore: PASS;
- constrained runtime role after restore: PASS;
- cross-tenant isolation after restore: PASS;
- ephemeral cleanup: PASS.

### Owner-local rollback job

Job: `102549196325`

- owner-local `unattended_runner --once`: PASS;
- local canonical SQLite database created independently of Railway;
- SQLite tables observed: `75`;
- `PRAGMA integrity_check = ok`;
- `A2_3_OWNER_LOCAL_ROLLBACK = PASS`.

## Post-Proof Control

Railway after proof remained unchanged:

- staged changes: `31`;
- PostgreSQL deployment unchanged: `773c74da-cfa1-48b6-83ab-a1629b6510bb`;
- API v3 deployment unchanged: `52c39935-9e89-4f12-82e3-82345c606426`;
- no redeploy;
- no new resources;
- no volume attachment;
- no backup/PITR enablement;
- no plan change;
- no secret exposure.

## Gate Decision

`PHASE_18_ACTIVATION_A2_3_BACKUP_RESTORE_ROLLBACK_VALIDATED = PASS`

Since A2.1, A2.2 and A2.3 are all validated:

`PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED = PASS`

The next executable stage is:

`A3 — Shadow / Reconciliation / Canary Evidence`

This checkpoint does not authorize activation, canonical cutover, paid resources, migration `033`, or production/live operation.

Strategic machine state remains `4.34` pending a later formal synchronization gate.
