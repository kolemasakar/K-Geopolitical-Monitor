# PROJECT CHECKPOINT — P15.3 CALIBRATION ENGINE VALIDATED

Date: 2026-09-04
Project: K-Geopolitical Monitor
State: `P15_3_CALIBRATION_ENGINE_VALIDATED`

## Validation Anchor

Exact validated implementation/test HEAD:
`a2e16cd7e41f2bbef50f6da8e61083e9e944ccd4`

Validation evidence:
- x64 CI run `33902093460`, job `101118300735`: `548 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33902093284`, job `101118300259`: native `aarch64`, `548 passed, 2 warnings / SUCCESS`;
- host bootstrap: PASS;
- unattended one-tick: PASS;
- systemd contract: PASS.

## Validated Calibration Contract

P15.3 adds `forecast_calibration_engine.py` and additive migration `029_forecast_calibration_observations.sql`.

- observations bind exact P15 outcome assessment, forecast version and scenario version;
- only `RESOLVED` assessments with same-forecast binary legacy outcomes and addressable persisted `OUTCOME_EVIDENCE` are scoreable;
- `UNRESOLVED`, `PARTIAL` and `AMBIGUOUS` remain unscoreable;
- `OBSERVED` uses one-vs-rest binary targets and exact scenario mapping;
- `NOT_OBSERVED` maps all scenario targets to zero;
- raw and calibrated probabilities receive separate Brier scores and reliability buckets;
- `scenario_confidence` is never substituted for probability;
- probability `1.0` maps to the final reliability bucket;
- observations are deterministic, idempotent and append-only;
- legacy M12 evaluation/calibration history remains unchanged;
- performance aggregation and drift/bias analysis are deferred to P15.4.

## Truth Boundary

Calibration scores and buckets are forecast-performance evidence only. They do not write or promote P13 factual-verification state and cannot act as factual truth operators.

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

P15.4 — Performance Intelligence and Drift/Bias Analysis.