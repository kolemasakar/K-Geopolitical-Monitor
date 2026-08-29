# E7 Forecast Probability Semantics

Status: BASELINE_VALIDATED
Date: 2026-08-29
Project: K-Geopolitical Monitor
Canonical engineering baseline: `72f049b30fcaa3711c7712c8df7d1da1f934f650`

## Objective

E7 hardens the semantic boundary between forecasting outputs and factual verification across persisted-state API, admin dashboard and report rendering surfaces.

The E7 delta-audit confirmed that the existing M12 persistence model already stores `raw_probability`, `calibrated_probability` and `scenario_confidence` separately. No new forecasting engine, parallel truth store or schema migration is required.

## Canonical semantic contract

E7 adds `KGM_FORECAST_SEMANTICS_V1` in `src/kgeopolitical_monitor/forecast_semantics.py`.

The contract defines:
- `raw_probability`: analytical scenario probability before calibration;
- `calibrated_probability`: calibrated analytical scenario probability;
- `scenario_confidence`: confidence in the quality/stability of the scenario assessment, not the probability that the scenario occurs.

Mandatory invariants:
- forecast probabilities are analytical outputs, not facts;
- scenario confidence is not forecast probability;
- forecast metrics do not modify claim verification state;
- forecast metrics do not modify factual/evidence confidence;
- forecast metrics do not modify independent-origin counts;
- graph relationships used as forecast context are not independent evidence.

## Backend Action API

The owner-only read-only API is extended to version `1.1.0` with:

`GET /v1/forecasts/active`

Operation ID: `getActiveForecasts`.

The response exposes the canonical forecast semantic contract and the three explicit scenario fields. Generic `probability` and generic `confidence` aliases are intentionally not introduced.

The existing read-only SQLite URI, `PRAGMA query_only = ON`, bearer authentication and `PROJECT_LOCAL_ONLY` storage boundary remain unchanged.

## Admin dashboard

The active-forecast HTML projection now renders every scenario as explicit values:

`Raw ... · Calibrated ... · Scenario confidence ...`

The dashboard notice states that forecast probability is analytical rather than factual confidence, forecast probabilities are not verification confidence, scenario confidence is not scenario probability, and forecast metrics never strengthen evidence or verification state.

The existing dashboard JSON projection already exposed the three persisted fields separately and remains compatible.

## Reporting and Markdown

The deterministic renderer now emits `forecast_semantics` in structured output whenever a `FORECAST_SCENARIO` section is present.

Markdown rendering adds a dedicated `Forecast semantics` section with the canonical contract version and explicit probability/confidence/verification boundaries.

This is presentation metadata only. Persisted M12 scenario state and M13 report snapshot/section/reference truth are not rewritten or recalculated.

## Regression isolation gate

`tests/test_e7_forecast_semantics.py` adds a deliberately adversarial fixture:
- claim verification state: `DETECTED`;
- factual claim confidence: `0.31`;
- independent-origin count: `1`;
- raw scenario probability: `0.95`;
- calibrated scenario probability: `0.98`;
- scenario confidence: `0.99`.

The regression verifies that API/dashboard/report presentation preserves the distinct forecast meanings and that the upstream claim remains exactly `DETECTED / 0.31 / 1` after forecast reads.

## Persistence and migration decision

No migration 021 is introduced for E7.

Reason: M12 already persists the required fields separately in `forecast_scenario_versions`. E7 is an additive semantic/presentation contract over canonical persisted state, not a new persistence model.

## Validation

Canonical engineering baseline:
`72f049b30fcaa3711c7712c8df7d1da1f934f650`

x64 GitHub Actions:
- workflow run: `33265984585`;
- job: `99136020793`;
- result: `294 passed, 1 warning in 29.26s`;
- conclusion: SUCCESS.

Native ARM64 GitHub Actions:
- workflow run: `33265984622`;
- job: `99136020853`;
- architecture: `aarch64`;
- result: `294 passed, 1 warning in 28.09s`;
- bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- systemd unit contract: PASS;
- conclusion: SUCCESS.

The single warning is the existing Starlette TestClient/httpx deprecation warning and is not an E7 functional failure.

## Boundary status after E7

Unchanged:
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared runtime storage: BLOCKED pending explicit architecture approval;
- private GPT backend Action connection: `NOT_CONNECTED`;
- backend HTTPS deployment: `NOT_DEPLOYED`;
- admin dashboard deployment: `NOT_DEPLOYED`;
- public sharing: DEFERRED;
- shared production runtime: NOT_APPROVED;
- production/live status: `NOT_OPERATIONAL`;
- no external forecasting provider is activated.

E7 gate:
`E7_FORECAST_PROBABILITY_SEMANTICS = BASELINE_VALIDATED`
