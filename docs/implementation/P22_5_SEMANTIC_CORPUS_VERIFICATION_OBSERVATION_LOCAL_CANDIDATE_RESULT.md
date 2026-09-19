# P22.5 — Semantic Corpus & Verification Observation — Local Closure Candidate

Date: 2026-09-19

Status: `LOCAL_CANDIDATE / AWAITING_CANONICAL_BRIDGE_INTEGRATION`

This result is derived from an isolated copy of the real P22.5 owner-local observation DB after applying the locally validated bounded semantic-ingestion bridge.

## Exact cohort

- analysis run: `analysis-40db4a933f17064d461789e8`;
- OFAC claims: `15`;
- White House claims: `13`;
- legacy live claims: `28`;
- canonical P13.1 semantic claims after bridge: `28`.

## P13.5 verification distribution

```text
DETECTED = 28
PARTLY_VERIFIED = 0
VERIFIED = 0
DISPUTED = 0
UNVERIFIABLE = 0
```

The bridge therefore creates an observable canonical semantic corpus without factual promotion.

## Evidence / provenance observation

- evidence relations: `28 ATTRIBUTION_ONLY`;
- observed PUBLICATION roles: `28`;
- UNDERLYING_ORIGIN roles: `28 UNRESOLVED`;
- independence assessments: `0`;
- canonical contradictions: `0`.

All 28 confidence profiles are fail-closed:

```text
evidence_sufficiency = LOW
provenance_independence = UNKNOWN
authority_proximity = LOW
contradiction_resolution = UNKNOWN
temporal_freshness = UNKNOWN
extraction_certainty = LOW
translation_certainty = UNKNOWN
claim_specific_certainty = LOW
coverage_limitation = LIMITED
```

## P13.6 compatibility

All 28 legacy live claims project as `LINKED_WITH_DECISION`.

Legacy verification/status promotion count is `0`.

## Candidate interpretation

P22.5's observation requirement becomes measurable after bridge integration:

- real canonical corpus: observed;
- canonical decision distribution: observed;
- unresolved-claim distribution: observed;
- provenance limitation: explicit;
- independence evidence: explicitly absent;
- exact cohort membership: preserved.

Candidate decision:

`VALIDATABLE_WITH_ALL_CLAIMS_DETECTED_AND_UNDERLYING_ORIGIN_UNRESOLVED`.

This is **not** canonical P22.5 closure yet. The bridge is pending canonical integration because GitHub Actions quota is exhausted. P22.6 remains closed.
