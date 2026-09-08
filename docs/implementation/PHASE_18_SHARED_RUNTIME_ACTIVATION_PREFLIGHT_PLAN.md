# Phase 18 — Shared Runtime Activation Preflight Plan

Status: `ACTIVATION_PREFLIGHT_AUTHORIZED / A0_VALIDATED / A1_BLOCKED_ON_RENDER_FREE_DB_QUOTA / NOT_ACTIVATED`
Date: 2026-09-08
Project: K-Geopolitical Monitor
Authorization: `docs/decisions/PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZATION_2026-09-08.md`
A0 decision: `docs/decisions/PHASE_18_ACTIVATION_A0_RENDER_DISPOSABLE_PROVIDER_DECISION_2026-09-08.md`
Current A1 checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-08_PHASE_18_ACTIVATION_A1_BLOCKED_RENDER_FREE_DB_QUOTA.md`
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

State: `VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`
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

A0 does not create infrastructure unless the provider/workspace/account is explicitly selected.

A0 closure records Render Frankfurt as approved **only** for a new free disposable non-production candidate in the owner-confirmed `My Workspace`. It does not approve any paid Render plan, durable provider selection, production use or A5 activation.

### A1 — Concrete Non-Production Launch Candidate

State: `BLOCKED_ON_RENDER_FREE_DB_QUOTA`
Target gate: `PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED`

Required evidence:

- disposable candidate exists in an explicitly selected account/workspace;
- candidate is non-production;
- no canonical cutover;
- no private/sensitive canonical data;
- shared API and PostgreSQL-compatible datastore are instantiated in the same approved region/topology where appropriate;
- credentials are externalized and not committed;
- database path used by the app is private/non-public or otherwise satisfies the approved non-public ingress control;
- public ingress is HTTPS-only and limited to the candidate API surface;
- candidate can be destroyed without affecting owner-local operation.

A1.1 concrete adapter state:

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED`

The adapter is limited to the `kgm_preflight` schema and synthetic probe data, uses forced RLS and transaction-local tenant context, and is not a canonical repository implementation.

Exact-main validation anchor: `570e710d3e7750c2d7b0f975202f70691c2c84b4`.

- x64 dependency check PASS;
- x64 full regression: `1131 passed`;
- native ARM64: `aarch64`;
- ARM64 dependency check PASS;
- ARM64 full regression: `1131 passed`;
- bootstrap PASS;
- unattended one-tick PASS with `execution_count=0`, `recovered_runs=0`;
- systemd contract PASS.

A dedicated free Frankfurt web-service shell named `kgm-shared-runtime-preflight` was created with auto-deploy disabled and synthetic-only settings. It is not operational. A non-resolving placeholder PostgreSQL DSN intentionally causes startup to fail closed until a dedicated datastore exists. Runtime was pinned to Python `3.11.16`, matching validated CI. Observed failure logs did not expose the bearer secret or database credentials.

Creating the required dedicated free KGM PostgreSQL instance was attempted after exact-main validation. Render rejected the request because the confirmed workspace already contains one active free-tier PostgreSQL database belonging to another project and the workspace cannot have a second active free-tier database.

The existing non-KGM database is excluded from reuse or mutation.

Therefore:

`A1 = BLOCKED_ON_RENDER_FREE_DB_QUOTA`

`RENDER_FREE_DB_QUOTA = EXHAUSTED_BY_EXISTING_NON_KGM_RESOURCE`

`KGM_POSTGRES_CREATED = NO`

`EXISTING_NON_KGM_DATABASE_REUSE = FORBIDDEN`

`PAID_RENDER_DATABASE = NOT_AUTHORIZED`

`PROVIDER_PIVOT = NOT_AUTHORIZED`

The A1 target gate is not satisfied.

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

The failed A1 web-service shell is not sufficient evidence for A2 and must not be treated as an operational shared-runtime endpoint.

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

Current characteristics at A0 research time:

- free web service available for disposable validation, with free-tier limitations and idle spin-down;
- free Postgres intended only for disposable preflight and subject to provider free-tier limits;
- same-region services can communicate over Render private networking;
- Render Postgres exposes an internal URL for private-network use;
- automatic TLS/HTTPS is available for public web services;
- paid Postgres instances provide capabilities unavailable to the disposable free candidate;
- environment variables/secret files are supported;
- Frankfurt is available for app and Postgres.

Assessment:

- strongest fit for an inexpensive disposable A1/A2 candidate;
- low operational burden;
- clean path for observing app-to-database private networking;
- free Postgres is preflight-only, not a durable launch target;
- paid Render use requires separate owner spend approval;
- datastore public-access controls must be directly inspected and tested during A2 rather than inferred.

Current A0 disposition:

`APPROVED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT_ONLY`

Current execution constraint discovered after A0:

`ONE_ACTIVE_FREE_POSTGRES_LIMIT_IN_CONFIRMED_WORKSPACE / QUOTA_ALREADY_OCCUPIED_BY_NON_KGM_RESOURCE`

### Candidate N — Render app + Neon Postgres

Assessment at A0:

- attractive database economics and branching;
- the free/low-cost topology did not satisfy the project's strict non-public datastore-path preference without additional capability;
- split-provider topology increases security, egress and operational complexity.

Current A0 disposition:

`NOT_PREFERRED_FOR_INITIAL_PREFLIGHT`.

### Candidate O — OCI Ampere A1 self-managed API + PostgreSQL

Topology:

`Internet client -> HTTPS reverse proxy/API on OCI VM -> local/private PostgreSQL on same VM or private VCN`

Assessment at A0:

- strong raw cost/control option;
- materially higher patching, database, backup/PITR, monitoring and recovery burden;
- useful fallback only after a separate provider/topology amendment.

Current A0 disposition:

`SECONDARY / COST-OPTIMIZED FALLBACK`.

### Candidate W — Railway app + PostgreSQL

Assessment at A0:

- technically viable;
- weaker operational fit because current connected tooling cannot directly manage the candidate in this execution environment.

Current A0 disposition:

`VIABLE_ALTERNATE / NOT_PREFERRED_FOR_AUTOMATED_PREFLIGHT`.

## 5. Approved A0 Target

Approved initial launch-preflight candidate remains:

`RENDER_FRANKFURT_DISPOSABLE_NONPROD`

Owner-confirmed Render workspace:

`My Workspace`

The A0 authorization remains narrow:

- free resources only;
- dedicated KGM resources only;
- no reuse or mutation of other-project resources;
- no canonical data copy;
- synthetic test tenant/project data only;
- no migration `033`;
- no paid plan upgrade;
- no production/live claim.

The free-database quota blocker does not silently expand A0 authorization.

## 6. A1 Current Blocker

Current factual state:

`RENDER_WORKSPACE_SELECTION = OWNER_CONFIRMED_MY_WORKSPACE`

`A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED`

`A1 = BLOCKED_ON_RENDER_FREE_DB_QUOTA`

`RENDER_FREE_DB_QUOTA = EXHAUSTED_BY_EXISTING_NON_KGM_RESOURCE`

`KGM_WEB_SERVICE_SHELL = CREATED_BUT_NOT_OPERATIONAL`

`KGM_POSTGRES_CREATED = NO`

`EXISTING_NON_KGM_DATABASE_REUSE = FORBIDDEN`

`PAID_RENDER_DATABASE = NOT_AUTHORIZED`

`PROVIDER_PIVOT = NOT_AUTHORIZED`

The required next step is an explicit owner-controlled resolution of the provider/cost constraint. A1 cannot advance by silently reusing another project's database, creating a paid database, or changing providers.

## 7. Current State

`PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZED = YES`

`A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`

`A0_PROVIDER = RENDER`

`A0_REGION = FRANKFURT`

`A0_RECOMMENDATION = RENDER_FRANKFURT_DISPOSABLE_NONPROD`

`RENDER_WORKSPACE_SELECTION = OWNER_CONFIRMED_MY_WORKSPACE`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED`

`A1 = BLOCKED_ON_RENDER_FREE_DB_QUOTA`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`P18_9_LAUNCH_ELIGIBLE = FALSE`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`
