# M12 Advanced Forecasting Delta Audit

Status: AUDIT_COMPLETE
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 9 - Advanced Forecasting

## Audit Objective

Determine the exact delta between the existing forecasting baseline and the approved Phase 9 forecasting model before adding new implementation.

## Canonical Forecasting Contract

FORECASTING_MODEL.md is APPROVED and defines:

- forecasts are scenario-based assessments rather than facts;
- inputs may include verified information, relationships, trends, actor behaviour and constraints;
- horizons are SHORT-TERM, MEDIUM-TERM, LONG-TERM and GLOBAL_EVOLUTIONARY;
- significant scenarios should include probability/relative likelihood, confidence, drivers, constraints, triggers, inhibitors and invalidation signals;
- forecast lifecycle is versioned: Forecast -> New Evidence -> Update -> Outcome Evaluation -> Calibration.

## Existing Baseline

### Forecast Preparation

`forecast_preparation.py` provides:

- ForecastHorizon;
- ForecastSignal;
- manual event_id, momentum, influence, confidence and horizon input.

Gap:

- no durable input snapshot;
- no evidence or graph provenance refs;
- no explicit assumptions/constraints;
- no input version identity;
- no validation that forecast confidence is distinct from upstream evidence confidence.

### Probabilistic Forecasting

`probabilistic_forecasting.py` provides:

- ScenarioType;
- ForecastScenario;
- probability normalization;
- drivers and uncertainty factors.

Gap:

- no durable forecast/scenario identity;
- no forecast version;
- no explicit scenario confidence;
- no constraints/triggers/inhibitors/invalidation signals;
- no time horizon or target outcome contract on each durable forecast;
- no scenario update/invalidation lifecycle;
- no provenance refs.

### Forecast Calibration

`forecast_calibration.py` provides:

- bounded probability calibration through a scalar historical_factor.

Gap:

- no calibration dataset;
- no sample-size contract;
- no historical cohort/version identity;
- no calibration method/version record;
- no separation between raw and calibrated scenario probability in durable history.

### Forecast Metrics

`forecast_metrics.py` provides:

- Brier score;
- absolute calibration error;
- a baseline metric result shape.

Gap:

- no aggregate cohort evaluation;
- no bucketed calibration;
- no longitudinal performance history;
- no per-horizon or scenario-type performance;
- no durable metric run identity.

### Historical Validation

`historical_validation.py` provides:

- ForecastOutcome;
- threshold-based accuracy across supplied outcomes.

Gap:

- no persisted outcome lifecycle;
- no outcome resolution timestamp;
- no partial/ambiguous outcome state;
- no link to a specific forecast version/scenario version;
- no Brier/calibration integration.

### Pattern Learning

`pattern_learning.py` provides a baseline PatternLearner and typed pattern categories.

Gap:

- current output is a static baseline pattern;
- no measured sample support;
- no connection to forecast calibration or scenario revision;
- pattern confidence must not become source-evidence confidence.

## Existing Test Depth

Current forecasting tests validate basic creation, bounds and arithmetic:

- probability normalization;
- calibration bounds;
- Brier and absolute calibration arithmetic;
- basic signal creation;
- simple threshold historical accuracy.

They do not constitute an Advanced Forecasting acceptance gate.

## M12 Required Delta

M12 must converge the existing baseline around one durable project-local forecast contract with:

1. deterministic forecast and forecast-version identity;
2. explicit target/question, horizon and evaluation deadline;
3. immutable input/provenance snapshot per forecast version;
4. scenario records with raw probability, calibrated probability and scenario confidence;
5. drivers, constraints, triggers, inhibitors, uncertainty and invalidation signals;
6. explicit forecast/version lifecycle;
7. outcome resolution linked to the exact forecast/scenario version;
8. Brier/calibration evaluation and cohort metrics;
9. reproducible calibration records with method/version/sample support;
10. forecast update history driven by new evidence without rewriting prior versions;
11. graph relationships as analytical inputs only, not independent evidence;
12. strict non-mutation of M8 verification confidence/origin count and M11 graph truth;
13. PROJECT_LOCAL_ONLY persistence and no external forecasting provider requirement for the baseline.

## Convergence Decision

Do not create a parallel forecasting engine.

M12 should preserve existing public baseline helpers where practical and add a durable forecasting layer around them. Existing scalar helpers remain compatibility utilities; the new durable model becomes the advanced forecasting contract.

## Audit Result

M12_DELTA_AUDIT_PASS = PASS

Phase 9 implementation is ready to proceed under a project-local, provenance-preserving design.
