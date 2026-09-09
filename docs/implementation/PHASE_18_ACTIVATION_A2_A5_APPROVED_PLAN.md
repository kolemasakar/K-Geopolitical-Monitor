# Phase 18 Activation A2–A5 Approved Plan

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `APPROVED / A2_VALIDATED / A3_VALIDATED_MERGE_PENDING / NOT_ACTIVATED`
Decision: `docs/decisions/PHASE_18_ACTIVATION_STRATEGY_BETA_SINGLE_OWNER_BOUNDARY_2026-09-09.md`
A1 checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md`
Canonical base at approval: `445070a270cfd7a9b926291a02caff2ed06c29ad`

## 1. Strategy

Do not rush activation. Preserve owner-local canonical operation while using free/no-charge non-production infrastructure only to collect evidence that a later shared-runtime cutover would be safe and reversible.

Until beta completion:

- user model: single owner only;
- multi-user/team operation: out of scope;
- paid resources: not considered / not authorized;
- canonical runtime: owner-local;
- production/live: not operational;
- migration `033`: not created / not preauthorized.

## 2. Current Position

- P18.0–P18.9: validated;
- A0 provider/topology preflight decision: completed;
- A1 concrete Railway non-production candidate and live RLS preflight: validated;
- A2.1 network/TLS/exposure: validated;
- A2.2 tenant/RBAC/security negative matrix: validated;
- A2.3 backup/restore/rollback: validated;
- parent A2 gate `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`: validated;
- A3 shadow/reconciliation/canary evidence: validated on PR evidence, guarded merge pending;
- A4 remains next only after A3 canonical closure.

## 3. A2 — Live Security / Network / Recovery Observation

Target gate: `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`

Status: `VALIDATED`.

### A2.1 — Network / TLS / Exposure

Validated directly on the existing disposable candidate:

- public API uses HTTPS/TLS as expected;
- database has no public service domain or public TCP proxy;
- app-to-database path uses private Railway networking;
- unauthorized direct public database reachability is absent;
- only intended API ingress is externally reachable;
- secrets are absent from repo, public artifacts and logs.

Status: `VALIDATED` via `PHASE_18_ACTIVATION_A2_1_NETWORK_TLS_EXPOSURE_VALIDATED`.

Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A2_1_NETWORK_TLS_EXPOSURE_VALIDATED.md`.

### A2.2 — Tenant / RBAC / Security Negative Matrix

Validated negative and isolation behavior, including:

- cross-tenant access rejection;
- authorization boundaries;
- IDOR/SSRF-relevant public-surface negatives;
- injection-style inputs;
- privilege-escalation attempts;
- non-BYPASSRLS runtime-role behavior;
- fail-closed startup/security behavior.

Status: `VALIDATED` via `PHASE_18_ACTIVATION_A2_2_SECURITY_NEGATIVE_MATRIX_VALIDATED`.

Final-head accepted live workflow: run `34374111299`, job `102542430156`.

Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A2_2_SECURITY_NEGATIVE_MATRIX_VALIDATED.md`.

### A2.3 — Backup / Restore / Rollback

Validated the strongest recovery path available without paid-resource activation.

Direct Railway observation established:

- existing PostgreSQL candidate has no persistent Railway volume;
- snapshot backups are not configured;
- PITR is not enabled/available under the observed current boundary;
- observed HOBBY plan effective limit reports `maxBackupsCount = 0`;
- the connector cannot execute `pg_dump/pg_restore` inside the private Postgres container without changing the approved boundary.

No paid upgrade, public DB exposure or provider mutation was used to bypass that limitation.

Equivalent no-charge proof:

- ephemeral PostgreSQL 16.15;
- exact `kgm_preflight` DDL/RLS/runtime-role contract;
- `pg_dump -> pg_restore` into a separate ephemeral database;
- deterministic row/hash comparison;
- RLS/policy/runtime-role verification after restore;
- restored cross-tenant isolation validation;
- full ephemeral cleanup;
- independent owner-local `unattended_runner --once` with SQLite integrity verification.

Status: `VALIDATED` via `PHASE_18_ACTIVATION_A2_3_BACKUP_RESTORE_ROLLBACK_VALIDATED`.

Accepted workflow: run `34376107585`:

- logical-recovery job `102549196019`;
- owner-local-rollback job `102549196325`.

Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A2_3_BACKUP_RESTORE_ROLLBACK_VALIDATED.md`.

Result: `docs/implementation/PHASE_18_ACTIVATION_A2_3_BACKUP_RESTORE_ROLLBACK_RESULT.md`.

The current beta result does not claim production-grade Railway physical snapshot/PITR readiness. If shared PostgreSQL later becomes a post-beta activation candidate, physical backup/PITR must be re-evaluated before canonical cutover.

## 4. A3 — Shadow / Reconciliation / Canary Evidence

Target gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`

Status: `VALIDATED / MERGE_PENDING`.

Validated evidence includes:

- synthetic/non-sensitive owner-local SQLite source only;
- disposable PostgreSQL 16.15 shadow;
- exact deterministic owner-local -> PostgreSQL reconciliation;
- tenant RLS isolation with NOBYPASSRLS runtime role;
- retry/idempotency behavior;
- outbox persistence;
- read-only shadow observation;
- deterministic mismatch classification;
- bounded mismatch threshold with deliberate `3 > 2` fail-closed case;
- read-only canary stages `1% -> 5% -> 25% -> 100%`;
- automatic promotion/cutover disabled;
- live Railway non-canonical health/RLS startup canary.

Accepted initial evidence:

- A3 workflow run `34379541994`;
- shadow-reconciliation job `102560691267`;
- live-noncanonical-canary job `102560691011`;
- full regression run `34379541997`, job `102560691416`;
- `1164 passed in 98.42s`.

Explicit limitation:

`LIVE_RAILWAY_DATA_PLANE_RECONCILIATION = NOT_EVIDENCED`.

This limitation is intentional and bounded: `/health` is not treated as a substitute for direct private PostgreSQL data-plane execution.

Migration `033` remains absent unless separately authorized later and shown to be genuinely required.

## 5. A4 — Fresh Exact-Head Launch Validation

Target gate: `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`

After A3 canonical closure, freeze one launch-candidate SHA and validate:

- full exact-head x64 regression;
- supported native ARM64 regression;
- dependency check;
- bootstrap/unattended/systemd contracts where applicable;
- live candidate health;
- live RLS/security evidence;
- A2 recovery evidence;
- A3 reconciliation/shadow evidence;
- exact provider/topology/cost snapshot;
- rollback path.

A4 may establish `ACTIVATION_READY / NOT_ACTIVATED`. It does not activate shared runtime.

During beta, readiness may remain in this state until beta completion.

## 6. A5 — Explicit Owner Activation / Cutover Decision

Target outcome, only if explicitly approved later: `PHASE_18_SHARED_RUNTIME_ACTIVE = YES`.

A5 is a separate owner decision and must consider at least:

- whether shared runtime is actually needed after beta;
- whether multi-user/team access is needed;
- provider selection and operational burden;
- whether any paid resource is justified after beta;
- migration `033` authorization if required;
- canonical-data migration/cutover plan;
- rollback window and failure criteria;
- long-term backup/PITR and monitoring;
- public/private API exposure.

No A0–A4 success implies A5 authorization.

## 7. Preserved Gates

Until a separate explicit activation decision:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `P18_9_LAUNCH_ELIGIBLE = FALSE` unless a later formal A4 synchronization gate explicitly changes it;
- canonical runtime storage = `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime = `BLOCKED`;
- `MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

## 8. Execution Status Addendum — 2026-09-09

The approved plan above remains authoritative. A2 is complete:

- `A2.1 — Network / TLS / Exposure = VALIDATED`;
- `A2.2 — Tenant / RBAC / Security Negative Matrix = VALIDATED`;
- `A2.3 — Backup / Restore / Rollback = VALIDATED`;
- parent gate `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED = PASS`.

A2.3 accepted recovery evidence:

- run `34376107585`;
- logical recovery job `102549196019`;
- owner-local rollback job `102549196325`;
- PostgreSQL logical restore: PASS;
- restored RLS/role/tenant isolation: PASS;
- ephemeral cleanup: PASS;
- owner-local SQLite integrity and independent startup: PASS.

## 9. A3 Execution Status Addendum — 2026-09-09

A3 validation evidence is complete on PR #55 and is awaiting guarded merge plus post-merge exact-main verification.

- target gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`;
- initial evidence head: `1c5f9bd3e161dda52cbae8fcc1fda9ef4441a23f`;
- A3 workflow run `34379541994`: PASS;
- shadow reconciliation job `102560691267`: PASS;
- live non-canonical canary job `102560691011`: PASS;
- regression run `34379541997`, job `102560691416`: `1164 passed in 98.42s`;
- exact reconciliation: PASS;
- retry/idempotency: PASS;
- outbox persistence: PASS;
- tenant isolation: PASS;
- mismatch threshold `3 > 2`: fail-closed PASS;
- automatic promotion/cutover: disabled;
- live Railway direct data-plane reconciliation: `NOT_EVIDENCED`.

This addendum does not change strategic machine state `4.34`, activate shared runtime, authorize paid resources, create/authorize migration `033`, or accept/apply Railway staged changes.
