# Phase 18 Activation A2–A5 Approved Plan

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `APPROVED / A2_VALIDATED / A3_VALIDATED / A4_TECHNICAL_PASS_BLOCKED_COST_VERIFICATION_REQUIRED / NOT_ACTIVATED`
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
- A3 shadow/reconciliation/canary evidence: validated and canonically closed;
- A4 fresh exact-head technical evidence: PASS on frozen candidate `44761d58fd0e0421131cda5059bc955c35bafb6f`;
- A4 target gate remains unsatisfied because account-specific Railway no-charge/waiver status is `NOT_OBSERVABLE`;
- current A4 state: `BLOCKED_COST_VERIFICATION_REQUIRED`;
- A5 remains unopened and unauthorized.

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

Final-head accepted live workflow: run `34374111299`, job `102542430156`.

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

Status: `VALIDATED / CLOSED`.

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

Canonical implementation closure:

- PR #55 final head `2f449a09b0484ea4c7a9ff3bf46a1d1eb7003625`;
- guarded merge SHA `496c43367a96a73839bb58ac26b1d12729f7fac4`, GitHub-verified;
- final-head A3 run `34380601564`: PASS;
- final-head regression run `34380601640`, job `102564224089`: `1164 passed in 119.47s`;
- exact-main A3 run `34381042333`: PASS;
- exact-main x64 run `34381042340`, job `102565674820`: `1164 passed in 118.07s`;
- exact-main native ARM64 run `34381042372`, job `102565674719`: `aarch64`, `1164 passed in 100.93s`;
- ARM64 bootstrap/unattended/systemd validation: PASS;
- exact-main A2.3 recovery run `34381042304`: PASS.

A concurrent docs-only PR #56 was safely composed into the A3 merge; it changed only `docs/ops/KGM_TAILSCALE_ANSIBLE_CONTROL_PLANE.md` and did not overlap A3 paths.

Explicit limitation:

`LIVE_RAILWAY_DATA_PLANE_RECONCILIATION = NOT_EVIDENCED`.

This limitation is intentional and bounded: `/health` is not treated as a substitute for direct private PostgreSQL data-plane execution.

Migration `033` remains absent unless separately authorized later and shown to be genuinely required.

## 5. A4 — Fresh Exact-Head Launch Validation

Target gate: `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`

Status: `TECHNICAL_PASS / BLOCKED_COST_VERIFICATION_REQUIRED / NOT_ACTIVATED`.

Frozen launch candidate:

`44761d58fd0e0421131cda5059bc955c35bafb6f`

Technical validation is complete:

- exact frozen-SHA x64 regression: `1164 passed in 289.96s`;
- exact frozen-SHA native ARM64 regression: `aarch64`, `1164 passed in 103.70s`;
- dependency checks: PASS;
- ARM64 bootstrap/unattended/systemd contracts: PASS;
- live candidate health/non-canonical controls: PASS;
- A2 recovery evidence: PASS;
- A3 reconciliation/shadow evidence: PASS;
- owner-local rollback: PASS;
- automatic promotion/cutover: disabled.

Accepted A4 workflow run: `34383486940`:

- frozen x64 job `102573817917`;
- frozen ARM64 job `102573817916`;
- frozen shadow reconciliation job `102573817854`;
- frozen recovery job `102573817601`;
- live candidate controls job `102573817880`;
- readiness gate job `102575682072`.

Final PR-head regression run `34383486586`, job `102573816190`: `1164 passed in 93.74s`.

Cost classification remains fail-closed:

- Railway effective plan tier: `HOBBY`;
- included usage credit: `$5`;
- account-specific subscription fee / waiver / trial / no-charge state: `NOT_OBSERVABLE` through the available read-only integration;
- ordinary Railway Hobby pricing cannot be treated as no-charge without direct account-specific evidence.

Therefore:

- `A4_TECHNICAL_EVIDENCE = PASS`;
- `A4_COST_STATUS = NOT_OBSERVABLE`;
- `A4_GATE = BLOCKED_COST_VERIFICATION_REQUIRED`;
- `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = NOT_SATISFIED`;
- `ACTIVATION_READY = FALSE` under the current beta no-paid-resource policy.

A4 may establish `ACTIVATION_READY / NOT_ACTIVATED` only if the no-charge requirement is independently satisfied. It does not activate shared runtime.

Result: `docs/implementation/PHASE_18_ACTIVATION_A4_LAUNCH_EVIDENCE_RESULT.md`.

Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A4_LAUNCH_EVIDENCE_IN_PROGRESS.md`.

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

## 9. A3 Canonical Closure Addendum — 2026-09-09

A3 is formally closed at `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`.

- PR #55 final head: `2f449a09b0484ea4c7a9ff3bf46a1d1eb7003625`;
- implementation closure SHA: `496c43367a96a73839bb58ac26b1d12729f7fac4`;
- merge commit verification: PASS;
- exact-main x64 regression: `1164 passed in 118.07s`;
- exact-main native ARM64 regression: `1164 passed in 100.93s`;
- exact-main A3 shadow/live-canary workflow: PASS;
- exact-main recovery guard: PASS;
- exact reconciliation: PASS;
- retry/idempotency: PASS;
- outbox persistence: PASS;
- tenant isolation: PASS;
- mismatch threshold `3 > 2`: fail-closed PASS;
- automatic promotion/cutover: disabled;
- live Railway direct data-plane reconciliation: `NOT_EVIDENCED`;
- next executable stage: `A4 — Fresh Exact-Head Launch Validation`.

This addendum does not change strategic machine state `4.34`, activate shared runtime, authorize paid resources, create/authorize migration `033`, or accept/apply Railway staged changes.

## 10. A4 Execution Status Addendum — 2026-09-09

A4 has completed all currently executable technical validation on frozen launch candidate `44761d58fd0e0421131cda5059bc955c35bafb6f`.

- technical evidence: PASS;
- exact frozen-SHA x64: `1164 passed in 289.96s`;
- exact frozen-SHA native ARM64/aarch64: `1164 passed in 103.70s`;
- dependency integrity: PASS;
- bootstrap/unattended/systemd: PASS;
- shadow reconciliation: PASS;
- logical recovery and owner-local rollback: PASS;
- live Railway non-canonical controls: PASS;
- PR-head regression: `1164 passed in 93.74s`;
- cost status: `NOT_OBSERVABLE`;
- gate: `BLOCKED_COST_VERIFICATION_REQUIRED`;
- target gate `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`: NOT SATISFIED.

Initial run `34383326462` encountered a transient third-party Google Chrome APT index hash mismatch before the recovery proof. The A4 disposable-runner harness was hardened without changing runtime code or the frozen candidate; final run `34383486940` then passed recovery.

Direct account-level Railway Billing evidence of an active fee waiver or equivalent no-charge status is required before the A4 cost condition can pass under the beta policy.

This addendum does not change strategic machine state `4.34`, activate shared runtime, authorize cutover or payment, create/authorize migration `033`, or accept/apply Railway staged changes.
