# Project Checkpoint — 2026-09-16 — P20.1 Source Taxonomy & Metadata Contract Validated

Status: `VALIDATED`
Gate: `P20_1_SOURCE_TAXONOMY_METADATA_CONTRACT_VALIDATED`
Implementation PR: `#94`
Implementation merge anchor: `2a9164f2815c4c7b36c48f963b85a9c0c8385024`

## Validation evidence

GitHub CI:

```text
workflow: CI
run: 35091228455
job: 104777750615
result: SUCCESS
pytest: 1196 passed in 116.94s
```

Validated artifacts:

- `docs/contracts/p20_1_source_record.schema.json`
- `docs/evidence/P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json`
- `docs/implementation/P20_1_CANONICAL_SOURCE_TAXONOMY_METADATA_CONTRACT.md`
- `tests/test_p20_1_source_taxonomy_contract.py`

## Validated decisions

- all 10 P20.0 governed source IDs have exactly one deterministic P20 `source_type`;
- all current adapter IDs have an explicit deterministic `collection_method` mapping;
- P12 region/language scopes remain multi-valued and are not collapsed;
- geography normalization preserves exact legacy scope and forbids unsupported geographic inference;
- `reliability_class`, `origin_group_id`, `syndication_or_copy_relation`, and `active_for_coverage` remain nullable/unknown unless explicit evidence or later policy governs them;
- P12 availability is not silently promoted into source credibility, factual verification, origin independence, or coverage eligibility;
- Haberturk `www.haberturk.com` current governance and historical P12.5 `rss.haberturk.com` measurement are reconciled without rewriting history;
- P13.5/P13.6 remains the factual-verification authority.

Permanent non-equivalence boundaries remain:

```text
SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT
LANGUAGE_COUNT != INDEPENDENT_EVIDENCE_COUNT
COVERAGE_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE
COLLECTION_HEALTH != CONTENT_CREDIBILITY
P20_COVERAGE_EVIDENCE != CLAIM_VERIFICATION
```

## Runtime / safety boundary

P20.1 introduced no:

- live source expansion;
- live ingest change;
- runtime deployment;
- service restart;
- control-plane change;
- migration `033`;
- paid-provider authorization;
- shared-runtime activation.

`PRODUCTION_LIVE` remains `NOT_OPERATIONAL` and runtime storage remains `PROJECT_LOCAL_ONLY`.

## Transition

```text
P20_0_EXISTING_COVERAGE_BASELINE_MAPPED = VALIDATED
P20_1_SOURCE_TAXONOMY_METADATA_CONTRACT_VALIDATED = VALIDATED
P20_2_COVERAGE_MATRIX_POLICY_VALIDATED = NEXT_GATE
```

Next implementation scope: **P20.2 Coverage Matrix & Target Policy**.
