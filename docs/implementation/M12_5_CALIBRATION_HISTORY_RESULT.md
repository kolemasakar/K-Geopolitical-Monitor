# M12.5 Calibration and Performance History Result

Status: PASS
Date: 2026-08-26
Project: K-Geopolitical Monitor
Milestone: M12.5 Calibration and Performance History

## Implementation Evidence

Implementation commit:
- `29421ccdeca5d8c3f2b306652b006e6c0d3d1200`

Deterministic ordering fix:
- `49099447ef1035c100642e194c30a8d2cd4e842f`

GitHub Actions validation:
- run: `32977809109`
- result: `148 passed in 11.05s`
- conclusion: `success`

## Validated Contracts

- immutable calibration history snapshots;
- explicit calibration method and method version;
- minimum calibration sample count of 5 scorable evaluations;
- exact evaluation-ID cohort identity;
- RAW and CALIBRATED probability history;
- deterministic calibration bucket ordering across first run and restart reads;
- cohort and bucket calibration summaries;
- performance breakdown by horizon and scenario type;
- PARTIAL and AMBIGUOUS evaluations with sample_count=0 are excluded from calibration cohorts;
- calibration history has no write path into persisted scenario probabilities.

## Defect Found and Corrected

The first M12.5 CI run exposed a deterministic API ordering defect. Newly created bucket results were returned in RAW then CALIBRATED order, while restart reads used alphabetical SQL ordering. The calibration values and sample filtering were correct.

The repository was corrected so persisted and newly created results use the same semantic ordering: RAW first, then CALIBRATED, then bucket index.

## Gate

`M12_5_CALIBRATION_HISTORY_VALIDATED = PASS`

## Boundary

This gate validates project-local calibration history and performance measurement only. It does not approve automatic probability optimization, external forecasting providers, shared runtime storage, or conversion of forecast outputs into verified facts or canonical events.
