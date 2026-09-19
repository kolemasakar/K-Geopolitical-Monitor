# P22.5 — Semantic Corpus & Verification Observation — Validated Result

Date: 2026-09-19

Status: `VALIDATED_WITH_ALL_CLAIMS_DETECTED_AND_UNDERLYING_ORIGIN_UNRESOLVED`

Gate: `P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED`

Canonical code SHA: `a4dfeee3765116e6b2c261413129b7329f754202`.

## Historical gap and remediation

The earlier exact-main observation at `eabd9ed98cfa3e266fdee5933f69bed2d459b83b` produced 28 legacy live-analysis claims but zero canonical P13 semantic rows. That gap remains preserved as historical evidence.

The canonical semantic-ingestion bridge is now integrated and exact-main validated. A new owner-local observation was executed against an isolated copy of the real P22.5 database.

## Exact cohort

- sources: OFAC Recent Actions + White House Briefings & Statements;
- analysis run: `analysis-40db4a933f17064d461789e8`;
- legacy live claims: `28`;
- canonical semantic claims: `28`;
- canonical semantic links: `56`;
- canonical evidence relations: `28 ATTRIBUTION_ONLY`;
- canonical confidence rows: `28`;
- canonical verification decisions: `28`.

## P13.5 verification distribution

```text
DETECTED = 28
PARTLY_VERIFIED = 0
VERIFIED = 0
DISPUTED = 0
UNVERIFIABLE = 0
```

No underlying factual claim is promoted.

All 28 canonical claims represent publication attribution only. Underlying origin remains unresolved and automatic factual independence credit remains zero.

## P13.6 compatibility

All 28 legacy live claims resolve as `LINKED_WITH_DECISION`.

```text
legacy_status_promoted = 0
legacy_confidence_promoted = 0
legacy_origin_count_establishes_independence = 0
```

## Downstream observations opened by P22.5

- canonical semantic corpus: `OBSERVED`;
- verification decision distribution: `OBSERVED`;
- unresolved-origin distribution: `OBSERVED`;
- contradiction workload: measurable, with `0` canonical contradiction rows in this exact cohort;
- forecast-input impact: remains `NOT_OBSERVED`.

A zero contradiction count is an observed workload property of this exact cohort, not evidence that the underlying claims are mutually consistent or true.

## Validation mode

GitHub Actions quota contingency is active until 2026-10-01.

The bridge exact head was validated on `kgm-e4-owner-pilot` / `aarch64`:

- targeted semantic suite: `32 passed`;
- full regression: `1357 passed in 416.09s`.

The post-merge observation against exact main also preserved DB integrity: `ok`.

## Boundary

No persistent owner operation, runtime deployment, service restart, paid/shared dependency, migration 033, production/live cutover or Plugin publication occurred.

P13.5/P13.6 remain the sole canonical factual-verification authority.

Next gate: `P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED`.
