# P12.3 — Priority Authoritative Source Pack

Date: 2026-09-01
Status: `VALIDATED_WITH_EXPLICIT_DEGRADATION`
Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`
Validation anchor: `038122e44139d6ff23bc5d79bb50a8dee3c38cde`

## Objective

Add a materially broader public/free authoritative source pack without weakening P12.1 governance, P12.2 acquisition controls or epistemic boundaries.

## Pack

- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

Existing Consilium RSS remains a previously validated controlled-live integration and is not duplicated.

## Implementation

- `src/kgeopolitical_monitor/authoritative_source_pack.py`;
- `tests/test_authoritative_source_pack.py`;
- deterministic RSS fixture `tests/fixtures/p12_3/authoritative.rss.xml`;
- deterministic Atom fixture `tests/fixtures/p12_3/authoritative.atom.xml`;
- controlled-live script `scripts/p12_3_live_source_smoke.py`;
- controlled-live workflow `.github/workflows/p12_3-controlled-live-smoke.yml`.

All sources have explicit P12.1 governance: canonical ID/name/publisher, source class/role, region/language scope, public-anonymous/free access, freshness/cadence, exact P12.2 adapter ID/version, HTTPS outbound hostname, PUBLIC classification, origin/independence constraints and approved review state.

Governance install is idempotent when unchanged and fails closed on pre-existing drift.

## Validation

Validation anchor `038122e44139d6ff23bc5d79bb50a8dee3c38cde`:
- x64 run `33527433110`, job `99921745359`: `356 passed, 1 warning / SUCCESS`;
- native ARM64 run `33527433197`, job `99921746285`: `356 passed, 1 warning / SUCCESS`;
- controlled-live repeat run `33527433106`, job `99921745640`: 3 source successes, 1 European Parliament failure/degradation, workflow SUCCESS.

The European Parliament official RSS directory resolves to the configured official endpoint, but the unattended runner receives anti-bot HTML rather than RSS XML. P12.2 parsing therefore fails closed. The source is governed as `DEGRADED`; no anti-bot bypass or third-party canonical mirror is approved.

Detailed result: `docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md`.
Controlled-live evidence: `docs/implementation/P12_3_CONTROLLED_LIVE_SOURCE_MATRIX.md`.

## Epistemic Boundary

- authoritative-source status establishes what an institution published/stated, not automatically the underlying event;
- publisher/domain/adapter/item count is not independent-origin count;
- reposts/citations/translations do not create independent corroboration;
- acquisition/parser success or failure is operational state, not verification promotion;
- probe success is not continuous uptime or exhaustive coverage evidence.

## Security / Runtime Boundary

- public anonymous read-only HTTPS only;
- no credentials;
- paid providers `NONE_APPROVED`;
- runtime storage `PROJECT_LOCAL_ONLY`;
- public KGM ingress not approved/deployed;
- production/live `NOT_OPERATIONAL`.

## Next Activity

`P12.4_LOCAL_LANGUAGE_AND_MEDIA_DISCOVERY_PACK / NEXT_NOT_STARTED`.
