# P22.6 — Downstream Intelligence Impact Result

Date: 2026-09-19

Status: `VALIDATED_WITH_NO_DOWNSTREAM_UPLIFT_OBSERVED`

Gate: `P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED`

Canonical base: `7c50fc6ed7c086c9d85aa963cfc9ceb77ef90535`.

## Exact cohort

P22.6 measures the exact P22.5 canonical cohort:

- 28 canonical semantic claims;
- 28 `DETECTED` verification decisions;
- 28 `ATTRIBUTION_ONLY` evidence relations;
- 28 unresolved underlying-origin roles;
- 0 automatic factual-independence credit.

## Contradiction workload

```text
semantic_contradiction_versions = 0
semantic_contradiction_evidence_links = 0
```

Interpretation: no canonical contradiction workload is observed in this exact cohort. This is **not** evidence that the underlying material is consistent or true.

## Analytical coverage

Legacy operational findings exist for all 28 collected items, but the canonical semantic scope is publication attribution only.

```text
legacy_operational_findings = 28
underlying_event_analytical_claims = 0
```

Therefore no underlying-event analytical uplift is observed.

## Forecast-input breadth

```text
forecasts = 0
forecast_versions = 0
forecast_version_inputs = 0
```

Forecast-input impact is measured as absent in this cohort; it is not inferred as a quality improvement.

## Decision

`VALIDATED_WITH_NO_DOWNSTREAM_UPLIFT_OBSERVED`

P22.6 validates that downstream impact is now measurable after P22.5, while preserving the result that no contradiction, underlying-event analytical, or forecast-input uplift is observed in the bounded cohort.

P13.5/P13.6 remain factual-verification authority.

Next gate: `P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED`.
