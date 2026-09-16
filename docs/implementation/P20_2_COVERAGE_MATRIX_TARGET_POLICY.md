# P20.2 — Coverage Matrix & Target Policy

Date: 2026-09-16
Status: `IMPLEMENTED / VALIDATION_PENDING`
Gate: `P20_2_COVERAGE_MATRIX_POLICY_VALIDATED`

## Objective

Represent source coverage deterministically across the canonical dimensions:

```text
GEOGRAPHY_SCOPE × LANGUAGE × SOURCE_TYPE
```

and define a policy contract that can explicitly describe required, optional, not-required, and not-yet-configured coverage cells without hard-coding a claim of exhaustive global coverage.

P20.2 is policy/contract/evidence work only. It does not onboard sources, change live ingest, deploy runtime code, restart services, create migration `033`, authorize paid resources, or activate shared runtime.

## Authoritative inputs

- `docs/evidence/P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json`
- `docs/evidence/P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json`
- `docs/contracts/p20_1_source_record.schema.json`

## Machine-readable outputs

- `docs/contracts/p20_2_coverage_matrix_policy.schema.json`
- `docs/evidence/P20_2_OBSERVED_COVERAGE_MATRIX_2026-09-16.json`
- `tests/fixtures/p20/p20_2_policy_synthetic.json`

## Matrix semantics

The observed matrix is generated from governed source metadata only.

For each governed source, P20.2 creates one observed cell for every Cartesian combination of:

- each exact P12/P20.1 `geography_scope` label;
- each exact governed language label;
- the single deterministic P20.1 `source_type`.

The current ten-source baseline produces **17 observed cells**.

A source may therefore contribute to more than one geography cell. This is intended and does not imply multiple independent origins.

Each observed cell records:

- governed source count;
- `ACTIVE` availability count;
- `DEGRADED` availability count;
- independent-origin count as `null` until P20.3;
- `coverage_status=POLICY_UNSET` until an explicit target policy is applied.

## Zero-coverage semantics

Absence from the observed matrix means only that no governed source currently generated that exact observed cell.

It does **not** mean:

- the cell is not required;
- the geography/language/source type is unimportant;
- global coverage is complete;
- an event is absent.

A zero-coverage gap becomes policy-visible when a target policy explicitly declares the cell. This lets P20.2 represent expected-but-empty cells instead of silently omitting them.

## Target policy contract

Each target cell is keyed deterministically by:

```text
geography_scope + language + source_type [+ topic_role]
```

`requirement_state` is one of:

```text
REQUIRED
OPTIONAL
NOT_REQUIRED
UNSET
```

`UNSET` is a first-class state. It means the project has not yet made a requirement decision for that cell; it must never be interpreted as `NOT_REQUIRED`.

Threshold fields are explicit and may be `null` where the governing policy has not set them:

- `minimum_source_count`;
- `minimum_independent_origin_count`;
- `minimum_healthy_source_count`;
- `maximum_stale_share`;
- `maximum_dominant_origin_share`.

Policy thresholds are configuration, not global constants. The repository therefore includes only a fully synthetic policy fixture at P20.2; it does not invent canonical geopolitical priority thresholds for real regions without an explicit governing decision.

## Boundary with P20.3/P20.4

P20.2 can express future independent-origin and health thresholds, but it does not fabricate their observed values.

- `minimum_independent_origin_count` may be configured by policy, while observed `independent_origin_count` remains `null` until P20.3 establishes the independence model.
- health/staleness thresholds are policy fields, while source-level health semantics remain governed by P20.4 and earlier source-health evidence.

Thus P20.2 defines **where coverage is expected and how targets are represented**, not the final independence or health evaluation algorithm.

## Epistemic boundaries

```text
SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT
LANGUAGE_COUNT != INDEPENDENT_EVIDENCE_COUNT
COVERAGE_STATUS != FACTUAL_VERIFICATION_STATUS
COVERAGE_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE
COLLECTION_HEALTH != CONTENT_CREDIBILITY
GLOBAL_SCOPE != EXHAUSTIVE_GLOBAL_COVERAGE
```

P13.5/P13.6 remains the factual-verification authority.

## Acceptance criteria

P20.2 is eligible for validation when tests demonstrate that:

- the observed matrix is deterministically reproducible from P20.0 + P20.1;
- the 10 governed sources produce exactly 17 current observed cells;
- source counts are not used as independent-origin counts;
- all observed independent-origin counts remain unknown pending P20.3;
- `UNSET` is distinct from `NOT_REQUIRED`;
- target policy can declare a cell even when it has zero observed sources;
- the P20.2 source-type enum is exactly aligned with P20.1;
- no live-source/runtime/paid/shared-resource boundary changes occur.

On validation, the next gate is `P20_3_SOURCE_INDEPENDENCE_MONOCULTURE_VALIDATED`.

## Validation execution note

GitHub Actions run `35092121412` became stale during the full pytest step without reporting a failure. A documentation-only head refresh was used to trigger a fresh validation run; no P20.2 contract, evidence, policy, runtime, or source semantics changed.
