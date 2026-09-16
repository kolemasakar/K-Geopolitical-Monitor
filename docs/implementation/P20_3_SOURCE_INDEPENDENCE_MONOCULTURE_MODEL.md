# P20.3 — Source Independence, Redundancy & Monoculture Model

Date: 2026-09-16
Status: `IMPLEMENTED / VALIDATION_PENDING`
Gate: `P20_3_SOURCE_INDEPENDENCE_MONOCULTURE_VALIDATED`

## Objective

Define a deterministic, fail-closed model for distinguishing portfolio diversity from copy/syndication amplification without treating publisher, domain, language, adapter, or source counts as proof of independent origin.

P20.3 is contract/evidence/test-fixture work only. It does not onboard sources, change live ingest, deploy runtime code, restart services, create migration `033`, authorize paid resources, or activate shared runtime.

## Relationship to P13 provenance and claim independence

P20.3 does not replace P13.2/P13.3.

- P13.2/P13.3 govern item/claim provenance, evidence relations, and claim-scoped independence assessment.
- P20.3 governs **coverage-topology accounting** for a source portfolio/cell.
- P20 may reuse explicit provenance evidence, but absence of a known derivation path is never converted into independence.
- P20 portfolio diversity cannot promote factual verification or claim confidence.

Permanent rule:

```text
P20_PORTFOLIO_DIVERSITY != P13_CLAIM_CORROBORATION
```

## Source-origin observation contract

Each source observation records:

- `source_id`;
- `origin_group_id` — nullable unless one explicit stable underlying-origin grouping is supported;
- `origin_identity_state`:
  - `EXPLICIT_SINGLE_ORIGIN`;
  - `UNKNOWN_ORIGIN`;
  - `MIXED_ORIGIN`;
- `syndication_or_copy_relation`:
  - `ORIGINAL`;
  - `SYNDICATED_COPY`;
  - `AGGREGATOR_COPY`;
  - `DERIVED`;
  - `UNKNOWN` / `null`;
- `provenance_references` — evidence references supporting non-unknown classification.

A source that routinely mixes original, syndicated, translated, aggregated, or otherwise derived material must not be forced into one source-wide origin group. `MIXED_ORIGIN` is an explicit fail-closed state.

## Completeness rule

A cell has `evaluation_completeness=COMPLETE` only when every source observation has:

- `origin_identity_state=EXPLICIT_SINGLE_ORIGIN`;
- non-null `origin_group_id`;
- a non-unknown syndication/copy relation.

If one or more sources are unresolved or mixed, the evaluation is `PARTIAL` (or `UNKNOWN` when nothing is known), and precise aggregate independence metrics are withheld.

This prevents false precision from partial provenance.

## Deterministic metrics

For a COMPLETE cell:

```text
INDEPENDENT_ORIGIN_COUNT = count(distinct origin_group_id)
COPY_CHAIN_COUNT = count(relation in {SYNDICATED_COPY, AGGREGATOR_COPY, DERIVED})
DOMINANT_ORIGIN_SHARE = max(source_count_per_origin_group) / source_count
REDUNDANCY_SCORE = source_count / independent_origin_count
```

`REDUNDANCY_SCORE` is a descriptive amplification ratio, not a quality score and not a truth score.

For incomplete provenance:

```text
INDEPENDENT_ORIGIN_COUNT = null
COPY_CHAIN_COUNT = null
DOMINANT_ORIGIN_SHARE = null
REDUNDANCY_SCORE = null
```

`known_origin_group_count` may still be reported as an explicit lower-bound observation, but must not be relabeled `independent_origin_count`.

## Monoculture state

For COMPLETE cells:

- one source only -> `NO_REDUNDANCY`;
- more than one source and exactly one explicit origin group -> `CONFIRMED_MONOCULTURE`;
- more than one explicit origin group -> `CONFIRMED_DIVERSE`.

For incomplete provenance -> `UNKNOWN`.

This state is descriptive. Policy risk is evaluated separately using P20.2 thresholds.

## Policy-linked monoculture risk

P20.3 reuses the P20.2 fields:

- `minimum_independent_origin_count`;
- `maximum_dominant_origin_share`.

When provenance metrics and both thresholds are available:

```text
MONOCULTURE_RISK =
  independent_origin_count < minimum_independent_origin_count
  OR dominant_origin_share > maximum_dominant_origin_share
```

If provenance metrics are incomplete or the governing threshold is unset, risk remains `null`; no default global threshold is invented.

## Current governed-source result

The current ten-source P20.0/P20.1 portfolio has no canonical source-level `origin_group_id` or syndication/copy classifications. Therefore:

```text
KNOWN_ORIGIN_SOURCE_COUNT = 0
UNKNOWN_ORIGIN_SOURCE_COUNT = 10
INDEPENDENT_ORIGIN_COUNT = null
COPY_CHAIN_COUNT = null
DOMINANT_ORIGIN_SHARE = null
REDUNDANCY_SCORE = null
MONOCULTURE_STATE = UNKNOWN
```

This is the correct P20.3 current-state result. Ten governed sources are not ten independent origins.

Authoritative evidence:
`docs/evidence/P20_3_CURRENT_SOURCE_INDEPENDENCE_BASELINE_2026-09-16.json`.

## Synthetic validation cases

The fixture validates:

- three explicitly distinct origins -> `CONFIRMED_DIVERSE`;
- three source paths tied to one explicit origin -> `CONFIRMED_MONOCULTURE`;
- one explicit origin -> `NO_REDUNDANCY` rather than monoculture amplification;
- one unresolved source -> precise metrics withheld;
- one mixed-origin source -> precise metrics withheld;
- configurable P20.2 thresholds produce deterministic `true/false/null` monoculture risk.

## Epistemic boundaries

```text
SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT
DOMAIN_COUNT != INDEPENDENT_ORIGIN_COUNT
LANGUAGE_COUNT != INDEPENDENT_ORIGIN_COUNT
ADAPTER_COUNT != INDEPENDENT_ORIGIN_COUNT
NO_KNOWN_DERIVATION != INDEPENDENT
COVERAGE_DIVERSITY != FACTUAL_VERIFICATION
REDUNDANCY_SCORE != QUALITY_SCORE
MONOCULTURE_RISK != CLAIM_FALSEHOOD
```

P13.5/P13.6 remains the factual-verification authority.

## Acceptance criteria

P20.3 is eligible for validation when tests demonstrate that:

- the current 10-source portfolio remains `UNKNOWN` for source-level independence rather than being inferred independent;
- complete explicit origin evidence yields deterministic independent-origin, copy-chain, dominant-share and redundancy metrics;
- syndication/aggregation/derivation does not create additional independent origins;
- unknown or mixed origin blocks precise independence and monoculture metrics;
- P20.2 thresholds, rather than hard-coded constants, control monoculture risk;
- P13 claim-level independence remains a separate semantic authority;
- no live-source/runtime/paid/shared-resource boundary changes occur.

On validation, the next gate is `P20_4_COLLECTION_HEALTH_LATENCY_VALIDATED`.

## Validation execution note

GitHub Actions run `35094320076` became stale during the full pytest step without reporting a failure or producing a completed log artifact. A documentation-only head refresh was used to trigger a fresh validation run against the current canonical `main`; no P20.3 contract, evidence, fixture, metric, runtime, or source semantics changed.
