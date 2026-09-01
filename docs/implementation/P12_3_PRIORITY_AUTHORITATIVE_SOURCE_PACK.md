# P12.3 — Priority Authoritative Source Pack

Date: 2026-09-01
Status: `IMPLEMENTED / VALIDATION_PENDING`
Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

## Objective

Add a materially broader public/free authoritative source pack without weakening P12.1 governance, P12.2 acquisition controls or epistemic boundaries.

## Initial Pack

- European Commission Press Corner;
- European Parliament Press Releases;
- UK Government News and Communications;
- OSCE Latest News.

Existing Consilium RSS remains a previously validated controlled-live integration and is not duplicated inside this pack.

## Implementation

Module:
`src/kgeopolitical_monitor/authoritative_source_pack.py`

Tests:
`tests/test_authoritative_source_pack.py`

Deterministic fixtures:
- `tests/fixtures/p12_3/authoritative.rss.xml`;
- `tests/fixtures/p12_3/authoritative.atom.xml`.

## Governance

Every pack source has explicit:

- canonical source ID/name and publisher;
- `Official sources` class and `OFFICIAL` role;
- region/language scope;
- public-anonymous/free access;
- freshness/cadence;
- P12.2 adapter ID/version;
- exact HTTPS outbound hostname;
- PUBLIC data classification;
- origin characteristics and independence constraints;
- owner/reviewer and APPROVED review state.

The install operation is idempotent when governance is unchanged. If an existing current portfolio version differs from the source-pack contract, onboarding fails closed and requires explicit review rather than silently creating a new version.

## Adapter Path

All four sources use `PublicFeedAdapterV2` and `FrameworkLiveSourceCollector` from P12.2. No parallel ingestion path, table or truth store is introduced.

## Validation Design

Deterministic tests cover:

- unique pack identity;
- public/free/non-sensitive constraints;
- deterministic adapter identity;
- explicit governance requirement before collection;
- idempotent governance installation;
- governance drift fail-closed;
- deterministic RSS/Atom parsing through the pack;
- four-source successful fixture collection;
- one-source failure isolation with `PARTIAL` collection status;
- no independent-origin, verification or coverage-confidence promotion.

CI remains network-independent. Controlled-live endpoint checks are separate evidence and must not be substituted for deterministic regression.

## Epistemic Boundary

Authoritative-source status establishes what an institution published or stated. It does not automatically prove the underlying event claim. Source/domain/adapter count is not independent-origin count. Reposts, citations, translations and statements derived from one underlying origin require provenance clustering.

## Security / Runtime Boundary

- only read-only HTTPS public-anonymous acquisition is in scope;
- no credentials are introduced;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- public ingress: unchanged/not deployed;
- production/live: `NOT_OPERATIONAL`.

## Gate State

Implementation exists, but the gate remains `VALIDATION_PENDING` until full project regression and controlled-live validation evidence are reviewed.
