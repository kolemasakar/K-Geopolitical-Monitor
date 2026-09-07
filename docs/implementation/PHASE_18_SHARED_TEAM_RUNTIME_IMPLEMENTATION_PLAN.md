# Phase 18 — Shared / Team Runtime Implementation Plan

Status: `IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / P18_5_VALIDATED / P18_6_READY`
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

The plan itself did not authorize implementation. A separate explicit owner decision on 2026-09-07 subsequently set `PHASE_18_IMPLEMENTATION_AUTHORIZED = YES`. P18.0 through P18.5 have since been implemented and validated. P18.6 is now the next permitted engineering step, but shared-runtime activation, canonical cutover, paid providers, migration `033` and production/live operation remain separately gated.

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

P18.0 is formally validated at `P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED`; P18.1 is formally validated at `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`; P18.2 is formally validated at `P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED`; P18.3 is formally validated at `P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED`; P18.4 is formally validated at `P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED`; P18.5 is formally validated at `P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED`; P18.6 is `READY_TO_BEGIN`.

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

State: `VALIDATED`
Gate: `P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED`
Implementation anchor: `eb9e51082320858be14aebafafd4746a16674ec7`
Result: `docs/implementation/P18_2_RBAC_OWNER_GATE_ENFORCEMENT_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED.md`

Validated roles:

- `OWNER`;
- `ADMIN`;
- `ANALYST`;
- `VIEWER`;
- `SERVICE`.

Validated scope:

- provider-neutral permission matrix and deny-by-default authorization;
- server-side workspace/project role bindings;
- `VIEWER` read-only boundary;
- `ANALYST` derived-analysis mutation without canonical-state mutation;
- `ADMIN` canonical/administrative permissions without owner-only strategic authority;
- `SERVICE` with no implicit authority and explicit allowlisted service scopes only;
- owner-only strategic permissions for Phase 14 activation, Phase 17 publication activation, Phase 18 shared-runtime activation, provider approval, canonical cutover and migration authorization;
- authenticated human plus workspace-wide `OWNER` required for owner-only strategic gates;
- cross-workspace/project access, inactive/wrong-principal bindings, escalation and service impersonation fail closed.

Validation evidence:

- x64 run `34131110962`, job `101771189130`: `820 passed in 125.92s / SUCCESS`;
- native ARM64 run `34131110956`, job `101771189222`: native `aarch64`, `820 passed in 173.68s / SUCCESS`, bootstrap/unattended/systemd PASS.

### P18.3 — Shared Datastore Schema and Migration Contract

State: `VALIDATED`
Gate: `P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED`
Implementation anchor: `7cf09298ee385a0ed7d5a5797f3a096f4cd04bf7`
Contract: `docs/implementation/P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT.md`
Result: `docs/implementation/P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED.md`

Validated scope:

- provider-neutral PostgreSQL-compatible transactional relational capability contract without selecting or provisioning a provider;
- mandatory non-null `workspace_id` and `project_id` on modeled shared canonical tables;
- composite primary-key and foreign-key rules that preserve full tenant scope below the UI/request layer;
- fail-closed database-policy/RLS-equivalent scope descriptors using both tenant-key columns;
- representative shared contracts for event, semantic claim, forecast, delivery intent and publication release state;
- explicit logical schema-version advance, forward operations, rollback operations and compatibility rules;
- hard rejection of allocated repository migration numbers, destructive migration semantics and canonical-cutover authorization inside P18.3;
- provenance-bound owner-local SQLite export manifest with source database SHA-256, row counts and per-table checksums;
- import reconciliation that can establish shadow-readiness only and never authorizes canonical cutover.

Validation evidence:

- x64 run `34141047205`, job `101802889133`: `858 passed in 111.18s / SUCCESS`;
- native ARM64 run `34141047066`, job `101802888555`: native `aarch64`, `858 passed in 95.67s / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration boundary:

- P18.3 allocated no repository migration number;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- no migration may rewrite the current owner-only SQLite canonical store in place;
- no datastore, provider, DDL execution or canonical cutover was activated by P18.3.

### P18.4 — Tenant-Scoped Repository, Write, Idempotency and Concurrency Layer

State: `VALIDATED`
Gate: `P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED`
Implementation anchor: `17888993263b1ae7ceda65cd46e7540f1ff17add`
Contract: `docs/implementation/P18_4_TENANT_REPOSITORY_CONCURRENCY_CONTRACT.md`
Result: `docs/implementation/P18_4_TENANT_REPOSITORY_CONCURRENCY_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED.md`

Validated scope:

- every shared canonical repository read/write requires authenticated principal, explicit `TenantContext` and server-side RBAC resolution;
- stored object keys include `workspace_id` and `project_id`, so object identifiers alone never establish authorization scope;
- retryable writes require tenant-scoped idempotency keys and deterministic SHA-256 command fingerprints;
- command payloads are snapshotted to immutable canonical JSON at command construction, preventing external mutation from changing retry identity or stored payload;
- exact retries replay the original result without duplicating canonical mutation;
- idempotency-key reuse for a different command fails deterministically;
- optimistic concurrency uses explicit expected/current versions and rejects stale writers;
- concurrent writers have deterministic one-winner/conflict semantics;
- identifier guessing cannot cross workspace/project boundaries;
- implementation is a provider-neutral in-memory contract harness only, not a deployed shared datastore adapter.

Validation evidence:

- PR #22 final CI run `34144837471`, job `101814489463`: `895 passed in 144.80s / SUCCESS`;
- exact-main x64 run `34145082756`, job `101815247999`: `895 passed in 203.00s / SUCCESS`; dependency check PASS;
- exact-main native ARM64 run `34145082744`, job `101815247894`: native `aarch64`, `895 passed in 122.97s / SUCCESS`; dependency check, bootstrap, unattended one-tick and systemd contract PASS.

P18.4 did not deploy shared storage, activate shared runtime, allocate migration `033`, select or purchase a provider, expose shared/public ingress, switch canonical storage, authorize canonical cutover or change production/live status.

### P18.5 — Audit, Transactional Outbox and Side-Effect Isolation

State: `VALIDATED`
Gate: `P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED`
Implementation anchor: `8effa120d76d2a0511dc1cf6a4cbb1b4b22b7f30`
Contract: `docs/implementation/P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_CONTRACT.md`
Result: `docs/implementation/P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED.md`

Validated scope:

- immutable application-append-only audit records for successful security-sensitive canonical mutations, bound to authenticated actor, tenant context, action, object/version, command fingerprint and correlation/request metadata;
- atomic contract boundary for canonical mutation, tenant-scoped idempotency receipt, retry identity, audit record and optional transactional outbox message;
- fail-closed retry identity binding canonical command to actor, audit action and side-effect intent;
- immutable canonical JSON outbox payloads with SHA-256 fingerprints and stable delivery idempotency keys;
- exact tenant-scoped audit/outbox reads and explicit `SERVICE_EXECUTE` authorization for dispatch;
- retry after process loss between external effect and local acknowledgement without duplicate externally visible effect;
- concurrent dispatch deduplication through one stable delivery key;
- delivery/publication audit, outbox and receipt lifecycle evidence remains explicitly truth-neutral.

Validation evidence:

- PR #24 CI run `34149036783`, job `101827182055`: `921 passed in 117.14s / SUCCESS`;
- exact-main x64 run `34149258098`, job `101827861321`: `921 passed in 121.97s / SUCCESS`; dependency check PASS;
- exact-main native ARM64 run `34149258084`, job `101827861052`: native `aarch64`, `921 passed in 111.01s / SUCCESS`; dependency check, bootstrap, unattended one-tick and systemd contract PASS.

P18.5 did not deploy shared storage or a provider/queue, activate shared runtime, allocate migration `033`, select or purchase a provider, expose shared/public ingress, switch canonical storage, authorize canonical cutover or change production/live status.

### P18.6 — Shared Runtime Security and Secrets Controls

State: `READY_TO_BEGIN`
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

`P18_1 = VALIDATED`

`P18_2 = VALIDATED`

`P18_3 = VALIDATED`

`P18_4 = VALIDATED`

`P18_5 = VALIDATED`

`P18_6 = READY_TO_BEGIN`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

## 9. Next Engineering Step

The next permitted engineering step is:

`P18.6 — Shared Runtime Security and Secrets Controls`

Target validation gate:

`P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED`

P18.6 readiness authorizes only the next provider-neutral engineering step. It does not allocate/create/preauthorize migration `033`, select or purchase a provider, deploy shared storage, expose shared/public ingress, activate shared runtime, switch canonical storage or authorize production/shared cutover.
