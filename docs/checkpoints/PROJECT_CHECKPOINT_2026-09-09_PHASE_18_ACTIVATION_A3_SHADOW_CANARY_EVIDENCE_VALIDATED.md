# Project Checkpoint — Phase 18 Activation A3 Shadow / Reconciliation / Canary Evidence

Date: 2026-09-09
Project: K-Geopolitical Monitor
Gate: `PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED`
Status: `VALIDATED / CANONICAL_MERGE_PENDING`
Strategic state sync: `4.34` unchanged

## Scope

A3 validates bounded non-production shadow/reconciliation/canary evidence while
preserving owner-local canonical authority and all beta restrictions.

## Accepted Evidence

PR #55 initial evidence head: `1c5f9bd3e161dda52cbae8fcc1fda9ef4441a23f`.

A3 workflow run `34379541994`:

- shadow-reconciliation job `102560691267`: SUCCESS;
- live-noncanonical-canary job `102560691011`: SUCCESS.

Full PR regression run `34379541997`, job `102560691416`:

- Ubuntu 24.04.5;
- Python 3.11.16 x64;
- `1164 passed in 98.42s`;
- SUCCESS.

## PostgreSQL Shadow Evidence

The no-charge disposable PostgreSQL 16.15 proof used synthetic data only and
validated:

- owner-local SQLite remains source of truth;
- PostgreSQL candidate remains non-canonical;
- exact deterministic reconciliation: PASS;
- primary tenant observation: two expected rows;
- alternate tenant has its own synthetic row while cross-tenant visibility is denied;
- forced RLS and NOBYPASSRLS runtime role: PASS;
- retry/idempotency: PASS;
- persistent outbox evidence: PASS;
- read-only shadow observation: PASS;
- deterministic mismatch classes: `ROW_COUNT`, `TABLE_CONTENT`, `SEMANTIC_PROJECTION`;
- deliberate mismatch count `3` against budget `2`: outside budget / fail-closed PASS;
- automatic promotion: false;
- canonical cutover authorized: false;
- shared-runtime activation authorized: false;
- production/live: false;
- migration 033 created/authorized: false;
- ephemeral cleanup: PASS.

## Live Railway Canary Evidence

Credential-free external observation returned:

- `A3_LIVE_CANARY_HEALTH=PASS`;
- `A3_LIVE_CANARY_NONCANONICAL=PASS`;
- `A3_LIVE_CANARY_RLS_STARTUP_EVIDENCE=PASS`;
- `A3_LIVE_RAILWAY_DATA_PLANE_RECONCILIATION=NOT_EVIDENCED`.

The canary confirms the existing disposable candidate remains healthy,
non-canonical, non-production, synthetic-only, on `railway_private`, with startup
RLS isolation evidence and zero alternate-tenant visibility.

## Explicit Evidence Boundary

`LIVE_RAILWAY_DATA_PLANE_RECONCILIATION = NOT_EVIDENCED`

No direct private Railway PostgreSQL command execution was available through the
current connector boundary. A3 therefore does not infer direct row-level live
Railway reconciliation, outbox mutation, retry persistence or privileged database
inspection from `/health`.

This bounded limitation does not invalidate the A3 gate because the approved beta
strategy requires no-charge non-production readiness evidence, not canonical
cutover, and the deterministic PostgreSQL data-plane proof is separately real and
reproducible on an ephemeral PostgreSQL service.

## Immutable Boundaries

- owner-local runtime remains canonical and independently operable;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- canary stages are read-only `1% -> 5% -> 25% -> 100%` observation design;
- automatic promotion/cutover remains forbidden;
- existing Railway staged changes remain untouched;
- strategic machine state remains `4.34`.

## Closure Procedure

The evidence above validates the A3 contract on the PR head. Formal canonical
closure requires, in order:

- fresh CI on the final documentation head;
- guarded merge of PR #55 using the exact final head SHA;
- successful exact-main regression on the resulting canonical merge SHA;
- successful exact-main A3 shadow/canary workflow on that SHA.

After those checks, A4 becomes the next executable stage:
`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`.
