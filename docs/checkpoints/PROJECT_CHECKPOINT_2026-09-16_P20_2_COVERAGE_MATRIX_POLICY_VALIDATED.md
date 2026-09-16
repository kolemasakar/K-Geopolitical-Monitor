# Project Checkpoint — 2026-09-16 — P20.2 Coverage Matrix & Target Policy

Status: `VALIDATED`

Gate:
`P20_2_COVERAGE_MATRIX_POLICY_VALIDATED`

Implementation PR: `#96 — Validate P20.2 coverage matrix and target policy contract`
Implementation merge anchor: `e4cc26990fdcee9b7b6be84cc29b2a2d0a0d6328`
Branch head validated: `335d3fdbf1faf6704a206495e588c09454ad93ca`
GitHub CI run: `35092121412` / run number `1485`
Validation result: `1204 passed in 1096.62s / SUCCESS`

## Validated P20.2 contract

P20.2 establishes deterministic coverage-matrix and target-policy semantics without changing live collection.

Validated properties:

- matrix identity is based on `geography_scope × language × source_type`;
- the current governed P20.0/P20.1 baseline materializes deterministically into 17 observed coverage cells from 10 governed sources;
- policy state distinguishes `REQUIRED`, `OPTIONAL`, `NOT_REQUIRED`, and `UNSET`;
- `UNSET` is not equivalent to `NOT_REQUIRED`;
- zero-observation cells can be represented explicitly by policy and are not silently omitted;
- policy thresholds are configuration, not hard-coded global constants;
- observed source counts do not imply independent-origin counts;
- independent-origin observations remain unknown until P20.3 supplies explicit provenance/independence semantics;
- coverage evidence remains separate from factual-verification confidence.

## Safety/runtime boundary

P20.2 introduced no:

- live-source expansion;
- live ingest change;
- runtime deployment or service restart;
- migration `033`;
- paid-provider authorization;
- shared-runtime activation;
- production/live cutover.

Runtime remains project-local and production/live remains not operational.

## Transition

Canonical phase position after this checkpoint:
`PHASE_20_P20_2_VALIDATED_P20_3_READY`

Next gate:
`P20_3_SOURCE_INDEPENDENCE_MONOCULTURE_VALIDATED`

P20.3 owns independence, redundancy, copy-chain and monoculture semantics. It must not derive independence from source/domain/language counts alone.
