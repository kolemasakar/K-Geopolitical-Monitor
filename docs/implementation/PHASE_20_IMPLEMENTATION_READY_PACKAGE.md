# Phase 20 — Implementation-Ready Package

Date: 2026-09-11
Status: `PREPARED / DESIGN_AND_TEST_ARTIFACTS_ONLY / LIVE_EXECUTION_NOT_STARTED`
Base: `5714a76aaf12c77993ed5a02165c02a48d953758`
Roadmap gate: `P20_GLOBAL_SOURCE_COVERAGE_VALIDATED`

This package refines the existing Phase 20 source-coverage design into machine-contract, fixture, validation, and implementation sequencing artifacts while Phase 19 Attempt 2 continues.

It does **not** authorize live source onboarding, source activation, ingestion changes, runtime deployment, migration 033, paid resources, shared runtime, A5 activation, or canonical cutover.

## Non-negotiable semantic boundaries

```text
SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT
LANGUAGE_COUNT != INDEPENDENT_EVIDENCE_COUNT
COVERAGE_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE
COLLECTION_HEALTH != CONTENT_CREDIBILITY
P20_COVERAGE_EVIDENCE != P21_CLAIM_VERIFICATION
```

## Prepared machine contracts

The implementation package defines three machine-readable contracts:

- `docs/contracts/p20_source_record.schema.json` — canonical source registry record;
- `docs/contracts/p20_coverage_policy.schema.json` — configurable minimum-coverage policy;
- `docs/contracts/p20_coverage_report.schema.json` — deterministic coverage evaluation output.

These contracts are deliberately source-neutral. They describe metadata and coverage semantics only; no live source is enabled by their presence.

## Prepared synthetic fixtures

Synthetic fixtures under `tests/fixtures/p20/` are intentionally non-routable and must never be treated as live source configuration.

- `source_registry_valid.json` demonstrates unique sources, shared `origin_group_id`, syndication, languages, health, and active/inactive coverage roles;
- `coverage_policy_valid.json` demonstrates policy-driven independent-origin and source-count requirements;
- `coverage_report_synthetic.json` demonstrates explainable `ADEQUATE`, `MONOCULTURE_RISK`, and `DEGRADED_COLLECTION` outcomes.

All fixture endpoints use `.invalid` domains.

## Implementation sequence

### P20.0 — Existing coverage inventory and reuse map

Deliverables:

- inventory current Phase 12 source registry, adapter framework, authoritative source pack, local-language discovery and health signals;
- map existing fields to the source-record contract;
- identify missing metadata without mutating live collection;
- produce a read-only baseline export.

Exit gate:
`P20_0_EXISTING_COVERAGE_BASELINE_MAPPED`

### P20.1 — Canonical taxonomy and metadata validation

Deliverables:

- source-record parser/validator;
- deterministic primary `source_type`;
- explicit `origin_group_id` and syndication relation;
- explicit collection-health state;
- validation errors are fail-closed and field-specific.

Minimum tests:

- valid complete source record;
- missing required field;
- invalid source type;
- invalid health state;
- non-boolean `active_for_coverage`;
- copy/syndication record without origin grouping;
- inactive historical source retained but excluded from active coverage.

Exit gate:
`P20_1_SOURCE_TAXONOMY_METADATA_CONTRACT_VALIDATED`

### P20.2 — Coverage matrix and target policy

Deliverables:

- policy loader;
- geography × language × source-type matrix;
- explicit zero-coverage cells;
- policy overrides for critical cells;
- no hard-coded global minimum hidden in evaluator code.

Minimum tests:

- required cell with zero sources;
- source count met but independent-origin count not met;
- independent-origin target met;
- optional cell marked `NOT_REQUIRED_BY_POLICY`;
- inactive source excluded;
- stale/failed source separated from healthy source count.

Exit gate:
`P20_2_COVERAGE_MATRIX_POLICY_VALIDATED`

### P20.3 — Independence, redundancy and monoculture

Required metrics:

```text
SOURCE_COUNT
INDEPENDENT_ORIGIN_COUNT
COPY_CHAIN_COUNT
DOMINANT_ORIGIN_SHARE
REDUNDANCY_SCORE
MONOCULTURE_RISK
```

Deterministic rules:

- two source records sharing one `origin_group_id` count as one independent origin;
- copies may increase redundancy but never independent-origin count;
- dominant-origin share is computed over active coverage-eligible sources;
- `MONOCULTURE_RISK` must expose a reason string, not only a score.

Minimum tests:

- two copies of one origin;
- two independent origins;
- mixed original/copy portfolio;
- one dominant origin with many copies;
- unknown origin relation handled explicitly, never assumed independent.

Exit gate:
`P20_3_SOURCE_INDEPENDENCE_MONOCULTURE_VALIDATED`

### P20.4 — Collection health and latency semantics

Canonical health states:

```text
HEALTHY
DEGRADED
STALE
UNREACHABLE
DISABLED_EXPECTED
DISABLED_UNEXPECTED
NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY
UNKNOWN
```

Minimum tests:

- healthy collector with no recent content is not reported as unreachable;
- stale collector cannot satisfy healthy-source requirement;
- disabled-expected source does not create an incident but remains visible;
- disabled-unexpected source creates degraded-collection evidence;
- unknown state fails closed for coverage sufficiency where policy requires health.

Exit gate:
`P20_4_COLLECTION_HEALTH_LATENCY_VALIDATED`

### P20.5 — Source onboarding contract

A source cannot become `ACTIVE_FOR_COVERAGE=true` until it has:

- deterministic source ID;
- taxonomy metadata;
- geography/language metadata;
- public/legal collection classification;
- origin/syndication classification or explicit `UNKNOWN`;
- expected latency/frequency;
- health semantics;
- synthetic fixture/test evidence;
- rollback/disable behavior;
- explicit authorization for any secret, paid resource or non-public dependency.

During P19, implementation is limited to validation code and fixtures; no live onboarding is authorized.

Exit gate:
`P20_5_SOURCE_ONBOARDING_CONTRACT_VALIDATED`

### P20.6 — Coverage evaluation and reporting

Report must expose:

```text
GLOBAL_SUMMARY
REGION_GAPS
LANGUAGE_GAPS
SOURCE_TYPE_GAPS
MONOCULTURE_WARNINGS
STALE_OR_FAILED_SOURCES
LATENCY_OUTLIERS
MISSING_EXPECTED_SOURCES
CHANGES_SINCE_PREVIOUS_REPORT
```

Every non-adequate cell must carry inspectable reason codes.

Exit gate:
`P20_6_COVERAGE_EVALUATION_REPORTING_VALIDATED`

## Validation matrix

| Case | Expected result |
|---|---|
| source_count=3, independent_origins=1, minimum_independent=2 | `MONOCULTURE_RISK` |
| source_count=2, independent_origins=2, all healthy, policy met | `ADEQUATE` |
| policy required, no active sources | `MISSING_EXPECTED_COVERAGE` |
| enough registered sources, most stale/unreachable | `DEGRADED_COLLECTION` |
| cell excluded by policy | `NOT_REQUIRED_BY_POLICY` |
| health/origin metadata indeterminate | `UNKNOWN` unless stricter fail-closed policy maps to gap |

## Acceptance evidence expected later

P20 final acceptance should include:

- schema/contract validation tests;
- deterministic matrix evaluation tests;
- synthetic monoculture and degraded-collection tests;
- read-only baseline over the existing source portfolio;
- operator-readable report;
- machine-readable report;
- proof that no source-count amplification through copies is misreported as independent coverage;
- proof that collection failure cannot silently masquerade as geopolitical silence.

## Current boundary

```text
P20_DESIGN = IMPLEMENTATION_READY
P20_TEST_ARTIFACTS = PREPARED
P20_EXECUTION = NOT_STARTED
LIVE_SOURCE_EXPANSION = NO
LIVE_INGEST_CHANGE = NO
RUNTIME_DEPLOYMENT = NO
MIGRATION_033 = NOT_CREATED_NOT_PREAUTHORIZED
BETA_PAID_RESOURCES_AUTHORIZED = NO
A5_ACTIVATION = NO
```
