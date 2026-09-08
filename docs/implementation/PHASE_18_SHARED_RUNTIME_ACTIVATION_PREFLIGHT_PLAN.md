# Phase 18 — Shared Runtime Activation Preflight Plan

Status: `ACTIVATION_PREFLIGHT_AUTHORIZED / A0_VALIDATED / A1_1_ADAPTER_IN_PROGRESS / NOT_ACTIVATED`
Date: 2026-09-08
Project: K-Geopolitical Monitor
Authorization: `docs/decisions/PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZATION_2026-09-08.md`
A0 decision: `docs/decisions/PHASE_18_ACTIVATION_A0_RENDER_DISPOSABLE_PROVIDER_DECISION_2026-09-08.md`
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

State: `IN_PROGRESS / A1_1_POSTGRES_CANDIDATE_ADAPTER`
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

A1.1 adds the concrete disposable PostgreSQL adapter and protected preflight API required before Render resources are created. The adapter is limited to the `kgm_preflight` schema and synthetic probe data, uses forced RLS and transaction-local tenant context, and is not a canonical repository implementation.

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

Current characteristics:

- Hobby workspace: `$0/month + compute`;
- free web service available for disposable validation, with free-tier limitations and idle spin-down;
- smallest paid web compute currently about `$7/month`;
- free Postgres: `256 MB`, `1 GB`, expires after 30 days;
- smallest paid Postgres compute currently about `$6/month` (`0.1c-256mb`), plus storage where applicable;
- same-region services can communicate over Render private networking;
- Render Postgres exposes an internal URL specifically for private-network use;
- automatic TLS/HTTPS is available for public web services;
- paid Postgres instances receive backup/PITR support;
- environment variables/secret files are supported;
- Frankfurt is available for app and Postgres.

Assessment:

- strongest fit for an inexpensive disposable A1/A2 candidate;
- low operational burden;
- cleanest path for observing app-to-database private networking with the current connected toolset;
- free Postgres is **preflight-only**, not a durable launch target because it expires after 30 days;
- a stable smallest paid topology is approximately `$13/month` before storage/egress, and therefore requires separate owner spend approval before use;
- datastore public-access controls must be directly inspected and tested during A2 rather than inferred from provider documentation.

Current A0 disposition:

`APPROVED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT_ONLY`

### Candidate N — Render app + Neon Postgres

Current characteristics:

- Neon Free: `$0`, no time limit, 0.5 GB/project and 100 CU-hours/project monthly;
- Launch is usage-based, typical low-load spend around `$15/month`;
- Private Networking/IP Allow rules are on Neon Scale; Free/Launch traffic normally uses the public network path;
- Scale private networking is AWS PrivateLink based.

Assessment:

- attractive database economics and branching;
- does not satisfy the project's strict non-public datastore-path preference on Free/Launch without upgrading to a private-network-capable tier;
- split-provider topology increases security, egress and operational complexity.

Current A0 disposition:

`NOT_PREFERRED_FOR_INITIAL_PREFLIGHT`.

### Candidate O — OCI Ampere A1 self-managed API + PostgreSQL

Topology:

`Internet client -> HTTPS reverse proxy/API on OCI VM -> local/private PostgreSQL on same VM or private VCN`

Current characteristics:

- current Oracle Always Free documentation provides the equivalent of up to `2 OCPU / 12 GB RAM` for A1 within the revised monthly allowance;
- full control over firewall, TLS, database listen addresses and backup design;
- potentially `$0/month` within Always Free limits;
- materially higher patching, database, backup/PITR, monitoring and recovery burden;
- recent 2026 Always Free allocation changes increase capacity/operational uncertainty.

Assessment:

- best raw cost/control option;
- weaker fit for rapid activation evidence because the project would need to own more security and DR implementation itself;
- useful fallback if managed-provider cost or public-datastore constraints become unacceptable.

Current A0 disposition:

`SECONDARY / COST-OPTIMIZED FALLBACK`.

### Candidate W — Railway app + PostgreSQL

Current characteristics:

- database services are private by default and public access is optional;
- private networking is supported;
- Free plan starts with a 30-day trial and then a low monthly charge; Hobby has a `$5` minimum usage commitment;
- no current project connector is available in this execution environment.

Assessment:

- technically viable and cost-competitive;
- weaker operational fit for this activation pass because current connected tooling cannot directly create/inspect the candidate.

Current A0 disposition:

`VIABLE_ALTERNATE / NOT_PREFERRED_FOR_AUTOMATED_PREFLIGHT`.

## 5. A0 Decision and A1 Target

Approved initial launch-preflight candidate:

`RENDER_FRANKFURT_DISPOSABLE_NONPROD`

Owner-confirmed Render workspace:

`My Workspace`

Approved first resources after green exact-head A1.1 adapter validation:

- one **free** Render Postgres instance in Frankfurt, used only for disposable validation;
- one **free** Render FastAPI web service in Frankfurt with auto-deploy disabled during initial configuration/review;
- app database connection via Render internal/private URL only;
- no canonical data copy;
- synthetic test tenant/project data only;
- no migration `033`;
- no paid plan upgrade;
- no production/live claim.

The purpose of the free candidate is to observe network/security/integration behavior. It is not a production recommendation.

If A1/A2 succeed, the later stable-cost decision should compare at minimum:

- Render smallest paid app + paid Postgres;
- OCI Always Free/self-managed option;
- Railway Hobby/usage-based option;
- any additional provider only if it materially improves private networking, PITR, cost or operational risk.

## 6. A1 Current Blocker

The owner explicitly confirmed Render workspace `My Workspace`, and workspace inventory was inspected. No existing non-KGM resource is authorized for reuse or mutation.

The repository then showed that P18.3/P18.4 remained provider-neutral in-memory contracts without a concrete PostgreSQL adapter. Creating a database before implementing that adapter would not produce a meaningful application candidate.

Therefore:

`RENDER_WORKSPACE_SELECTION = OWNER_CONFIRMED_MY_WORKSPACE`

`A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_IN_PROGRESS`

`A1_RESOURCE_CREATION = BLOCKED_UNTIL_GREEN_EXACT_HEAD_ADAPTER_CI`

No KGM Render service or KGM Render PostgreSQL database has been created yet.

## 7. Current State

`PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZED = YES`

`A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`

`A0_PROVIDER = RENDER`

`A0_REGION = FRANKFURT`

`A0_RECOMMENDATION = RENDER_FRANKFURT_DISPOSABLE_NONPROD`

`RENDER_WORKSPACE_SELECTION = OWNER_CONFIRMED_MY_WORKSPACE`

`A1 = IN_PROGRESS`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_IN_PROGRESS`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`P18_9_LAUNCH_ELIGIBLE = FALSE`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`
