# PROJECT CHECKPOINT — P15.1 FORECAST/OUTCOME PERSISTENCE MODEL VALIDATED

Date: 2026-09-04
Project: K-Geopolitical Monitor
State: `P15_1_FORECAST_OUTCOME_PERSISTENCE_MODEL_VALIDATED`

## Validation Anchor

Exact validated implementation/test HEAD:
`a5b25aae1bf3c5962385b852c987e802469239ca`

Validation evidence:
- x64 CI run `33899347550`, job `101109486579`: `525 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33899347669`, job `101109486964`: native `aarch64`, `525 passed, 2 warnings / SUCCESS`;
- host bootstrap: PASS;
- unattended one-tick: PASS;
- systemd contract: PASS.

## Validated Persistence Model

P15.1 adds migration `028_forecast_outcome_assessment_history.sql` and an append-only repository layer.

Validated properties:
- `forecast_outcome_assessments` records resolution lifecycle independently of legacy scenario-result state;
- `forecast_outcome_assessment_evidence` records ordered typed provenance references;
- resolution states are `RESOLVED`, `UNRESOLVED`, `PARTIAL`, `AMBIGUOUS`;
- `RESOLVED` requires explicit outcome evidence;
- optional linkage to legacy `forecast_outcomes` must remain within the same forecast;
- Phase 15 assessment/evidence history cannot be UPDATEd or DELETEd;
- legacy M12 forecast outcome/evaluation history remains readable and is not rewritten.

## Truth / Provenance Boundary

Forecast probability, scenario confidence, calibration/performance metrics, coverage confidence, legacy scalar confidence and source/host/domain/language/adapter/item counts remain non-promotional with respect to factual verification.

P15.1 introduces no factual-verification field or alternate truth store. Canonical factual verification remains owned by the current P13.5 decision through the P13.6 semantic/live bridge.

## Historical Migration Boundary

Phase 14 introduced no migration `028`. Migration `028_forecast_outcome_assessment_history.sql` is a Phase 15.1 artifact. Historical guards were updated only to preserve this temporal distinction.

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

P15.2 — Provenance-Bound Outcome Resolution.
