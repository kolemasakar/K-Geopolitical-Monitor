# P12.5 — Source Health, Freshness and Egress Inventory Result

Date: 2026-09-01
Status: `VALIDATED_WITH_MEASURED_DEGRADATION`
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`
Implementation candidate / validation anchor: `92d0c0516351e2af7ba836d3ae711dd414d22023`

## Validation Evidence

- x64 CI run `33533313297`, job `99941475948`: `382 passed, 1 warning / SUCCESS`;
- native ARM64 run `33533313313`, job `99941475266`: real `aarch64`, `382 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd checks PASS;
- controlled-live run `33533313654`, job `99941475574`: workflow `SUCCESS`, complete 10-source measurement persisted and emitted;
- controlled-live matrix: `docs/implementation/P12_5_CONTROLLED_LIVE_SOURCE_HEALTH_MATRIX.md`.

The warning is the existing FastAPI/Starlette TestClient deprecation warning and is not a P12.5 functional failure.

## Gate Result

P12.5 is a measurement/inventory gate, not an all-sources-healthy gate. The required source network was fully measured and operational failures/staleness remained explicit.

Measured result:
- governed source paths: `10`;
- measured source paths: `10`;
- unmeasured: `0`;
- source collection attempts: `8 SUCCESS / 2 FAILED`;
- unique outbound hosts: `10`;
- outbound protocols: `HTTPS` only;
- canonical DB migration: `NONE`;
- credentials: `NONE`;
- paid providers: `NONE_APPROVED`.

## Measured Operational Findings

- European Parliament Press Releases: latest attempt `FAILED`, operational state `UNAVAILABLE`, error class `PARSER`, error `RSS/Atom response is not valid XML`; governed portfolio state remains `DEGRADED` from P12.3. No anti-bot bypass is authorized.
- Haberturk News: latest attempt `FAILED`, operational state `UNAVAILABLE`, current error class `UNKNOWN`, error `original_url must be HTTP or HTTPS`; governed portfolio state remains `ACTIVE`. This measured discrepancy is retained for P12.6 review rather than silently changing governance in P12.5.
- OSCE Latest News: acquisition succeeded and operational state is `HEALTHY`, while observed publisher-content freshness is `STALE`; transport health and content freshness remain separate dimensions.
- Consilium and European Commission: acquisition succeeded with zero bounded watch matches; content freshness remains `UNKNOWN`, not inferred from collection time.
- GDELT, Meduza, RMF24, Ukrainska Pravda and GOV.UK succeeded in the controlled probe; observed content freshness was `FRESH` where a parseable publication timestamp was captured.

These are controlled observations, not continuous-uptime guarantees.

## Egress Inventory Result

Measured required HTTPS hostnames:
- `api.gdeltproject.org`;
- `ec.europa.eu`;
- `feeds.osce.org`;
- `meduza.io`;
- `rss.haberturk.com`;
- `www.consilium.europa.eu`;
- `www.europarl.europa.eu`;
- `www.gov.uk`;
- `www.pravda.com.ua`;
- `www.rmf24.pl`.

The inventory is factual input for a separate restriction decision. P12.5 does not deploy an outbound allowlist and does not revoke the existing owner-approved broad-egress exception.

## Epistemic / Coverage Result

- operational health does not change claim truth;
- freshness does not promote or demote factual verification;
- source/host/language/item count does not create independent-origin count;
- source failure does not prove an event did not occur;
- successful acquisition does not prove exhaustive coverage;
- `GLOBAL` remains scope, not proof of completeness.

## Runtime / Security Result

- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`;
- public KGM ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- private GPT backend Action: `NOT_CONNECTED`;
- broad outbound egress: retained explicit owner-approved candidate exception pending a separate decision.

## Gate Decision

`P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

P12.6 Phase 12 Validation Matrix is the next activity. P12.5 measured findings must remain visible during P12.6 and must not be converted into stronger truth, coverage or production claims.
