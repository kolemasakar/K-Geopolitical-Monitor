# M12.4 Outcome Resolution and Historical Evaluation Result

Status: PASS
Date: 2026-08-26
Gate: M12_4_OUTCOME_EVALUATION_VALIDATED

## Implementation

Implementation commit:

- 46ccaaaded487531d4f0feb8d32545dab421f9cf - Implement M12.4 outcome resolution and evaluation

Implemented:

- migration `013_forecast_outcomes_evaluations.sql`;
- durable immutable forecast outcomes;
- outcome states OBSERVED, NOT_OBSERVED, PARTIAL and AMBIGUOUS;
- outcome evidence references validated against project-local raw items;
- exact forecast-version and scenario-version historical evaluation linkage;
- reuse of existing Brier-score and calibration-error helpers;
- raw and calibrated probability metrics stored separately;
- deterministic immutable evaluation identity by outcome, scenario version and method/version;
- binary one-vs-rest baseline evaluation method with explicit version metadata;
- horizon-aware historical summaries;
- restart-safe outcome and evaluation history;
- PARTIAL and AMBIGUOUS outcomes persist without invented binary precision.

## Validation

GitHub Actions run:

- run_id: 32976909208
- workflow: CI
- result: PASS
- tests: 143 passed
- execution time: 25.41s
- Python: 3.11

M12.4 acceptance coverage includes:

- durable evidence-backed outcome resolution;
- unknown outcome evidence reference fail-closed behavior;
- exact-version OBSERVED evaluation;
- raw and calibrated Brier scoring;
- raw and calibrated calibration-error scoring;
- idempotent immutable repeated evaluation;
- PARTIAL/AMBIGUOUS no-score handling with sample_count=0;
- rejection of evaluation against another forecast's version;
- horizon-aware scorable/unscorable historical summaries;
- canonical migration execution and idempotence through migration 013.

## Architectural Boundaries

- Outcomes require explicit evidence and explanation.
- Historical evaluation does not rewrite the original forecast version.
- PARTIAL and AMBIGUOUS outcomes do not receive synthetic binary labels.
- Historical metrics do not mutate M8 evidence confidence or M11 graph state.
- Runtime storage remains PROJECT_LOCAL_ONLY.
- No external forecasting provider is introduced.

## Result

M12_4_OUTCOME_EVALUATION_VALIDATED = PASS

## Next

M12.5 Calibration and Performance History.
