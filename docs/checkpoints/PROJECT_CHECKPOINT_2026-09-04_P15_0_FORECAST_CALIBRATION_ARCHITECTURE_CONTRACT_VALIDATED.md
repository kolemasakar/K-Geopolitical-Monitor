# PROJECT CHECKPOINT — P15.0 FORECAST CALIBRATION ARCHITECTURE CONTRACT VALIDATED

Date: 2026-09-04
Project: K-Geopolitical Monitor
State: `P15_0_FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT_VALIDATED`

## Validation Anchor

Implementation and validation anchor:
`3019884590dfdc2aec8230a33f0521330575b08e`

Validation evidence:
- x64 CI run `33897654496`, job `101103985520`: `518 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33897654494`, job `101103985599`: native `aarch64`, `518 passed, 2 warnings / SUCCESS`;
- host bootstrap: PASS;
- unattended one-tick: PASS;
- systemd contract: PASS.

## Validated Contract

P15.0 establishes `KGM_FORECAST_CALIBRATION_PERFORMANCE_ARCHITECTURE_V1` and keeps the following roles separate:
- forecast;
- immutable forecast version;
- immutable scenario version;
- provenance-bound outcome assessment;
- calibration observation;
- derived performance aggregate.

Outcome states are `RESOLVED`, `UNRESOLVED`, `PARTIAL`, and `AMBIGUOUS`. Only `RESOLVED` is automatically scoreable at this architecture layer.

Forecast probability, scenario confidence, calibration score, performance rank, coverage metrics, legacy scalar confidence and source/host/domain/language/adapter/item counts cannot promote factual verification.

Canonical factual verification remains owned exclusively by the current P13.5 decision through the P13.6 semantic/live bridge.

## Persistence / Runtime Boundary

- migration `028`: `NONE_FOR_P15_0`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- public ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- paid providers: `NONE_APPROVED`;
- owner execution: disabled;
- `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.

## Next Sequential Task

P15.1 — Forecast/Outcome Persistence Model.
