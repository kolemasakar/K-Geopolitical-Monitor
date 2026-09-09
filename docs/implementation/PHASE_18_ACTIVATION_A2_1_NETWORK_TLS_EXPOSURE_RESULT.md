# Phase 18 Activation A2.1 — Network / TLS / Exposure Result

Date: 2026-09-09
Status: `PASS / VALIDATED / NOT_ACTIVATED`
Gate: `PHASE_18_ACTIVATION_A2_1_NETWORK_TLS_EXPOSURE_VALIDATED`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A2_1_NETWORK_TLS_EXPOSURE_VALIDATED.md`

## Result summary

A2.1 validated the existing disposable Railway A1 candidate without credentials, Railway mutations, paid-resource use, canonical-data movement, or production activation.

Accepted live evidence:

- Railway API service `kgm-preflight-api-v3`: deployment `52c39935-9e89-4f12-82e3-82345c606426`, `SUCCESS`;
- API public domain: `kgm-preflight-api-v3-production.up.railway.app`;
- PostgreSQL service `kgm-preflight-postgres`: `SUCCESS`, zero service domains, zero custom domains;
- GitHub-hosted external probe run `34368911806`, job `102524751017`;
- TLS 1.3 handshake PASS;
- HTTPS `/health` = 200;
- HTTP `/health` = 301 redirect to HTTPS;
- `/docs` and `/redoc` = 404;
- unauthenticated protected API = 401 with Bearer challenge;
- Railway internal PostgreSQL hostname not publicly resolvable from the external runner;
- no credential or DSN value observed in the inspected public response/build/deploy evidence;
- health metadata confirms non-canonical, non-production, non-activated synthetic mode and `railway_private` database networking.

## Gate state

`A2_1 = VALIDATED`

`A2_2 = NEXT`

`A2_3 = BLOCKED_ON_A2_2`

`PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED = NOT_YET_SATISFIED`

The strategic machine state remains deliberately unchanged at state sync `4.34` until a separately defined formal synchronization gate.

## Beta boundaries

- `BETA_USER_MODEL = SINGLE_OWNER_ONLY`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- canonical runtime = owner-local / `PROJECT_LOCAL_ONLY`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.
