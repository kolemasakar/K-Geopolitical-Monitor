# Phase 18 — Shared Runtime Activation Preflight Plan

Status: `ACTIVATION_PREFLIGHT_AUTHORIZED / A0_AMENDED_TO_RAILWAY_FREE_PREFLIGHT / A1_READY_ON_CONNECTION / NOT_ACTIVATED`
Date: 2026-09-08
Project: K-Geopolitical Monitor
Authorization: `docs/decisions/PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZATION_2026-09-08.md`
Original A0 decision: `docs/decisions/PHASE_18_ACTIVATION_A0_RENDER_DISPOSABLE_PROVIDER_DECISION_2026-09-08.md`
Current A0 amendment: `docs/decisions/PHASE_18_ACTIVATION_A0_AMENDMENT_RAILWAY_FREE_PREFLIGHT_2026-09-08.md`
Current checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-08_PHASE_18_ACTIVATION_A0_AMENDED_RAILWAY_A1_READY.md`
Historical Render blocker checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-08_PHASE_18_ACTIVATION_A1_BLOCKED_RENDER_FREE_DB_QUOTA.md`
Readiness gate: `PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`
Readiness closure anchor: `8ce8e78eaf88996f1588b280265fb66ca62479f9`

## 1. Purpose

This workstream converts the provider-neutral Phase 18 readiness contracts into evidence for one concrete, disposable non-production launch candidate before any final activation/cutover decision.

It is deliberately separate from P18.0–P18.9. There is no P18.10.

The workstream remains fail-closed until all required live observations exist.

## 2. Immutable Boundaries

Throughout A0–A4 unless separately and explicitly changed at A5:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `P18_9_LAUNCH_ELIGIBLE = FALSE`;
- owner-only project-local SQLite remains canonical and independently operable;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime remains `BLOCKED`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers remain `NONE_APPROVED` until a separate provider/spend decision;
- production/live remains `NOT_OPERATIONAL`;
- factual verification authority remains P13.5/P13.6;
- no private/sensitive canonical data is copied into an external candidate before a validated data-handling path exists;
- no candidate may auto-promote, auto-cutover or mutate the owner-local canonical store.

## 3. Activation Workstream Gates

### A0 — Provider / Topology / Cost Decision

State: `AMENDED_TO_RAILWAY_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT`
Target gate: `PHASE_18_SHARED_RUNTIME_PROVIDER_TOPOLOGY_DECISION_READY`

Required evidence:

- current provider pricing and free/paid boundaries;
- application and datastore topology;
- private datastore path or equivalent non-public ingress control;
- TLS/HTTPS ingress capability;
- secret-management mechanism;
- backup/PITR capability and limitations;
- region availability and Ukraine-adjacent latency considerations;
- provider lock-in/exit path;
- operational burden;
- no-cost disposable validation option where possible;
- explicit distinction between recommendation, provider approval and spend approval.

The original A0 closure approved Render Frankfurt only for a free disposable candidate. That path was executed far enough to expose a real free-tier PostgreSQL quota blocker. The owner then explicitly selected option `3 — AMEND A0`.

The active A0 selection is now Railway Free/Free-Trial for a **new dedicated disposable KGM non-production candidate only**. This amendment does not approve any paid Railway plan, durable provider selection, production use or A5 activation.

`A0_AMENDMENT = APPROVED`

`A0_PROVIDER = RAILWAY`

`A0_TARGET = RAILWAY_FREE_OR_FREE_TRIAL_DISPOSABLE_NONPROD`

`PROVIDER_PIVOT = AUTHORIZED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT_ONLY`

`PAID_PROVIDERS = NONE_APPROVED`

### A1 — Concrete Non-Production Launch Candidate

State: `READY_TO_RESUME_AFTER_RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY`
Target gate: `PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED`

Required evidence:

- disposable candidate exists in an explicitly selected account/workspace;
- candidate is non-production;
- no canonical cutover;
- no private/sensitive canonical data;
- shared API and PostgreSQL-compatible datastore are instantiated in one approved isolated topology;
- credentials are externalized and not committed;
- database path used by the app is private/non-public or otherwise satisfies the approved non-public ingress control;
- public ingress is HTTPS-only and limited to the candidate API surface;
- candidate can be destroyed without affecting owner-local operation.

A1.1 concrete adapter state:

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED`

The adapter is limited to the `kgm_preflight` schema and synthetic probe data, uses forced RLS and transaction-local tenant context, and is not a canonical repository implementation.

Validated implementation anchor: `570e710d3e7750c2d7b0f975202f70691c2c84b4`.

- x64 dependency check PASS;
- x64 full regression: `1131 passed`;
- native ARM64: `aarch64`;
- ARM64 dependency check PASS;
- ARM64 full regression: `1131 passed`;
- bootstrap PASS;
- unattended one-tick PASS with `execution_count=0`, `recovered_runs=0`;
- systemd contract PASS.

The later factual blocker synchronization at exact main `68b7b0157dcb36e9e8bb1bff4e379b7a52df256c` also passed x64 and native ARM64 with `1133 passed` on each architecture, plus dependency/bootstrap/unattended/systemd checks.

#### Historical Render A1 observation

A dedicated free Frankfurt Render web-service shell named `kgm-shared-runtime-preflight` was created. It never became operational because a non-resolving placeholder PostgreSQL DSN intentionally failed closed. Runtime was pinned to Python `3.11.16`. Observed failure logs did not expose the bearer secret or database credentials.

Creating the required dedicated free KGM Render PostgreSQL instance was rejected because the confirmed Render workspace already contained one active free-tier PostgreSQL database belonging to another project. That unrelated database remains forbidden for KGM reuse or mutation.

`RENDER_WEB_SHELL = HISTORICAL_FAIL_CLOSED_NONOPERATIONAL`

`RENDER_FREE_DB_QUOTA = EXHAUSTED_BY_EXISTING_NON_KGM_RESOURCE`

`EXISTING_NON_KGM_DATABASE_REUSE = FORBIDDEN`

`PAID_RENDER_DATABASE = NOT_AUTHORIZED`

#### Active Railway A1 target

Target topology:

`Internet client -> Railway HTTPS service -> Railway private network -> dedicated KGM PostgreSQL`

Required Railway controls:

- one new Railway project dedicated to KGM preflight;
- Free/Free-Trial only;
- FastAPI and PostgreSQL in the same Railway project/environment;
- PostgreSQL remains private by default;
- no TCP proxy and no public database endpoint;
- app uses private `DATABASE_URL`, never `DATABASE_PUBLIC_URL`;
- only the FastAPI service receives a public HTTPS domain;
- bearer/database credentials are service variables and never committed;
- synthetic tenant/project identifiers only;
- no owner-local SQLite access;
- no canonical data copy;
- no migration `033`;
- no auto-promotion/cutover.

Before mutation, Railway account/project inventory must be read. Provisioning may proceed only if no paid plan or paid minimum is required.

`RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY = NEXT_EXECUTABLE_GATE`

`PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED = NO`

The A1 target gate remains unsatisfied until the dedicated Railway app and PostgreSQL candidate are directly created and observed.

### A2 — Live Security / Network / Recovery Observation

State: `BLOCKED_ON_A1`
Target gate: `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`

Required direct observations:

- TLS/HTTPS endpoint behavior;
- HTTP-to-HTTPS behavior where applicable;
- database private-path reachability from the app;
- rejection/non-reachability from unauthorized public paths;
- secrets absent from repo, logs, audit payloads and public artifacts;
- tenant/RBAC negative tests against the concrete candidate;
- IDOR/injection/SSRF/privilege-escalation negative matrix against deployed boundaries where applicable;
- backup/recovery capability observed on the concrete provider;
- clean restore exercise or provider-appropriate disposable equivalent;
- rollback to owner-only canonical runtime remains viable.

The failed Render shell is historical evidence only and is not sufficient for A2. No Railway A2 claim exists before A1 creation.

### A3 — Migration / Reconciliation / Shadow / Canary Evidence

State: `BLOCKED_ON_A2`
Target gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`

Required evidence:

- controlled synthetic/non-sensitive dataset or separately authorized export path;
- deterministic reconciliation against owner-local expectations;
- tenant isolation under concrete datastore behavior;
- retry/idempotency/outbox behavior under concrete persistence;
- read-only shadow comparison;
- bounded mismatch policy;
- no automatic promotion/cutover;
- migration `033` remains absent unless separately authorized and genuinely required.

### A4 — Fresh Exact-Head Launch Validation

State: `BLOCKED_ON_A3`
Target gate: `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`

Required evidence:

- fresh exact-head full x64 regression;
- supported native ARM64 regression;
- concrete candidate health/security/recovery/shadow evidence on the exact launch candidate;
- dependency check;
- rollback-path validation;
- exact provider/topology/cost snapshot;
- final launch package states observed vs inferred facts separately;
- `launch_eligible` may become `TRUE` only if every required launch-time condition is directly satisfied.

### A5 — Explicit Owner Activation / Cutover Decision

State: `NOT_AUTHORIZED`
Target gate: `PHASE_18_SHARED_RUNTIME_ACTIVE = YES` only after an explicit owner decision.

A5 must be a separate decision artifact. A0–A4 success does not imply A5 approval.

## 4. A0 Provider / Topology Evaluation

Research date: 2026-09-08.

### Candidate R — Render unified app + Render Postgres

Topology:

`Internet client -> Render HTTPS web service -> Render private network -> Render Postgres`

Assessment:

- technically strong disposable topology;
- low operational burden;
- private app-to-database path available;
- free KGM Postgres creation is currently blocked in the confirmed workspace by the one-active-free-Postgres quota;
- paid Render use requires separate owner spend approval.

Current A0 disposition:

`HISTORICALLY_APPROVED_FREE_PREFLIGHT / CURRENTLY_BLOCKED_BY_FREE_DB_QUOTA`

### Candidate N — Neon Postgres

Assessment:

- attractive free database economics and branching;
- current Neon private-networking/IP-allow capability is associated with higher-tier security capability;
- a free public database endpoint does not fit the strict non-public datastore-path requirement for this preflight.

Current A0 disposition:

`NOT_SELECTED_FOR_STRICT_NONPUBLIC_PREFLIGHT`.

### Candidate S — Supabase Free Postgres

Assessment:

- free PostgreSQL capacity and database network restrictions are available;
- split-provider app/database topology is unnecessary for the first amended candidate;
- no currently connected Supabase management path for autonomous A1 execution;
- Railway offers the cleaner same-project private-network topology.

Current A0 disposition:

`VIABLE_ALTERNATE / NOT_SELECTED`.

### Candidate O — OCI Ampere A1 self-managed API + PostgreSQL

Topology:

`Internet client -> HTTPS reverse proxy/API on OCI VM -> local/private PostgreSQL on same VM or private VCN`

Assessment:

- strong zero-cost and network-control option within Always Free allowances;
- materially higher patching, database, backup/PITR, monitoring and recovery burden;
- retained as fallback if Railway free topology cannot be instantiated without spend.

Current A0 disposition:

`SECONDARY / COST-OPTIMIZED FALLBACK`.

### Candidate W — Railway app + PostgreSQL

Topology:

`Internet client -> Railway HTTPS service -> Railway private network -> Railway PostgreSQL`

Current characteristics:

- Free plan is `$0/month` with a small recurring free usage credit after the initial free trial;
- free trial permits code and database deployment with one-time credits;
- PostgreSQL is private by default; external database access requires explicit public TCP proxy configuration;
- same-project/environment services communicate over isolated Railway private networking;
- private-network traffic is encrypted and not publicly exposed;
- public web services receive Railway-managed HTTPS/SSL capability;
- credentials can remain service variables;
- compute is usage-metered, so the candidate is disposable evidence infrastructure, not a durable production-cost recommendation;
- free-plan region/features are more constrained than paid plans and must be directly observed rather than inferred.

Current A0 disposition:

`SELECTED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT`.

## 5. Approved A0 Target

Active launch-preflight candidate:

`RAILWAY_FREE_OR_FREE_TRIAL_DISPOSABLE_NONPROD`

The A0 authorization is narrow:

- free/no-charge state only;
- dedicated KGM project/resources only;
- no reuse or mutation of other-project resources;
- no canonical data copy;
- synthetic test tenant/project data only;
- PostgreSQL private by default and no public TCP proxy;
- only app HTTPS ingress may be public;
- no migration `033`;
- no paid plan upgrade or paid minimum commitment;
- no production/live claim.

The Render quota blocker does not authorize a paid Render workaround. The Railway amendment does not authorize a paid Railway workaround.

## 6. A1 Current Gate

Current factual state:

`A0_AMENDMENT = APPROVED`

`A0_PROVIDER = RAILWAY`

`A0_TARGET = RAILWAY_FREE_OR_FREE_TRIAL_DISPOSABLE_NONPROD`

`PROVIDER_PIVOT = AUTHORIZED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT_ONLY`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED`

`A1 = READY_TO_RESUME_AFTER_RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY`

`RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY = NEXT_EXECUTABLE_GATE`

`PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED = NO`

`PAID_PROVIDERS = NONE_APPROVED`

The required next action is to connect/authorize the Railway management integration, perform read-only account/project inventory, confirm Free/Free-Trial/no-charge eligibility, and only then create dedicated KGM resources. No paid commitment may be inferred from this amendment.

## 7. Current State

`PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZED = YES`

`A0_AMENDMENT = APPROVED`

`A0_PROVIDER = RAILWAY`

`A0_TARGET = RAILWAY_FREE_OR_FREE_TRIAL_DISPOSABLE_NONPROD`

`PROVIDER_PIVOT = AUTHORIZED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT_ONLY`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED`

`A1 = READY_TO_RESUME_AFTER_RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY`

`PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED = NO`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`P18_9_LAUNCH_ELIGIBLE = FALSE`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`
