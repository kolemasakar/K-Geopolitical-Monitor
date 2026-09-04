# PROJECT CHECKPOINT — P15.4 PERFORMANCE INTELLIGENCE / DRIFT-BIAS VALIDATED

Date: 2026-09-04
Project: K-Geopolitical Monitor
State: `P15_4_PERFORMANCE_INTELLIGENCE_DRIFT_BIAS_VALIDATED`

## Validation Anchor

Exact validated implementation/test HEAD:
`ca014fbc3d3e7807b82c0a183d30356dab5414bd`

Validation evidence:
- x64 CI run `33903267073`, job `101122112480`: `560 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33903266962`, job `101122111679`: native `aarch64`, `560 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS;
- ARM64 systemd contract: PASS.

## Validated Performance Contract

P15.4 adds:
- migration `030_forecast_performance_intelligence.sql`;
- `forecast_performance_intelligence.py`;
- append-only `forecast_performance_aggregates`;
- exact aggregate-to-observation membership;
- append-only temporal drift comparisons.

Validated rules:
- performance snapshots consume only immutable P15.3 calibration observations;
- cohort definition, observation membership and observation-set hash are explicit and reproducible;
- new observations create a new aggregate snapshot rather than rewriting history;
- sample count is mandatory and small samples remain explicitly qualified by descriptive N-bands;
- mean Brier, reliability-based expected calibration error and signed probability bias are computed separately for raw and calibrated probabilities;
- calibration-improvement values remain descriptive raw-minus-calibrated deltas;
- drift comparison requires identical non-temporal cohort dimensions and explicit ordered non-overlapping time windows;
- drift values are recent-minus-baseline descriptive deltas only; no statistical-significance or causal claims are generated;
- bias labels, where requested, require an explicit descriptive tolerance and do not represent confidence bounds;
- aggregate, membership and comparison state is deterministic/idempotent and append-only.

## Truth Boundary

Performance intelligence does not write, rank or promote P13 factual-verification state. Forecast probability/confidence, Brier/ECE/bias/drift metrics, sample size, coverage and count metadata remain non-truth operators. Canonical verification remains P13.5/P13.6 only.

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

P15.5 — Owner Read-Only Performance Projection.
