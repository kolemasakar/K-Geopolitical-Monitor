# Phase 18 Activation A2–A5 Approved Plan

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `APPROVED / A2_VALIDATED / A3_VALIDATED / A4_VALIDATED / ACTIVATION_READY_NOT_ACTIVATED / A5_DEFERRED`
Decision: `docs/decisions/PHASE_18_ACTIVATION_STRATEGY_BETA_SINGLE_OWNER_BOUNDARY_2026-09-09.md`
Canonical base at approval: `445070a270cfd7a9b926291a02caff2ed06c29ad`
Strategic state sync: `4.34` unchanged

## 1. Binding Strategy

Do not rush activation. Preserve owner-local canonical operation while using free/no-charge disposable non-production infrastructure only to collect evidence that a later shared-runtime cutover would be safe and reversible.

Until beta completion:

- user model: single owner only;
- multi-user/team operation: out of scope;
- paid resources: not considered / not authorized;
- canonical runtime: owner-local;
- production/live: not operational;
- migration `033`: not created / not preauthorized;
- no external candidate auto-promotes to canonical.

Canonical beta token:

`BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`

## 2. Current Roadmap Position

- P18.0–P18.9: `VALIDATED`;
- A0 provider/topology preflight: `COMPLETE`;
- A1 Railway non-production candidate + live RLS preflight: `VALIDATED`;
- A2 live controls: `VALIDATED`;
- A3 shadow/reconciliation/canary: `VALIDATED / CLOSED`;
- A4 fresh exact-head launch evidence: `VALIDATED`;
- current state: `ACTIVATION_READY / NOT_ACTIVATED`;
- A5 explicit owner activation/cutover decision: `DEFERRED / NOT_AUTHORIZED`.

Current roadmap:

```text
P18.0–P18.9 VALIDATED
       ↓
A0 COMPLETE
       ↓
A1 VALIDATED
       ↓
A2 VALIDATED
       ↓
A3 VALIDATED
       ↓
A4 VALIDATED
       ↓
ACTIVATION_READY / NOT_ACTIVATED   ← current position
       ↓
BETA CONTINUES
       ↓
A5 only after a separate explicit owner decision
```

## 3. A2 — Live Security / Network / Recovery Observation

Target gate: `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`

Status: `VALIDATED`.

### A2.1 — Network / TLS / Exposure

Validated directly on the disposable candidate:

- HTTPS/TLS ingress works as intended;
- PostgreSQL has no public service domain/public TCP proxy;
- app-to-database traffic uses Railway private networking;
- only intended API ingress is public;
- secrets are absent from public artifacts/logs.

Gate:

`PHASE_18_ACTIVATION_A2_1_NETWORK_TLS_EXPOSURE_VALIDATED`

### A2.2 — Tenant / RBAC / Security Negative Matrix

Validated:

- cross-tenant access rejection;
- authorization boundaries;
- IDOR/SSRF-relevant public-surface negatives;
- injection-style inputs;
- privilege-escalation attempts;
- non-BYPASSRLS runtime-role behavior;
- fail-closed startup/security behavior.

Gate:

`PHASE_18_ACTIVATION_A2_2_SECURITY_NEGATIVE_MATRIX_VALIDATED`

### A2.3 — Backup / Restore / Rollback

Direct Railway observation established that production-grade physical backup/PITR is not available under the current no-paid-resource boundary. No paid upgrade or public database exposure was used to bypass that limitation.

Equivalent no-charge recovery proof validated:

- ephemeral PostgreSQL 16;
- exact preflight DDL/RLS/runtime-role contract;
- `pg_dump -> pg_restore`;
- deterministic row/hash comparison;
- restored RLS/policy/runtime-role verification;
- restored cross-tenant isolation;
- ephemeral cleanup;
- independent owner-local `unattended_runner --once` and SQLite integrity proof.

Gate:

`PHASE_18_ACTIVATION_A2_3_BACKUP_RESTORE_ROLLBACK_VALIDATED`

Parent A2 gate:

`PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED = PASS`

Physical backup/PITR must be re-evaluated if shared PostgreSQL is ever proposed as post-beta canonical storage.

## 4. A3 — Shadow / Reconciliation / Canary Evidence

Target gate:

`PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`

Status: `VALIDATED / CLOSED`.

Validated evidence includes:

- synthetic/non-sensitive owner-local SQLite source;
- disposable PostgreSQL 16 shadow;
- exact deterministic reconciliation;
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
- merge SHA `496c43367a96a73839bb58ac26b1d12729f7fac4`;
- exact-main x64: `1164 passed in 118.07s`;
- exact-main native ARM64: `1164 passed in 100.93s`;
- exact-main A3 and A2.3 guards: PASS.

Explicit bounded limitation:

`LIVE_RAILWAY_DATA_PLANE_RECONCILIATION = NOT_EVIDENCED`

The limitation is not treated as activation evidence and does not authorize canonical cutover.

## 5. A4 — Fresh Exact-Head Launch Validation

Target gate:

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`

Status: `VALIDATED / ACTIVATION_READY_NOT_ACTIVATED`.

Frozen launch candidate:

`44761d58fd0e0421131cda5059bc955c35bafb6f`

### Technical evidence

Accepted A4 run `34383486940` validated:

- frozen x64: `1164 passed in 289.96s`;
- frozen native ARM64/aarch64: `1164 passed in 103.70s`;
- dependency integrity: PASS;
- ARM64 bootstrap/unattended/systemd: PASS;
- A3 reconciliation/shadow: PASS;
- A2.3 logical recovery: PASS;
- owner-local rollback: PASS;
- live Railway non-canonical controls: PASS.

PR #58 merged the A4 harness/evidence at canonical SHA:

`74e2aeb103ced874a3dd47a0600bf31536802090`

Post-merge evidence confirmed:

- exact-main CI `34384871798` / job `102578501178`: `1164 passed in 113.94s`;
- frozen x64: `1164 passed in 95.73s`;
- frozen ARM64/aarch64: `1164 passed in 92.00s`;
- A3 shadow/live-canary: PASS;
- A2.3 recovery/owner-local rollback: PASS.

### Cost evidence

The automated Railway integration cannot observe account-specific billing/trial state. This limitation remains recorded as:

`A4_AUTOMATED_COST_STATUS = NOT_OBSERVABLE`

It is not treated as a machine-verifiable cost assertion.

The owner then supplied direct Railway `Billing` and `Plans` UI screenshots showing:

- active plan: `Trial Workspace` / `Trial Plan`;
- `$5` free resource usage;
- no payment method on file;
- no billing history found;
- Hobby not active and offered only via `Unlock Hobby plan`;
- approximately `29 days or $4.98 left` at observation time;
- trial deployments shut down when credits run out.

Evidence record:

`docs/evidence/PHASE_18_A4_RAILWAY_TRIAL_NO_CHARGE_EVIDENCE_2026-09-09.md`

Point-in-time cost determination:

`A4_COST_STATUS = NO_CHARGE_VERIFIED`

Therefore:

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = PASS`

`ACTIVATION_READY / NOT_ACTIVATED`

### Time-bounded validity

The no-charge determination is valid only while the observed Trial Workspace remains active and free trial capacity remains available.

Before any later A5 activation decision, cost status must be revalidated if:

- the trial expires;
- credits are exhausted;
- Railway changes the active plan;
- a payment method is added;
- paid resources are proposed;
- provider pricing/account status changes.

A4 validation does not create a permanent entitlement to Railway resources and cannot be reused as future paid-resource authorization.

Result:

`docs/implementation/PHASE_18_ACTIVATION_A4_LAUNCH_EVIDENCE_RESULT.md`

Validated checkpoint:

`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A4_LAUNCH_EVIDENCE_VALIDATED.md`

## 6. A5 — Explicit Owner Activation / Cutover Decision

Target outcome, only if explicitly approved later:

`PHASE_18_SHARED_RUNTIME_ACTIVE = YES`

Status:

`DEFERRED / NOT_AUTHORIZED`

A5 is a separate owner decision and must re-evaluate at least:

- whether shared runtime is actually needed after beta;
- whether multi-user/team access is needed;
- provider selection and operational burden;
- current provider cost/no-charge status;
- whether paid resources are justified after beta;
- migration `033` authorization if required;
- canonical-data migration/cutover plan;
- rollback window and failure criteria;
- long-term backup/PITR and monitoring;
- public/private API exposure.

No A0–A4 success implies A5 authorization.

## 7. Preserved Gates

Until a separate explicit A5 activation decision:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- owner-local runtime remains canonical;
- canonical storage remains `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime remains blocked;
- `CANONICAL_CUTOVER_AUTHORIZED = NO`;
- `MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- strategic machine state remains `4.34` until its separately defined synchronization gate.

## 8. Current Decision State

A4 has established readiness evidence only.

Current authoritative state:

`ACTIVATION_READY / NOT_ACTIVATED`

Beta continues with owner-local canonical authority. A5 may be considered only later and only through an explicit owner-approved activation/cutover decision.
