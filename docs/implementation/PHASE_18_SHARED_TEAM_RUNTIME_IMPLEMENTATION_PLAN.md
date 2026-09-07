# Phase 18 — Shared / Team Runtime Implementation Plan

Status: `IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_READY`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Architecture approval: `PHASE_18_NEW_ARCHITECTURE_APPROVAL = APPROVED_BY_OWNER`
Planning authorization: `PHASE_18_IMPLEMENTATION_PLANNING_AUTHORIZED = YES`
Implementation authorization: `PHASE_18_IMPLEMENTATION_AUTHORIZED = YES`
Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`
Architecture decision: `docs/decisions/PHASE_18_ARCHITECTURE_APPROVAL_GATE_2026-09-07.md`
Implementation authorization decision: `docs/decisions/PHASE_18_IMPLEMENTATION_AUTHORIZATION_GATE_2026-09-07.md`
Architecture preflight: `docs/implementation/PHASE_18_SHARED_TEAM_RUNTIME_ARCHITECTURE_PREFLIGHT.md`

## 1. Purpose

This document converts the owner-approved Phase 18 architecture into an implementation sequence with explicit validation gates.

The plan itself did not authorize implementation. A separate explicit owner decision on 2026-09-07 subsequently set `PHASE_18_IMPLEMENTATION_AUTHORIZED = YES`. P18.0 and P18.1 have since been implemented and validated. P18.2 is now the next permitted engineering step, but shared-runtime activation, canonical cutover, paid providers and production/live operation remain separately gated.

The active canonical runtime remains:

- `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite;
- mixed/shared canonical runtime `BLOCKED`;
- production/live `NOT_OPERATIONAL`;
- paid providers `NONE_APPROVED`;
- migration `033` `NOT_CREATED / NOT_PREAUTHORIZED`.

## 2. Recorded Implementation Authorization

The explicit owner decision has set:

`PHASE_18_IMPLEMENTATION_AUTHORIZED = YES`

This authorizes sequential P18.x engineering work subject to each subphase's prerequisites and validation gate.

Implementation authorization does **not** by itself authorize:

- shared-runtime activation;
- canonical cutover;
- production/live transition;
- public/shared ingress activation;
- paid provider purchase, spending or provider activation;
- migration `033` creation or execution merely because implementation is authorized;
- destructive conversion of the owner-only project-local SQLite store;
- direct cross-project canonical-store mutation;
- bypass of any P18.x validation, migration, security, DR, provider or activation gate.

The recorded decision is:

`docs/decisions/PHASE_18_IMPLEMENTATION_AUTHORIZATION_GATE_2026-09-07.md`

P18.0 is formally validated at `P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED`; P18.1 is formally validated at `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`; P18.2 is `READY_TO_BEGIN`.

## 3. Engineering Principles

Every Phase 18 implementation step must preserve these invariants:

- the validated owner-only SQLite runtime remains independently operable and rollback-capable;
- shared runtime is a separate profile, never a shared-filesystem extension of the current SQLite store;
- `workspace_id` is the primary tenancy/security boundary and `project_id` is the canonical project boundary inside a workspace;
- authorization is deny-by-default;
- authentication and authorization remain separate concerns;
- owner-only roadmap decisions remain owner-only even when an `ADMIN` role exists;
- direct cross-project canonical-store mutation remains forbidden;
- externally retried writes are idempotent where duplicate execution matters;
- conflicting writes use explicit concurrency semantics rather than silent unsafe last-write-wins;
- externally delivered side effects use a transactional outbox or equivalent durable handoff;
- audit state, delivery state and publication state never become factual-verification authority;
- canonical factual verification remains P13.5/P13.6;
- provider selection and spending remain separate owner decisions;
- shared-runtime activation remains a separate final owner decision.

## 4. Planned Phase 18 Sequence

Validation requires evidence; implementation alone is never enough.

### P18.0 — Shared Runtime Contract Foundation and Test Harness

State: `VALIDATED`
Gate: `P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED`
Implementation anchor: `6a932c1572fc8136a372bbef35be926adf5248fd`
Result: `docs/implementation/P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED.md`

Validated scope:

- provider-neutral shared-runtime interfaces and configuration boundaries;
- explicit owner-local versus shared-team profile selection without changing the default owner-only profile;
- tenant-context value objects/contracts with mandatory `workspace_id` and `project_id` semantics;
- negative test harnesses for absent/ambiguous tenant context;
- test fixtures for multiple workspaces/projects without external provider dependencies;
- shared runtime disabled by default;
- shared-profile binding cannot use project-local SQLite.

Validation evidence:

- x64 run `34118505375`, job `101730823343`: `749 passed in 117.36s / SUCCESS`;
- native ARM64 run `34118505353`, job `101730823137`: native `aarch64`, `749 passed in 111.25s / SUCCESS`, bootstrap/unattended/systemd PASS.

### P18.1 — Identity and Authenticated Tenant Context Foundation

State: `VALIDATED`
Gate: `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`
Implementation anchor: `01abc4f6be77c856e24497ad77c58ab052bb89e2`
Result: `docs/implementation/P18_1_IDENTITY_TENANT_CONTEXT_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED.md`

Validated scope:

- provider-neutral identity-validation adapter contract;
- explicit human/service identity and credential separation;
- short-lived temporal validation with mandatory fail-closed revocation status;
- server-side workspace/project membership resolution;
- authenticated tenant context derived only after identity, temporal, revocation and membership checks;
- forged, unauthorized and ambiguous tenant scope rejected;
- service identities cannot satisfy human/owner authority requirements;
- no concrete external identity provider selected.

Validation evidence:

- x64 run `34124491945`, job `101749841571`: `776 passed in 124.31s / SUCCESS`;
- native ARM64 run `34124491899`, job `101749841305`: native `aarch64`, `776 passed in 99.81s / SUCCESS`, bootstrap/unattended/systemd PASS.

### P18.2 — RBAC and Owner-Only Strategic Gate Enforcement

State: `READY_TO_BEGIN`
Gate: `P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED`

Planned roles:

- `OWNER`;
- `ADMIN`;
- `ANALYST`;
- `VIEWER`;
- `SERVICE`.

Scope after implementation authorization:

- permission matrix by action and canonical object family;
- deny-by-default service-layer authorization;
- workspace/project membership enforcement;
- explicit owner-only permissions for irreversible/strategic gates;
- negative authorization tests for every role boundary.

Acceptance:

- `VIEWER` cannot mutate canonical state;
- `ANALYST` cannot perform owner-only strategic actions;
- `ADMIN` cannot bypass owner-only roadmap gates;
- cross-workspace access is denied even with valid object identifiers;
- service identities cannot exceed enumerated scopes.

### P18.3 — Shared Datastore Schema and Migration Contract

State: `PLANNED / NOT_STARTED`
Gate: `P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED`

Scope after implementation authorization:

- design PostgreSQL-compatible transactional schema or demonstrably equivalent relational contract;
- tenant-scope every canonical shared object;
- define referential integrity and tenant-consistency constraints;
- define migration versioning, forward/rollback expectations and schema compatibility rules;
- define row-level security or equivalent database-policy evaluation where appropriate;
- design controlled export/import from owner-only SQLite with provenance and reconciliation.

Migration boundary:

- this plan does **not** allocate, create or preauthorize migration `033`;
- the first Phase 18 migration number/name is chosen only after a separate migration review inside authorized implementation;
- no migration may rewrite the current owner-only SQLite canonical store in place.

Acceptance:

- schema review demonstrates tenant isolation at more than the UI layer;
- cross-tenant foreign-key/ownership inconsistencies fail;
- forward/rollback migration tests exist before migration validation;
- owner-only SQLite remains unchanged and independently restorable.

### P18.4 — Tenant-Scoped Repository, Write, Idempotency and Concurrency Layer

State: `PLANNED / NOT_STARTED`
Gate: `P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED`

Scope after implementation authorization:

- tenant-scoped repositories/services for shared canonical reads and writes;
- mandatory authenticated scope in every shared canonical repository method;
- idempotency keys for retryable commands where duplicate execution matters;
- object version/optimistic concurrency tokens where conflicting edits are unsafe;
- deterministic conflict responses;
- concurrent writer tests.

Acceptance:

- repository methods cannot issue unscoped canonical shared queries;
- duplicate command retries do not duplicate effects;
- conflicting writes are deterministic and observable;
- one workspace cannot read/write another workspace through identifier guessing.

### P18.5 — Audit, Transactional Outbox and Side-Effect Isolation

State: `PLANNED / NOT_STARTED`
Gate: `P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED`

Scope after implementation authorization:

- durable security-sensitive mutation audit records;
- actor, workspace, project, action, object identity/version and correlation metadata;
- transactional outbox or equivalent durable side-effect handoff;
- idempotent delivery consumers;
- strict separation of analytical truth from delivery/publication lifecycle state.

Acceptance:

- canonical transaction and outbox handoff cannot diverge through ordinary process failure;
- audit records are append-only from the application perspective;
- retries do not duplicate external effects;
- delivery/publication receipts cannot promote factual verification.

### P18.6 — Shared Runtime Security and Secrets Controls

State: `PLANNED / NOT_STARTED`
Gate: `P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED`

Scope after implementation authorization:

- HTTPS-only shared application boundary;
- non-public canonical datastore ingress;
- secrets outside source code, canonical analytical rows and public artifacts;
- session/token misuse controls;
- IDOR, injection, SSRF, CSRF-where-applicable and privilege-escalation negative tests;
- rate/resource controls to limit tenant-level abuse;
- security-event audit mapping;
- secret/log/export/backup review.

Acceptance:

- threat-model control matrix has test/evidence mappings;
- datastore is not publicly reachable;
- tenant/private secrets do not appear in logs or public/non-sensitive surfaces;
- privileged operations are deny-by-default and auditable.

### P18.7 — Backup, Disaster Recovery and Rollback

State: `PLANNED / NOT_STARTED`
Gate: `P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED`

Scope after implementation authorization:

- encrypted shared-runtime backups;
- schema/migration version capture;
- tenant-safe restore procedures;
- clean-environment restore drill;
- point-in-time recovery or equivalent where supported;
- rollback from failed shared candidate to unchanged owner-only runtime;
- measured RPO/RTO evidence before any service-level claim.

Acceptance:

- clean-environment restore succeeds;
- restore cannot cross tenant/project ownership boundaries;
- failed shared candidate can be discarded without corrupting owner-only canonical data;
- RPO/RTO values are measured, not inherited from planning assumptions.

### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness

State: `PLANNED / NOT_STARTED`
Gate: `P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`

Scope after implementation authorization:

- provider-neutral non-production shared runtime candidate;
- controlled copy/export with provenance from local canonical source;
- row-count, invariant and semantic reconciliation;
- read-only shadow comparison;
- concurrency, isolation, security and restore evidence;
- provider/cost comparison when external infrastructure is actually needed;
- explicit owner provider approval before any paid-provider commitment;
- canary design without canonical cutover.

Acceptance:

- shadow mismatches are explicit and bounded;
- no automatic promotion/cutover occurs;
- paid providers remain `NONE_APPROVED` unless separately approved;
- current owner-only local store remains canonical.

### P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness

State: `PLANNED / NOT_STARTED`
Gate: `PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`

Scope after implementation authorization and successful P18.0–P18.8:

- full tenancy/RBAC negative matrix;
- migration forward/rollback validation;
- concurrency/idempotency/outbox validation;
- threat-model/security evidence review;
- clean restore and rollback evidence;
- provider/cost approval evidence where applicable;
- x64 full repository regression;
- native ARM64 owner-only regression where that deployment profile remains supported;
- owner-only runtime compatibility verification;
- staged canary evidence if separately authorized.

P18.9 validation means **activation readiness only**.

It must not set:

`PHASE_18_SHARED_RUNTIME_ACTIVE = YES`

Final activation requires a separate explicit owner activation decision after fresh launch-time validation.

## 5. Cross-Cutting Validation Matrix

Every implemented P18.x change must satisfy relevant sections below.

### Tenancy

- explicit `workspace_id` and `project_id` context;
- cross-workspace read denial;
- cross-workspace write denial;
- cross-project direct canonical mutation denial unless a separately approved versioned contract exists;
- absent/ambiguous tenant context fails closed.

### Identity and Authorization

- AuthN and AuthZ separated;
- deny-by-default permission checks;
- human/service identities separated;
- owner-only strategic gates remain owner-only;
- negative role-boundary tests exist.

### Data and Concurrency

- transaction boundaries explicit;
- idempotent retry behavior where required;
- deterministic conflict semantics;
- tenant referential constraints;
- audited security-sensitive writes.

### Security

- HTTPS for shared ingress;
- datastore without public ingress;
- secrets isolated;
- threat controls mapped to evidence;
- logs/exports/backups reviewed for tenant-private leakage.

### Recovery

- encrypted backup design;
- clean restore;
- tenant-safe restore;
- rollback to owner-only profile;
- measured RPO/RTO before claims.

### Regression and Epistemic Boundaries

- owner-only runtime remains valid;
- source/provenance/verification contracts remain green;
- forecast/calibration metrics cannot promote factual verification;
- delivery/publication state cannot promote factual verification;
- no reconstructed backend state is represented as observed state.

## 6. Provider and Cost Decision Boundary

Architecture approval did not select a provider.

The recorded implementation authorization permits provider-neutral code and local/non-production test infrastructure under the approved P18.x sequence, but **does not automatically approve paid infrastructure**.

Before any paid provider or managed external service is activated, a separate owner decision must evaluate:

- monthly fixed cost;
- variable compute/storage/egress cost;
- identity/authentication cost;
- backup retention cost;
- observability/log retention cost;
- regional availability;
- security controls;
- export/exit path and lock-in;
- operational burden and recovery responsibility.

## 7. Migration and Cutover Boundary

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

No migration number is reserved by this plan or by implementation authorization.

Canonical cutover from owner-only SQLite to a shared datastore is not part of implementation authorization alone. It requires:

1. implemented and validated shared candidate;
2. migration/reconciliation evidence;
3. tenant/RBAC/security validation;
4. backup/restore and rollback evidence;
5. shadow/canary evidence where applicable;
6. fresh exact-head regression;
7. explicit owner cutover/activation decision.

Until then, owner-only project-local SQLite remains canonical.

## 8. Current Decision State

`PHASE_18_ARCHITECTURE_PREFLIGHT = COMPLETE`

`PHASE_18_NEW_ARCHITECTURE_APPROVAL = APPROVED_BY_OWNER`

`PHASE_18_IMPLEMENTATION_PLANNING_AUTHORIZED = YES`

`PHASE_18_IMPLEMENTATION_AUTHORIZED = YES`

`P18_0 = VALIDATED`

`P18_1 = READY_TO_BEGIN`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

## 9. Next Engineering Step

The next permitted engineering step is:

`P18.1 — Identity and Authenticated Tenant Context Foundation`

Target validation gate:

`P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`

P18.1 readiness does not select a concrete identity provider, approve paid infrastructure, activate shared runtime, create migration `033`, or authorize production/shared cutover.