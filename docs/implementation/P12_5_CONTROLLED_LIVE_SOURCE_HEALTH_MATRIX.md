# P12.5 — Controlled-Live Source Health Matrix

Date: 2026-09-01
Validation anchor: `92d0c0516351e2af7ba836d3ae711dd414d22023`
Workflow: `P12.5 Controlled Live Source Health Inventory`
Run: `33533313654`
Job: `99941475574`
Result: `SUCCESS / P12_5_CONTROLLED_LIVE_MEASUREMENT_COMPLETE`

## Measurement Summary

- assessed source paths: `10/10`;
- unmeasured: `0`;
- collection attempts: `8 SUCCESS / 2 FAILED`;
- portfolio states at probe: `9 ACTIVE / 1 DEGRADED`;
- egress inventory entries: `10`;
- unique protocols: `HTTPS`;
- production/live: `false`.

| Source | Portfolio | Latest attempt | Operational | Measurement | Content freshness | Items | Error class | Measured note |
|---|---|---|---|---|---|---:|---|---|
| Consilium Press Releases | ACTIVE | SUCCESS | HEALTHY | CURRENT | UNKNOWN | 0 | NONE | Zero bounded watch matches; no publisher timestamp inferred. |
| European Commission Press Corner | ACTIVE | SUCCESS | HEALTHY | CURRENT | UNKNOWN | 0 | NONE | Zero bounded watch matches; no publisher timestamp inferred. |
| European Parliament Press Releases | DEGRADED | FAILED | UNAVAILABLE | CURRENT | UNKNOWN | 0 | PARSER | `RSS/Atom response is not valid XML`; retained known degraded endpoint behavior. |
| GDELT DOC 2.0 | ACTIVE | SUCCESS | HEALTHY | CURRENT | UNKNOWN | 25 | NONE | Discovery/index metadata; not independent corroboration. |
| Haberturk News | ACTIVE | FAILED | UNAVAILABLE | CURRENT | UNKNOWN | 0 | UNKNOWN | `original_url must be HTTP or HTTPS`; item URL validation/mapping discrepancy retained for review. |
| Meduza | ACTIVE | SUCCESS | HEALTHY | CURRENT | FRESH | 30 | NONE | Parseable recent publisher timestamps observed. |
| OSCE Latest News | ACTIVE | SUCCESS | HEALTHY | CURRENT | STALE | 18 | NONE | Acquisition works, but observed latest publisher timestamp exceeds configured freshness expectation. |
| RMF24 | ACTIVE | SUCCESS | HEALTHY | CURRENT | FRESH | 14 | NONE | Parseable recent publisher timestamps observed. |
| Ukrainska Pravda | ACTIVE | SUCCESS | HEALTHY | CURRENT | FRESH | 50 | NONE | Parseable recent publisher timestamps observed. |
| UK Government News and Communications | ACTIVE | SUCCESS | HEALTHY | CURRENT | FRESH | 50 | NONE | Parseable recent publisher timestamps observed. |

Operational health and content freshness are independent dimensions. In particular, OSCE is not marked unavailable merely because its observed content is stale.

## Exact Egress Inventory

| Source | Hostname | Protocol |
|---|---|---|
| GDELT DOC 2.0 | `api.gdeltproject.org` | HTTPS |
| European Commission | `ec.europa.eu` | HTTPS |
| OSCE | `feeds.osce.org` | HTTPS |
| Meduza | `meduza.io` | HTTPS |
| Haberturk | `rss.haberturk.com` | HTTPS |
| Consilium | `www.consilium.europa.eu` | HTTPS |
| European Parliament | `www.europarl.europa.eu` | HTTPS |
| GOV.UK | `www.gov.uk` | HTTPS |
| Ukrainska Pravda | `www.pravda.com.ua` | HTTPS |
| RMF24 | `www.rmf24.pl` | HTTPS |

This table records measured/governed requirements. It is not an outbound firewall rule and does not itself authorize or implement egress restriction.

## Interpretation Boundary

- a failed source path is a visible operational limitation;
- a successful source path is not continuous-health proof;
- content freshness does not determine factual truth;
- source/host/item count is not independent-origin count;
- this matrix is not proof of exhaustive global coverage.
