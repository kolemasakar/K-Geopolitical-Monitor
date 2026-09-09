# Project Checkpoint — Phase 18 Activation A2.2 Security Negative Matrix Validated

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `VALIDATED / NON-PRODUCTION PREFLIGHT / NOT_ACTIVATED`
Gate: `PHASE_18_ACTIVATION_A2_2_SECURITY_NEGATIVE_MATRIX_VALIDATED`

## Canonical Context

A2.2 follows:

- P18.0–P18.9 validated;
- A0 provider/topology preflight completed;
- A1 Railway/RLS preflight validated;
- A2.1 network/TLS/exposure validated.

A2.2 validates the tenant/auth/security negative matrix only. It does not satisfy the parent A2 gate because A2.3 recovery evidence is still required.

## Accepted Evidence

### Live

- candidate: `kgm-preflight-api-v3`
- deployment: `52c39935-9e89-4f12-82e3-82345c606426`
- deployed source: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`
- accepted workflow run: `34373579763`
- accepted workflow job: `102540600589`
- result: `A2_2_LIVE_SECURITY_NEGATIVE_MATRIX=PASS`
- live RLS alternate-tenant visible rows: `0`
- auth/privilege escalation negative cases: `7 / 7 rejected`
- protected mutation/RLS endpoints without valid bearer: `REJECTED`
- IDOR/SSRF guessed public routes: `ABSENT`
- credential use by probe: `NONE`

### Structural / Regression

The PR adds exact-source tests for:

- server-side tenant selection only;
- no generic URL-fetch surface;
- safe metadata redaction;
- injection-style identifier rejection before DB connection;
- payload hashing and SQL parameterization;
- constrained transaction-local runtime role;
- forced RLS and non-BYPASSRLS behavior;
- absence of elevated table/schema grants.

Final PR merge remains contingent on green standard regression CI on the final PR head.

## Infrastructure Mutation Check

During A2.2:

- Railway staged changes remained present and untouched;
- no service configuration was applied;
- no redeploy was triggered;
- no public DB exposure was created;
- no secret was read through the probe;
- no paid resource was authorized.

## Preserved State

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`
- `P18_9_LAUNCH_ELIGIBLE = FALSE`
- canonical runtime = `PROJECT_LOCAL_ONLY`
- mixed/shared canonical runtime = `BLOCKED`
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`
- paid resources = `NOT_CONSIDERED / NOT_AUTHORIZED`
- production/live = `NOT_OPERATIONAL`
- strategic machine state = `4.34`

## Current Position

`A1 VALIDATED -> A2.1 VALIDATED -> A2.2 VALIDATED -> A2.3 NEXT -> A3 -> A4 -> A5 OWNER DECISION`

Next executable stage after this checkpoint is merged:

`A2.3 — Backup / Restore / Rollback`

Parent gate `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED` remains `NOT_SATISFIED` until A2.3 closure.