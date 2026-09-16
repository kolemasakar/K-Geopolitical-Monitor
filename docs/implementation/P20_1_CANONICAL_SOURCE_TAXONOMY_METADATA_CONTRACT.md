# P20.1 — Canonical Source Taxonomy & Metadata Contract

Date: 2026-09-16
Status: `IMPLEMENTED / VALIDATION_PENDING`
Gate: `P20_1_SOURCE_TAXONOMY_METADATA_CONTRACT_VALIDATED`

## Scope

P20.1 defines deterministic source classification and metadata semantics for the existing P20.0 governed baseline. It does not onboard sources, change live ingest, deploy runtime code, restart services, create migration 033, authorize paid resources, or activate shared runtime.

Authoritative inputs:

- `docs/evidence/P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json`
- `docs/evidence/P20_0_EXISTING_COVERAGE_REUSE_MAP_2026-09-16.json`
- Phase 12 source portfolio / adapter / source-health governance
- P13 provenance semantics for evidence references only

Machine-readable outputs:

- `docs/contracts/p20_1_source_record.schema.json`
- `docs/evidence/P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json`

## Contract decisions

### 1. Identity

`source_id` is preserved exactly from P20.0. P20.1 does not manufacture new source identities for endpoint aliases or historical measurements.

### 2. Source taxonomy

One deterministic `source_type` is required for reporting. The current baseline maps to:

- EU institutional sources and OSCE -> `INTERNATIONAL_ORGANIZATION`;
- UK Government -> `OFFICIAL_GOVERNMENT`;
- GDELT DOC 2.0 -> `PUBLIC_OSINT`;
- Haberturk, Meduza, RMF24 and Ukrainska Pravda -> `NATIONAL_MEDIA`.

The mapping is an administrative coverage taxonomy. It is not a reliability score, credibility judgment, factual-verification result, or independence assessment.

### 3. Geography and language

P12 `region_scope` and `language_scope` are multi-valued and remain multi-valued.

`geography.legacy_region_scope` preserves the exact governed P12 labels. `countries`, `regions` and `subregions` exist as normalized P20 containers but P20.1 does not populate them by guessing from labels. A later explicit mapping may populate them without deleting the legacy scope.

`languages` preserves P12 values including `multi`; P20.1 does not convert `multi` into an invented language list.

### 4. Frequency and latency

`collection_cadence_minutes` maps to `update_frequency_minutes`.

`expected_freshness_minutes` maps to `expected_latency_minutes` as compatibility metadata only. It is not newly asserted as an observed runtime SLA.

### 5. Collection method

Collection method is derived only from explicit adapter identity using the deterministic mapping in the reconciliation evidence. No network probing or live-source mutation is required.

### 6. Health versus lifecycle state

P12 availability is not silently reinterpreted as a collection lifecycle decision.

- `DEGRADED` maps to P20 `health_status=DEGRADED`.
- P12 `ACTIVE` does not prove item-level health, therefore maps to `health_status=UNKNOWN` in the P20.1 normalization contract.
- `collection_status` remains `UNKNOWN` until an explicit lifecycle field governs it.

This keeps collection health separate from content credibility and avoids turning source governance into a truth operator.

### 7. Fields that must remain unknown

The following fields are explicit but nullable because P20.0 does not supply evidence sufficient to determine them:

- `reliability_class`;
- `origin_group_id`;
- `syndication_or_copy_relation`;
- `active_for_coverage`.

`active_for_coverage` is reserved for P20.2 policy; it is not inferred from `availability_state`.

Origin/syndication fields may only be populated from explicit provenance evidence and must not be inferred from publisher, domain, language, adapter, or item counts.

## Haberturk endpoint reconciliation

Canonical current governed endpoint:

`www.haberturk.com`

Historical P12.5 measured endpoint:

`rss.haberturk.com`

P20.1 preserves the historical hostname as `historical_endpoint_aliases` and does not rewrite the P12.5 measurement. Both refer to the same governed `source_id=haberturk-tr` unless future evidence explicitly establishes otherwise.

## Permanent non-equivalence boundaries

```text
SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT
LANGUAGE_COUNT != INDEPENDENT_EVIDENCE_COUNT
COVERAGE_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE
COLLECTION_HEALTH != CONTENT_CREDIBILITY
P20_COVERAGE_EVIDENCE != CLAIM_VERIFICATION
```

Canonical factual verification remains governed by P13.5/P13.6.

## Acceptance criteria

P20.1 is eligible for validation when tests demonstrate that:

- all ten P20.0 source IDs have exactly one deterministic P20 source type;
- all existing adapter IDs have exactly one explicit collection-method mapping;
- multi-valued region and language scopes are not collapsed;
- unknown origin/syndication/coverage-policy fields remain nullable and uninferred;
- Haberturk endpoint drift is preserved as history rather than overwritten;
- no live-source expansion, runtime deployment, service restart, migration 033, paid-resource authorization or shared-runtime activation is introduced.

On validation, the next gate is `P20_2_COVERAGE_MATRIX_POLICY_VALIDATED`.
