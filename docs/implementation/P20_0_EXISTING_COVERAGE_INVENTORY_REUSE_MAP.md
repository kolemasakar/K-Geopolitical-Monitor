# P20.0 — Existing Coverage Inventory & Reuse Map

Date: 2026-09-16
Status: `IMPLEMENTED / VALIDATION_CANDIDATE`
Gate: `P20_0_EXISTING_COVERAGE_BASELINE_MAPPED`
Canonical base: `5c9e2b0dc8f7741c08e035f2f3f38f6afa3ced93`

## Goal

Establish exactly what source/coverage capability already exists before P20 introduces any new taxonomy, source metadata, source onboarding or coverage-evaluation abstraction.

P20.0 is read-only. It does not onboard sources, change ingestion, deploy runtime code, allocate migration `033`, activate shared runtime, or authorize paid resources.

## Reproducible current baseline

The current governed source network is reconstructed in a temporary project-local database using the existing canonical installer:

`install_phase12_health_probe_governance(...)`

Result:

```text
GOVERNED_SOURCE_PATHS = 10
ACTIVE = 9
DEGRADED = 1
PUBLIC_ANONYMOUS = 10
FREE = 10
PUBLIC_DATA = 10
APPROVED = 10
PAID_PROVIDER_APPROVED = 0
```

Machine-readable evidence:

- `docs/evidence/P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json`
- `docs/evidence/P20_0_EXISTING_COVERAGE_REUSE_MAP_2026-09-16.json`

## Existing source network

The reusable P12 network consists of:

- baseline integrations: Consilium and GDELT DOC 2.0;
- authoritative pack: European Commission, European Parliament, GOV.UK, OSCE;
- local-language discovery pack: Ukrainska Pravda, Meduza, RMF24, Haberturk.

Existing language labels are `en`, `multi`, `uk`, `ru`, `pl`, `tr`.

Existing region labels are governance scope labels, not a normalized P20 geography taxonomy. They include EU/Europe, UK, OSCE/Eurasia, Global, Ukraine/Eastern Europe, Russia, Poland/Central Europe, and Turkey/Black Sea/Middle East.

## Reuse decisions

### Reuse directly

- `source_portfolio` for versioned source governance metadata;
- `adapter_framework` for read-only HTTPS adapter identity and collection contracts;
- `authoritative_source_pack` and `local_language_discovery_pack` for governed source definitions;
- `source_health_egress` for operational health, measurement freshness, content freshness and egress inventory;
- `operational_coverage` for contracts, snapshots, limitations and `SATISFIED/GAP/UNAVAILABLE/STALE/UNKNOWN/UNMEASURED` semantics;
- `recovery_coverage` for explicit post-gap covered/uncovered interval semantics;
- `region_language_coverage` as a partial geography/language foundation.

### Reuse only with explicit mapping

- P12 `source_class` + `source_role` are inputs to P20 source taxonomy, not the P20 taxonomy itself;
- `region_scope` and `language_scope` are multi-valued governance scope and require P20 normalization rules;
- collection cadence/freshness can inform update-frequency and latency policy but are not equivalent to end-to-end latency;
- adapter identity can derive collection method only through an explicit mapping contract.

### Do not infer

P20.0 explicitly refuses to derive the following from publisher/domain/adapter/source counts:

```text
origin_group_id
syndication_or_copy_relation
independent_origin_count
active_for_coverage
```

Semantic provenance already exists downstream, but it cannot be collapsed into a guessed source-level origin group. This preserves the permanent boundary:

`SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT`.

## Existing coverage machinery

P11/P12/P19 already provide substantial P20 foundations:

- source identity and availability coverage;
- region/language attribution;
- source health and freshness;
- immutable coverage snapshots and explicit limitations;
- recovery-window coverage after missed intervals;
- downstream semantic provenance and independence evidence.

P20 therefore extends these components rather than creating a parallel coverage stack.

## Current gaps reserved for later P20 gates

P20.1 must define deterministic source taxonomy and metadata mapping, including country/subregion normalization, source type, coverage role, and coverage eligibility.

P20.3 must define source-level independence/redundancy/monoculture semantics without promoting publisher/domain counts into origin counts.

P20.4 will compose existing health/freshness/recovery signals into the canonical P20 collection-health states.

P20.5 will define onboarding/disable semantics.

P20.6 will define deterministic coverage reports over the validated contracts.

## Historical reconciliation item

The historical P12.5 health matrix recorded Haberturk egress as `rss.haberturk.com`; the current governed source spec resolves to `www.haberturk.com`.

P20.0 does not silently choose one historical value as truth. The drift is retained as an explicit P20.1 metadata-reconciliation item.

## Draft PR #78 disposition

Draft PR #78 contains useful candidate P20 schemas, synthetic fixtures and semantic-boundary tests, but it was prepared before P19 closure and is stale relative to current canonical main.

P20.0 classifies it as `REFERENCE_ONLY_STALE`. It must not be merged directly. Individual artifacts may be reconciled into the P20.1/P20.2/P20.6 owning gates after review against the current baseline.

## Acceptance candidate

P20.0 is eligible to close when tests prove:

- the deterministic governed baseline contains the same 10 source IDs as the committed machine-readable baseline;
- no source is silently added by the inventory;
- all current sources preserve public/free/non-paid governance boundaries;
- existing components and field mappings are explicit;
- absent P20 concepts remain absent rather than inferred;
- migration `033` remains not created/preauthorized;
- no runtime/live mutation occurs.

Next gate after validation:

`P20_1_SOURCE_TAXONOMY_METADATA_CONTRACT_VALIDATED`
