# PROJECT CHECKPOINT — P15.5 OWNER READ-ONLY PERFORMANCE PROJECTION VALIDATED

Date: 2026-09-04
Project: K-Geopolitical Monitor
State: `P15_5_OWNER_READ_ONLY_PERFORMANCE_PROJECTION_VALIDATED`

## Validation Anchor

Exact validated implementation/test HEAD:
`7659c33b321c6dec62240976930015696ae4e1da`

Validation evidence:
- x64 CI run `33904943801`, job `101127542119`: `568 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33904943796`, job `101127542387`: native `aarch64`, `568 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS;
- ARM64 systemd contract: PASS.

## Validated Owner Projection Contract

P15.5 adds:
- `src/kgeopolitical_monitor/forecast_performance_projection.py`;
- no new migration;
- no new API route, public endpoint or deployment.

Validated rules:
- the projection reads only already-persisted P15.4 aggregate and drift state;
- canonical SQLite is opened with `mode=ro` and `PRAGMA query_only = ON`;
- the projection does not initialize the database and does not call P15.4 aggregate/drift creation paths;
- a missing canonical project-local database fails closed and is not created;
- absence of persisted performance records is surfaced explicitly as `NO_PERSISTED_PERFORMANCE_DATA`;
- aggregate/drift lists are bounded while total persisted counts remain visible;
- explicit cohort definition, observation-set hash, sample size, raw/calibrated metrics and descriptive sample limitations remain visible;
- sample qualification remains descriptive only and is not statistical confidence;
- drift remains a descriptive temporal delta and is not a causal or statistical-significance claim;
- owner projection creates no calibration observations, performance aggregates or drift comparisons.

## Truth Boundary

Forecast probability, calibration/performance metrics, drift metrics, sample size and sample qualification do not write, rank or promote P13 factual-verification state. Canonical factual verification remains P13.5/P13.6 only.

## Runtime / Security Boundary

Unchanged:
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- public ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- paid providers: `NONE_APPROVED`;
- owner execution: disabled;
- `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.

## Next Sequential Task

P15.6 — Phase 15 Validation Matrix / Closure.
