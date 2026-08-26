# M12.1 Durable Forecast Schema and Version Identity Result

Status: PASS
Date: 2026-08-26
Gate: M12_1_DURABLE_FORECAST_SCHEMA_VALIDATED

## Implementation

Implementation commit:

- 426a66a9073c12ddf44d1de83ca49c9b2cbd7a75 - Implement M12.1 durable forecast schema and version identity

Implemented:

- migration `011_advanced_forecasting.sql`;
- project-local `forecasts`, `forecast_versions` and `forecast_scenario_versions` tables;
- deterministic forecast identity from target key, horizon and evaluation deadline;
- deterministic forecast-version and scenario-version identity;
- immutable forecast-version persistence;
- monotonic version numbering;
- restart-safe durable forecast/scenario retrieval;
- idempotent repeated save for identical deterministic definitions;
- raw and calibrated scenario probability-distribution validation;
- scenario confidence bounded independently from evidence confidence;
- approved scenario structure fields for drivers, constraints, triggers, inhibitors, uncertainty factors and invalidation signals;
- direct compatibility with existing ForecastHorizon and ScenarioType contracts.

## Validation

GitHub Actions run:

- run_id: 32974666330
- workflow: CI
- result: PASS
- tests: 123 passed
- execution time: 6.26s
- Python: 3.11

M12.1 acceptance coverage includes:

- restart persistence;
- deterministic identity;
- idempotent repeated save;
- immutable old versions;
- monotonic version sequence;
- normalized raw probability distribution;
- normalized calibrated probability distribution;
- existing forecast horizon and scenario type compatibility;
- canonical migration execution and idempotence.

## Architectural Boundaries

- Forecasts remain analytical outputs, not facts.
- Forecast probability and scenario confidence are separate from M8 verification confidence.
- M11 graph relationships are not independent evidence.
- No forecast creates a canonical verified event or claim.
- Runtime storage remains PROJECT_LOCAL_ONLY.
- No external forecasting provider is introduced.

## Result

M12_1_DURABLE_FORECAST_SCHEMA_VALIDATED = PASS

## Next

M12.2 Provenance-Bound Forecast Inputs.
