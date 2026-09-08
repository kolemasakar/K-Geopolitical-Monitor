# Phase 18 Activation A0 — Render Disposable Provider Decision

Status: `APPROVED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`
Date: 2026-09-08
Project: K-Geopolitical Monitor
Parent authorization: `docs/decisions/PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZATION_2026-09-08.md`
Preflight plan: `docs/implementation/PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_PLAN.md`

## Owner Decision Context

The owner authorized continuation of the post-P18.9 activation preflight and then explicitly confirmed the connected Render workspace named `My Workspace` for this workstream.

The confirmed workspace inventory was inspected before any mutation. Existing services and the existing PostgreSQL database belong to other projects and are out of scope. They must not be reused, modified or deleted for K-Geopolitical Monitor.

## A0 Decision

For A1/A2 disposable validation only:

`A0_PROVIDER = RENDER`

`A0_REGION = FRANKFURT`

`A0_TOPOLOGY = FREE_WEB_SERVICE_PLUS_FREE_POSTGRES`

`A0_WORKSPACE = OWNER_CONFIRMED_MY_WORKSPACE`

`A0_GATE = PHASE_18_SHARED_RUNTIME_PROVIDER_TOPOLOGY_DECISION_READY`

`A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`

This approves creation of new, clearly KGM-named **free-tier** disposable resources in the confirmed workspace after the candidate adapter has green exact-head CI.

## Explicitly Authorized A1 Resource Class

- one new KGM-specific free Render PostgreSQL instance in Frankfurt;
- one new KGM-specific free Render Python web service in Frankfurt;
- internal/private Render database connection for the application;
- synthetic/non-sensitive preflight data only;
- externalized provider environment variables;
- candidate may be destroyed without affecting owner-local operation.

## Not Authorized

This decision does **not** authorize:

- any paid Render plan or spend;
- reuse or mutation of existing non-KGM Render resources;
- production/live service status;
- canonical data copy;
- canonical shared-runtime cutover;
- migration `033` creation or execution;
- `P18_9_LAUNCH_ELIGIBLE = TRUE`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = YES`;
- A5 activation/cutover.

A later durable-provider/spend decision remains separate even if the free disposable candidate validates successfully.

## Current Safety State

`PAID_PROVIDERS = NONE_APPROVED`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`P18_9_LAUNCH_ELIGIBLE = FALSE`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

`OWNER_LOCAL_SQLITE = CANONICAL / INDEPENDENT_ROLLBACK_PATH`
