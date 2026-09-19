# P22.5 — Semantic Corpus & Verification Observation — Gap Result

Status: `BLOCKED_ON_CANONICAL_SEMANTIC_INGESTION_GAP`

Exact-main owner-local observation at `eabd9ed98cfa3e266fdee5933f69bed2d459b83b` produced real post-B1 collection evidence but no canonical P13 semantic corpus.

## Observed

- host: `kgm-e4-owner-pilot` / `aarch64`;
- source cohort: OFAC + White House;
- collection: `COMPLETED`;
- raw items: `28`;
- source success/failure: `2 / 0`;
- legacy live-analysis claims: `28 DETECTED`;
- legacy findings: `28`;
- database integrity: `ok`.

## Canonical semantic path

```text
semantic_claim_versions = 0
semantic_claim_links = 0
semantic_evidence_relation_versions = 0
semantic_factual_confidence_versions = 0
semantic_verification_decision_versions = 0
```

Therefore:

```text
CANONICAL_SEMANTIC_CORPUS_OBSERVED = FALSE
VERIFICATION_YIELD_IMPACT = NOT_OBSERVED
CONTRADICTION_WORKLOAD_IMPACT = NOT_OBSERVED
FORECAST_INPUT_IMPACT = NOT_OBSERVED
```

## Interpretation

The source-expansion path is now producing owner-local evidence, but the runtime has no canonical ingestion/claim-formation bridge from live source evidence into the validated P13 semantic model.

The legacy M8 `live_analysis_claims` path groups normalized titles and exposes legacy statuses such as `DETECTED`. These rows are compatibility/operational state only. They must not be relabeled as P13 semantic claims or factual verification.

A safe bridge must preserve:

- semantic claim identity is not headline identity;
- provenance roles remain explicit;
- evidence relation remains explicit;
- underlying-origin independence defaults to UNKNOWN unless established;
- publisher/domain/host/source count cannot create independence;
- P13.5/P13.6 remain the only canonical verification authority.

## Gate

P22.5 is not validated yet.

Next action: `P22_5_CANONICAL_SEMANTIC_INGESTION_BRIDGE_IMPLEMENTATION`.

No P22.6 work is opened by this observation.
