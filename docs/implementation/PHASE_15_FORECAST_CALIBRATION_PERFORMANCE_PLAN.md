# Phase 15 — Forecast Calibration and Performance Intelligence

Date: 2026-09-04
Status: `IN_PROGRESS`
Project: K-Geopolitical Monitor
Strategic phase gate: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`

## Objective

Establish a provenance-bound forecast evaluation layer that can represent outcomes, calibration observations and performance evidence without allowing forecast probability, scenario confidence, calibration metrics, coverage, legacy scalar confidence or source counts to promote factual verification.

Phase 15 extends the validated M12/E7 forecasting baseline and preserves all Phase 13 semantic-verification and Phase 14 runtime/security boundaries.

## Audited Compatibility Baseline

Existing validated capabilities are reused rather than replaced:

- M12 advanced forecasting already persists stable `forecast_id`, immutable `forecast_version_id` and immutable `scenario_version_id` objects;
- scenario versions already keep `raw_probability`, `calibrated_probability` and `scenario_confidence` separate;
- E7 defines `KGM_FORECAST_SEMANTICS_V1` and explicitly forbids forecast metrics from changing factual verification, factual/evidence confidence or independent-origin counts;
- P13.5/P13.6 remain the canonical factual-verification path;
- Phase 14 remains `VALIDATED_READY / NOT_ACTIVATED` and owner execution remains separately gated.

No parallel forecast store or truth store is authorized.

## P15.0 — Forecast Calibration Architecture Contract

State: `IMPLEMENTED_PENDING_VALIDATION`
Target gate: `P15_0_FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT_VALIDATED`

P15.0 introduces the machine-readable contract `KGM_FORECAST_CALIBRATION_PERFORMANCE_ARCHITECTURE_V1` in `src/kgeopolitical_monitor/forecast_calibration_contract.py`.

### Canonical entity boundaries

The architecture distinguishes:

- `forecast` — stable target/question and evaluation horizon;
- `forecast_version` — immutable analytical snapshot and assumptions;
- `scenario_version` — immutable raw/calibrated probability and scenario-confidence assessment;
- `outcome_assessment` — provenance-bound conclusion available at evaluation time;
- `calibration_observation` — immutable scoreable pairing of a forecast/scenario version with an outcome assessment;
- `performance_aggregate` — derived performance evidence over an explicit cohort.

Forecast inputs and outcome evidence are separate provenance roles.

### Outcome-state contract

Initial states are:

- `RESOLVED`;
- `UNRESOLVED`;
- `PARTIAL`;
- `AMBIGUOUS`.

Only `RESOLVED` is automatically scoreable at the P15.0 architecture level. `UNRESOLVED` is not a negative outcome, `PARTIAL` is not coerced to binary, and `AMBIGUOUS` fails closed for automatic scoring.

Later implementation phases may add typed resolution detail, but they must not weaken this fail-closed baseline.

### Calibration contract

The initial metric family is prepared for:

- Brier score;
- reliability/calibration buckets.

P15.0 does not compute either metric. It defines their permitted inputs and interpretation.

Mandatory rules:

- calibration measures forecast-probability performance, not factual-verification quality;
- raw and calibrated probability are evaluated separately;
- scenario confidence is never substituted for probability;
- scoring requires an explicitly scoreable outcome;
- performance aggregation must expose cohort definition and sample size;
- small-sample results must remain explicitly qualified.

### Permanent epistemic invariants

The following can never promote factual verification:

- forecast probability or scenario confidence;
- calibration score or performance rank;
- coverage metrics;
- legacy scalar confidence;
- source, host, domain, language, adapter or item counts.

Outcome resolution does not retroactively turn forecast context into independent evidence. Canonical factual verification remains supplied only by the current P13.5 decision through the P13.6 semantic/live bridge.

### Persistence decision

Migration `028`: `NONE_FOR_P15_0`.

Reason: P15.0 establishes the architecture and validation contract only. Existing forecast identity/version fields are sufficient for the contract baseline. Any later Phase 15 persistence change must be additive, explicitly reviewed and must preserve historical forecast versions.

### Runtime / security boundary

Unchanged:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- public ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- paid providers: `NONE_APPROVED`;
- owner execution: disabled;
- `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.

P15.0 does not activate Phase 14 operations or any external forecasting provider.

## Planned Phase 15 sequence

- P15.0 — Forecast Calibration Architecture Contract — `IMPLEMENTED_PENDING_VALIDATION`;
- P15.1 — Forecast/Outcome Persistence Model — `NOT_STARTED`;
- P15.2 — Provenance-Bound Outcome Resolution — `NOT_STARTED`;
- P15.3 — Calibration Engine — `NOT_STARTED`;
- P15.4 — Performance Intelligence and Drift/Bias Analysis — `NOT_STARTED`;
- P15.5 — Owner Read-Only Performance Projection — `NOT_STARTED`;
- P15.6 — Phase 15 Validation Matrix / Closure — `NOT_STARTED`.

P15.0 must pass repository regression validation before its state is promoted to `VALIDATED`.
