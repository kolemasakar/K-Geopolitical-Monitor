# Project Checkpoint — P13.1 Structured Semantic Claim Model Validated

Date: 2026-09-01
Project: K-Geopolitical Monitor
State: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`

## Validation Anchor

Commit: `69c3282077ad8dd90ef239c0594be56f9363bfe5`

- x64 run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`.
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`.
- bootstrap shell: PASS.
- unattended one-tick smoke: PASS.
- systemd unit contract: PASS.

## Saved Model

P13.1 adds migration `023_structured_semantic_claim_model.sql` and the additive semantic-claim persistence layer:
- append-only `semantic_claim_versions`;
- append-only `semantic_claim_links`;
- explicit semantic identity and version/supersession;
- structured proposition, actor/subject/object/action, polarity, modality, time/location/quantity, original-language and extraction metadata;
- non-evidentiary links to legacy claims, live-analysis claims and raw items.

Legacy analytical tables remain readable compatibility state. P13.1 does not change live verification behavior or production/runtime activation state.

Extraction confidence remains separate from factual verification confidence. The P13.1 schema contains no provenance-origin, independence, contradiction, verification-state, factual-confidence or coverage-confidence fields reserved for P13.2-P13.5.

## Next Exact Point

Current Phase 13 package after this checkpoint:
`P13.2_PROVENANCE_ORIGIN_RELATION_MODEL / CURRENT_NOT_STARTED`.

P13.2 must add explicit provenance/underlying-origin relations and preserve `UNKNOWN/UNRESOLVED` origin where evidence is insufficient. It must not yet implement evidentiary independence, contradiction resolution or verification promotion.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY