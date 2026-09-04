# Phase 15 — Forecast Calibration and Performance Intelligence

Date: 2026-09-04
Status: `IN_PROGRESS`
Project: K-Geopolitical Monitor
Strategic phase gate: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`

## Objective

Establish a provenance-bound forecast evaluation layer that can represent outcomes, calibration observations and performance evidence without allowing forecast probability, scenario confidence, calibration metrics, coverage, legacy scalar confidence or source counts to promote factual verification.

Phase 15 extends the validated M12/E7 forecasting baseline and preserves all Phase 13 semantic-verification and Phase 14 runtime/security boundaries.

## Audited Compatibility Baseline

- M12 already persists stable `forecast_id`, immutable `forecast_version_id` and immutable `scenario_version_id` objects.
- Scenario versions keep `raw_probability`, `calibrated_probability` and `scenario_confidence` separate.
- M12 `forecast_outcomes`, `forecast_evaluations` and calibration history remain readable compatibility state.
- P13.5/P13.6 remain the canonical factual-verification path.
- Phase 14 remains `VALIDATED_READY / NOT_ACTIVATED`.
- No parallel forecast truth store is authorized.

## P15.0 — Forecast Calibration Architecture Contract

State: `VALIDATED`
Gate: `P15_0_FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT_VALIDATED`
Validation anchor: `3019884590dfdc2aec8230a33f0521330575b08e`

Validation:
- x64 run `33897654496`, job `101103985520`: `518 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33897654494`, job `101103985599`: `518 passed, 2 warnings / SUCCESS`;
- bootstrap/unattended/systemd: PASS.

P15.0 defines `KGM_FORECAST_CALIBRATION_PERFORMANCE_ARCHITECTURE_V1` and separates `forecast`, `forecast_version`, `scenario_version`, `outcome_assessment`, `calibration_observation` and `performance_aggregate`.

Outcome-resolution states: `RESOLVED`, `UNRESOLVED`, `PARTIAL`, `AMBIGUOUS`. Only `RESOLVED` is automatically scoreable at the architecture level. Migration `028`: `NONE_FOR_P15_0`.

## P15.1 — Forecast/Outcome Persistence Model

State: `VALIDATED`
Gate: `P15_1_FORECAST_OUTCOME_PERSISTENCE_MODEL_VALIDATED`
Validation anchor: `a5b25aae1bf3c5962385b852c987e802469239ca`

Validation:
- x64 run `33899347550`, job `101109486579`: `525 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33899347669`, job `101109486964`: `525 passed, 2 warnings / SUCCESS`;
- bootstrap/unattended/systemd: PASS.

P15.1 introduced additive migration `028_forecast_outcome_assessment_history.sql` and `forecast_outcome_persistence.py`.

Validated persistence rules:
- `forecast_outcome_assessments` and ordered typed provenance references are append-only;
- `RESOLVED` requires explicit evidence;
- optional legacy-outcome linkage must remain within the same forecast;
- legacy M12 outcome/evaluation history is not rewritten;
- legacy `OBSERVED/NOT_OBSERVED` result semantics remain distinct from Phase 15 resolution lifecycle semantics.

Phase 14 introduced no migration `028`; migration 028 is a Phase 15.1 artifact.

## P15.2 — Provenance-Bound Outcome Resolution

State: `VALIDATED`
Gate: `P15_2_PROVENANCE_BOUND_OUTCOME_RESOLUTION_VALIDATED`
Validation anchor: `f70c03d1c902d4af45c0f32676a75e3093943ac4`

Validation:
- x64 run `33900253602`, job `101112390646`: `534 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33900253628`, job `101112390649`: native `aarch64`, `534 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS;
- ARM64 systemd contract: PASS.

P15.2 introduces `forecast_outcome_resolution.py` and no new migration.

Validated resolution rules:
- no persisted final forecast result resolves fail-closed to `UNRESOLVED`;
- legacy `OBSERVED` and `NOT_OBSERVED` may map to Phase 15 `RESOLVED` only when the result is linked to the same forecast and traceable persisted outcome evidence is supplied;
- legacy `PARTIAL` and `AMBIGUOUS` remain non-binary Phase 15 states;
- persisted `RAW_ITEM`, `SEMANTIC_CLAIM` and `SEMANTIC_EVIDENCE` references must exist before use;
- `EXTERNAL_REFERENCE` alone cannot establish a canonical `RESOLVED` outcome;
- a resolved assessment requires persisted evidence with provenance role `OUTCOME_EVIDENCE`;
- assessment history remains monotonic and append-only;
- outcome resolution does not write, alter or promote `semantic_verification_decision_versions` or any other P13 factual-verification state.

## Permanent Epistemic Boundary

The following cannot promote factual verification:
- forecast probability or scenario confidence;
- Brier/calibration/performance measurements;
- coverage metrics;
- legacy scalar confidence;
- source/host/domain/language/adapter/item counts.

Canonical factual verification remains supplied only by the current P13.5 decision through the P13.6 semantic/live bridge.

## Runtime / Security Boundary

Unchanged through P15.2:
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- public ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- paid providers: `NONE_APPROVED`;
- owner execution: disabled;
- `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.

## Planned Phase 15 Sequence

- P15.0 — Forecast Calibration Architecture Contract — `VALIDATED`;
- P15.1 — Forecast/Outcome Persistence Model — `VALIDATED`;
- P15.2 — Provenance-Bound Outcome Resolution — `VALIDATED`;
- P15.3 — Calibration Engine — `NOT_STARTED`;
- P15.4 — Performance Intelligence and Drift/Bias Analysis — `NOT_STARTED`;
- P15.5 — Owner Read-Only Performance Projection — `NOT_STARTED`;
- P15.6 — Phase 15 Validation Matrix / Closure — `NOT_STARTED`.

Next sequential engineering task: P15.3 — Calibration Engine.
