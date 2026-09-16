# P21.2 — Fresh Operational Health Baseline — Measurement Result

Date: 2026-09-16
Status: `VALIDATED_WITH_MEASURED_DEGRADATION`
Gate: `P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED`

Measurement vantage: `OWNER_LOCAL_KGM_E4_PILOT_ISOLATED_CANONICAL_CHECKOUT` on `kgm-e4-owner-pilot` (`aarch64`). Canonical checkout SHA: `3ff9df391f31ff8c7d19e6c229e4647e8dc88597`. Deployed runtime observed separately at `b31b2136b5fe982d0b63b0135479b1549041906c`; it was not changed or restarted.

Fresh assessed-at timestamp: `2026-09-16T16:59:49.917696+00:00`.

## Result

- measured sources: `10/10`;
- collection: `PARTIAL`;
- source successes: `8`;
- source failures: `2`;
- collected items: `260`;
- current measurement freshness: `10/10 CURRENT`.

Measured failures:
- `gdelt-doc-2`: `UNAVAILABLE / TRANSPORT`, HTTP `429`;
- `eu-parliament-press-releases`: `UNAVAILABLE / PARSER`, payload not valid XML.

Successful but stale-content observations:
- `eu-commission-press-corner`: collector `HEALTHY`, content `STALE` against its configured freshness expectation;
- `osce-latest-news`: collector `HEALTHY`, content `STALE` against its configured freshness expectation.

The remaining six successful paths were `HEALTHY / FRESH` in this snapshot: Consilium, Haberturk, Meduza, RMF24, GOV.UK and Ukrainska Pravda.

This is operational evidence from one explicit vantage, not a claim of global reachability, credibility, truth, independent corroboration, or exhaustive coverage. P13.5/P13.6 remains factual-verification authority.

Validation: GitHub CI run `35126109733`, job `104895421504`: `1263 passed in 122.61s / SUCCESS`. Canonical merge anchor: `7affa9ee3ca875ddff472972ee63d11a03ed1054`.

Safety: `LIVE_SOURCE_EXPANSION=NO`, `RUNTIME_DEPLOYMENT=NO`, `SERVICE_RESTART=NO`, `MIGRATION_033=NOT_CREATED/NOT_PREAUTHORIZED`, `PLUGIN_BUILD=NOT_STARTED`, `PLUGIN_PUBLICATION=NOT_ACTIVATED`.
