# Phase 20 — Source Coverage & Collection Quality Design Specification

Date: 2026-09-11
Status: `DESIGN_ONLY / P20 EXECUTION NOT STARTED`
Roadmap gate: `P20_GLOBAL_SOURCE_COVERAGE_VALIDATED`

This specification prepares P20 while P19 real-soak evidence accumulates. It does **not** authorize live source onboarding, source expansion, ingestion changes, runtime deployment, or P20 gate execution.

## Objective

Make KGM coverage measurable so the system can answer both:

- what information it sees; and
- where its information picture is weak, stale, dependent on one origin, or absent.

P20 extends rather than replaces earlier source work. Existing Phase 12 source portfolio, adapter framework, authoritative source pack, local-language discovery, and source-health foundations must be inventoried and reused before new abstractions are introduced.

## Design principles

- coverage is a measurable property, not a source-count target;
- independent origins matter more than duplicated/syndicated copies;
- a quiet feed must be distinguishable from a quiet geopolitical environment;
- local-language and regional sources must be visible in the coverage model;
- source reliability and source independence are separate dimensions;
- collection health must not be conflated with content credibility;
- P20 produces coverage evidence, not truth adjudication; claim-level verification remains P21 scope;
- no new paid resource or shared-runtime dependency may be introduced during beta without separate authorization.

## Canonical source taxonomy

Minimum source types:

```text
OFFICIAL_GOVERNMENT
INTERNATIONAL_ORGANIZATION
WIRE_SERVICE
NATIONAL_MEDIA
REGIONAL_LOCAL_MEDIA
DEFENSE_SECURITY
THINK_TANK_RESEARCH
PUBLIC_OSINT
ECONOMIC_ENERGY
SANCTIONS_REGULATORY
APPROVED_PUBLIC_SOCIAL
OTHER_EXPLICITLY_CLASSIFIED
```

The taxonomy should permit multiple roles while retaining one canonical primary type where required for deterministic reporting.

## Minimum source metadata contract

Required design fields:

```text
SOURCE_ID
DISPLAY_NAME
PRIMARY_DOMAIN_OR_ENDPOINT
COUNTRY
REGION
SUBREGION
LANGUAGE
SOURCE_TYPE
RELIABILITY_CLASS
UPDATE_FREQUENCY
COLLECTION_STATUS
COVERAGE_ROLE
ORIGIN_GROUP_ID
SYNDICATION_OR_COPY_RELATION
COLLECTION_METHOD
EXPECTED_LATENCY
LAST_SUCCESS_AT
LAST_ITEM_AT
HEALTH_STATUS
ACTIVE_FOR_COVERAGE
```

Optional/extended fields should include jurisdiction, topic specialization, ownership/provenance notes, access restrictions, and reason for inclusion/exclusion.

### Semantics

`RELIABILITY_CLASS` describes historically/administratively assessed source reliability; it does not imply that every claim from the source is true.

`ORIGIN_GROUP_ID` and `SYNDICATION_OR_COPY_RELATION` prevent multiple republishes of one origin from being counted as independent coverage.

`ACTIVE_FOR_COVERAGE` allows a source to remain registered for provenance/history while being excluded from current coverage calculations.

## Coverage dimensions

Coverage must be computable across at least:

```text
GEOGRAPHY
LANGUAGE
SOURCE_TYPE
TOPIC_ROLE
ORIGIN_INDEPENDENCE
COLLECTION_HEALTH
LATENCY
REDUNDANCY
```

Recommended output unit:

```text
coverage_cell = geography × language × source_type [× topic_role where applicable]
```

Each cell should expose source count, independent-origin count, healthy-source count, stale-source count, and coverage status.

## Proposed P20 decomposition

### P20.0 — Existing Coverage Inventory & Reuse Map

Goal: establish what already exists before adding anything.

Design/entry evidence:

- inventory Phase 12 source registry/portfolio structures;
- map current adapters, authoritative packs, local-language discovery and health signals;
- identify duplicate concepts and reusable fields;
- produce current coverage baseline without changing live collection.

Proposed gate:
`P20_0_EXISTING_COVERAGE_BASELINE_MAPPED`

### P20.1 — Canonical Source Taxonomy & Metadata Contract

Goal: define deterministic source classification and metadata validation.

Proposed gate:
`P20_1_SOURCE_TAXONOMY_METADATA_CONTRACT_VALIDATED`

### P20.2 — Coverage Matrix & Target Policy

Goal: represent gaps by geography, language and source type.

Design rules:

- targets are policy/configuration, not hard-coded global constants;
- critical regions may have stricter minimum independent-origin requirements;
- zero/low coverage must be explicit rather than silently omitted.

Proposed gate:
`P20_2_COVERAGE_MATRIX_POLICY_VALIDATED`

### P20.3 — Independence, Redundancy & Monoculture Model

Goal: distinguish genuinely independent coverage from copies/syndication.

Required concepts:

```text
INDEPENDENT_ORIGIN_COUNT
COPY_CHAIN_COUNT
REDUNDANCY_SCORE
MONOCULTURE_RISK
DOMINANT_ORIGIN_SHARE
```

Proposed gate:
`P20_3_SOURCE_INDEPENDENCE_MONOCULTURE_VALIDATED`

### P20.4 — Collection Health, Latency & Missing-Source Semantics

Goal: prevent collection failure from looking like geopolitical silence.

Required states should distinguish at least:

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

Proposed gate:
`P20_4_COLLECTION_HEALTH_LATENCY_VALIDATED`

### P20.5 — Source Onboarding Contract

Goal: define how a new source becomes coverage-eligible.

Before activation, require:

- explicit taxonomy and jurisdiction/language metadata;
- collection method and legal/public-access classification;
- deterministic source ID;
- origin/syndication classification where known;
- expected frequency/latency;
- health-check behavior;
- fixture/test evidence;
- rollback/disable semantics;
- no secret or paid-resource assumption unless separately approved.

During the current P19 soak, P20.5 remains design/test-fixture only; no new live source is enabled.

Proposed gate:
`P20_5_SOURCE_ONBOARDING_CONTRACT_VALIDATED`

### P20.6 — Coverage Evaluation & Reporting

Goal: produce reproducible machine-readable and operator-readable coverage reports.

Recommended report sections:

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

Proposed gate:
`P20_6_COVERAGE_EVALUATION_REPORTING_VALIDATED`

### P20.7 — Phase 20 Acceptance

Required final evidence:

- coverage is measurable by region, language and source type;
- material gaps are explicit;
- independent-origin coverage is distinguishable from copy amplification;
- stale/failed collection cannot silently masquerade as low event activity;
- current source set can be evaluated deterministically;
- no unapproved paid/shared-runtime dependency was introduced.

Final gate:
`P20_GLOBAL_SOURCE_COVERAGE_VALIDATED`

## Suggested coverage status semantics

A coverage cell should resolve to an explainable state such as:

```text
ADEQUATE
THIN
MONOCULTURE_RISK
DEGRADED_COLLECTION
MISSING_EXPECTED_COVERAGE
NOT_REQUIRED_BY_POLICY
UNKNOWN
```

Avoid a single opaque numeric score as the only representation. Numeric metrics may support the status, but the reasons must remain inspectable.

## Boundary with P21

P20 answers:

> Do we have healthy, diverse, independent-enough collection coverage for this information space?

P21 answers:

> Given the evidence actually collected, how well is a specific claim supported, contradicted, and verified?

P20 must not preempt P21 by treating source reputation or source count as proof of a claim.

## Entry condition

Operational P20 work starts only after the project accepts the required P19 gate/transition decision. Until then:

```text
P20_DESIGN = PREPARED
P20_EXECUTION = NOT_STARTED
LIVE_SOURCE_EXPANSION = NO
LIVE_INGEST_CHANGE = NO
```
