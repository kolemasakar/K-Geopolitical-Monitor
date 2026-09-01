# P13.1 Structured Semantic Claim Model — Result

Date: 2026-09-01
Status: `VALIDATED`
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`

## Result

P13.1 is validated as the first additive schema-bearing Phase 13 work package.

Migration `023_structured_semantic_claim_model.sql` adds append-only `semantic_claim_versions` and `semantic_claim_links` while preserving legacy `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence` and raw-item state.

Validated behavior includes:
- explicit caller-controlled semantic claim identity rather than normalized-headline identity;
- append-only semantic versions with monotonic version numbers and explicit supersession;
- structured normalized proposition, claimant/actor, subject, object/theme, event/action type, polarity, modality, time scope, location scope, quantity, original language and extraction metadata;
- deterministic preservation of Unicode/original-language content;
- extraction confidence constrained to `[0,1]` and explicitly separated from factual verification confidence;
- non-evidentiary links to legacy claims, live-analysis claims and raw items;
- fail-closed link-target and structured-value validation;
- identical text does not automatically merge semantic identity;
- no live analytical cutover or change to legacy verification behavior.

## Validation Evidence

Exact implementation/validation commit: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.

- x64 CI run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`.
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`.
- ARM64 bootstrap shell validation: PASS.
- unattended one-tick smoke: PASS.
- systemd unit contract validation: PASS.

The single warning remains the existing FastAPI/Starlette TestClient deprecation warning.

## Scope Boundary

P13.1 intentionally does not implement:
- provenance / underlying-origin relations — P13.2;
- evidence stance or evidentiary independence — P13.3;
- typed contradiction lifecycle — P13.4;
- verification policy engine or multidimensional factual confidence — P13.5;
- live analytical cutover — P13.6.

The schema guard verifies that `underlying_origin`, `independence_state`, `evidence_relation`, `contradiction_state`, `verification_state`, `factual_confidence` and `coverage_confidence` are absent from `semantic_claim_versions`.

`semantic_claim_links` are association records only and cannot be interpreted as `SUPPORTS`, `CONTRADICTS`, provenance identity or independence judgments.

## Truth / Runtime Boundaries

- semantic extraction confidence is not factual verification confidence;
- publisher/publication remains distinct from underlying origin;
- another source/domain/language does not create independent corroboration;
- legacy host/count shortcuts remain historical compatibility behavior pending later validated cutover;
- no model/LLM extraction output may directly promote canonical truth.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

P13.1 does not activate public ingress, backend HTTPS, private GPT Action, shared runtime, paid providers or production/live operation.

## Next Package

`P13.2_PROVENANCE_ORIGIN_RELATION_MODEL` becomes `CURRENT / NOT_STARTED` after this gate is saved.

P13.2 must introduce explicit, auditable provenance/origin relations while keeping evidence independence, contradiction resolution and verification promotion reserved for later packages.