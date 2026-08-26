# M12 Advanced Forecasting Plan

Status: COMPLETED
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 9 - Advanced Forecasting

## Goal

Extend the validated forecasting baseline into a durable, versioned, calibrated and explainable project-local scenario forecasting system while preserving canonical evidence and graph truth boundaries.

## Architecture Rule

M12 extends existing forecasting modules rather than creating a parallel forecasting subsystem.

Forecasts are analytical outputs, not facts.

Runtime storage remains PROJECT_LOCAL_ONLY.

## Mandatory Boundaries

- No shared or mixed runtime database.
- No external forecasting provider is required by the baseline.
- Forecast probability is not evidence confidence.
- Forecast confidence is not M8 verification confidence.
- Forecast results must not increase independent-origin count.
- M11 graph relationships may be forecast inputs but are not independent source evidence.
- Forecast updates create new versions; prior forecast versions remain immutable.
- Calibration must be reproducible from explicit historical outcomes and method metadata.
- No forecast may silently become a canonical event or verified claim.

## Canonical Durable Model

### Forecast

Required baseline fields:

- forecast_id;
- target_key;
- question;
- horizon;
- evaluation_deadline;
- status;
- created_at;
- updated_at.

Baseline statuses:

- ACTIVE;
- RESOLVED;
- INVALIDATED;
- CLOSED.

### Forecast Version

Required fields:

- forecast_version_id;
- forecast_id;
- version_number;
- input_snapshot_json;
- provenance_refs_json;
- assumptions_json;
- created_at;
- change_reason.

A forecast version is immutable after creation.

### Scenario Version

Required fields:

- scenario_version_id;
- forecast_version_id;
- scenario_type;
- label;
- raw_probability;
- calibrated_probability;
- scenario_confidence;
- drivers_json;
- constraints_json;
- triggers_json;
- inhibitors_json;
- uncertainty_factors_json;
- invalidation_signals_json.

Probabilities inside one forecast version must form a validated distribution.

### Outcome Resolution

Required fields:

- outcome_id;
- forecast_id;
- resolved_at;
- outcome_state;
- observed_scenario_type;
- evidence_refs_json;
- explanation.

Baseline outcome states:

- OBSERVED;
- NOT_OBSERVED;
- PARTIAL;
- AMBIGUOUS.

### Evaluation and Calibration

Persist:

- exact forecast/scenario version evaluated;
- Brier score when binary/outcome semantics permit;
- calibration error/cohort metrics;
- calibration method/version;
- sample count;
- raw vs calibrated probability;
- evaluation timestamp.

## M12.1 Durable Forecast Schema and Version Identity

Implemented and validated:

- migration `011_advanced_forecasting.sql`;
- durable forecast, forecast-version and scenario-version tables;
- deterministic forecast identity;
- monotonic immutable version numbers;
- validated horizon/status contracts;
- probability distribution validation;
- restart persistence and repeated-save idempotence;
- compatibility with existing ForecastHorizon and scenario concepts.

Gate:
`M12_1_DURABLE_FORECAST_SCHEMA_VALIDATED = PASS`

## M12.2 Provenance-Bound Forecast Inputs

Implemented and validated:

- migration `012_forecast_provenance_inputs.sql`;
- immutable forecast input snapshots;
- evidence, event, finding and graph-reference provenance;
- explicit assumptions and constraints;
- SOURCE_EVIDENCE, CANONICAL_EVENT, GRAPH_RELATIONSHIP, OPERATIONAL_FINDING and ANALYST_ASSUMPTION input kinds;
- fail-closed unknown canonical references for durable project references.

Gate:
`M12_2_PROVENANCE_INPUTS_VALIDATED = PASS`

## M12.3 Scenario Lifecycle and Updates

Implemented and validated:

- complete approved scenario structure;
- raw probability vs calibrated probability;
- scenario confidence separate from evidence confidence;
- triggers, inhibitors and invalidation signals;
- forecast updates through new immutable versions;
- explicit change reason;
- previous versions remain queryable.

Gate:
`M12_3_SCENARIO_VERSIONING_VALIDATED = PASS`

## M12.4 Outcome Resolution and Historical Evaluation

Implemented and validated:

- migration `013_forecast_outcomes_evaluations.sql`;
- durable outcome resolution;
- exact forecast-version/scenario-version linkage;
- Brier score and calibration evaluation;
- horizon-aware historical summaries;
- PARTIAL/AMBIGUOUS handling without false binary precision;
- immutable evaluation records.

Gate:
`M12_4_OUTCOME_EVALUATION_VALIDATED = PASS`

## M12.5 Calibration and Performance History

Implemented and validated:

- migration `014_forecast_calibration_history.sql`;
- reproducible calibration records;
- method/version metadata;
- explicit historical cohort and sample count;
- raw/calibrated probability history;
- bucketed and cohort calibration summaries;
- performance breakdown by horizon and scenario type;
- minimum five-scorable-evaluation sample contract;
- deterministic RAW then CALIBRATED bucket ordering.

Gate:
`M12_5_CALIBRATION_HISTORY_VALIDATED = PASS`

## M12.6 Advanced Forecast Query and Isolation Gate

Implemented and validated:

- current forecast and version-history queries;
- scenario comparison;
- provenance-backed forecast explanation;
- outcome/evaluation history;
- calibration history;
- all existing forecast helper tests remain green;
- M8 confidence and independent-origin count remain unchanged;
- M11 graph state remains unchanged by forecasting;
- graph-derived inputs do not become independent evidence;
- runtime database remains project-local;
- no external forecasting service is required;
- full deterministic repository regression CI passes.

Gate:
`M12_ADVANCED_FORECASTING_BASELINE_PASS = PASS`

## Final Validation Summary

M12 implementation commit for the final query/isolation gate:
- `e148fe3e92892e95f565c8b6fa5aefba1528ec54`

GitHub Actions final M12 implementation regression:
- run `32980859938`;
- `154 passed in 8.19s`;
- conclusion: `success`.

M12.5 fixed regression:
- run `32977809109`;
- `148 passed in 11.05s`;
- conclusion: `success`.

All M12.1-M12.6 gates passed.

## Completion Boundary

M12 is complete and validates the ROADMAP Phase 9 Advanced Forecasting engineering baseline.

M12 completion does not approve production/global operational status, shared runtime storage, external forecasting providers, automatic probability optimization, or automatic conversion of forecasts into verified facts/events.
