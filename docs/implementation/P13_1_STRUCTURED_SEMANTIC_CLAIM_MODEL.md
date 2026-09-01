# Phase 13 P13.1 — Structured Semantic Claim Model

Date: 2026-09-01
Status: `VALIDATED`
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`
Parent phase: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE`
Parent gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`

## Purpose

P13.1 is the first schema-bearing Phase 13 package. It introduces additive, immutable/versioned semantic claim structure while preserving existing `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence` and raw-item state.

It does not perform live analytical cutover and does not change factual verification behavior.

## Schema

Migration `023_structured_semantic_claim_model.sql` adds:
- `semantic_claim_versions`;
- `semantic_claim_links`.

`semantic_claim_versions` stores:
- explicit caller-controlled semantic claim identity and version;
- normalized proposition;
- claimant/actor;
- subject;
- object/theme;
- event/action type;
- polarity/negation state;
- modality/epistemic framing;
- structured time scope JSON;
- structured location scope JSON;
- structured quantity/value/unit JSON;
- original language;
- extraction method/version;
- extraction confidence;
- supersession metadata;
- creation timestamp.

Versions are append-only. The model does not silently mutate historical semantic extraction.

`semantic_claim_links` provides non-evidentiary compatibility links from a semantic claim version to:
- legacy `claims`;
- `live_analysis_claims`;
- `raw_items`.

A link means only that the semantic object is associated with an existing/raw object. It is not a `SUPPORTS`, `CONTRADICTS`, independence or provenance-origin judgment.

## Identity Boundary

P13.1 deliberately does not infer canonical semantic equivalence from a headline, normalized headline, publisher, hash or embedding. `semantic_claim_id` is explicit/caller-controlled. Two records with identical proposition text may remain separate claims until a later auditable semantic-resolution process establishes otherwise.

This avoids converting an extraction/storage fingerprint into an unsupported truth or equivalence assertion.

## Confidence Boundary

`extraction_confidence` measures confidence in extraction/structuring only. It is not factual verification confidence and cannot promote truth state.

P13.1 contains no `verification_state`, `factual_confidence`, `coverage_confidence`, `independence_state`, `underlying_origin`, evidence stance or contradiction state fields.

## Reserved For Later P13 Packages

P13.1 does **not** implement:
- underlying-origin/provenance relation model — P13.2;
- evidence relation and independence assessment — P13.3;
- typed contradiction lifecycle — P13.4;
- verification policy engine or multidimensional factual confidence — P13.5;
- live compatibility cutover — P13.6.

## Validation Evidence

Exact implementation/validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.

- x64 CI run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`.
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`.
- ARM64 bootstrap shell validation: PASS.
- unattended one-tick smoke: PASS.
- systemd unit contract validation: PASS.

The single warning remains the existing FastAPI/Starlette TestClient deprecation warning.

Validated deterministic guards cover:
- migration idempotence through canonical database initialization;
- Unicode/original-language preservation;
- explicit identity independent of identical wording;
- immutable version/supersession behavior;
- structured JSON dimensions;
- extraction-confidence validation and truth-confidence separation;
- compatibility links to legacy/live/raw targets;
- link target fail-closed validation;
- schema guard proving P13.2-P13.5 truth fields are absent.

## Runtime / Security Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

P13.1 does not activate public ingress, backend HTTPS, GPT Action, shared runtime, paid providers or autonomous truth promotion.

## Next Package

`P13.2_PROVENANCE_ORIGIN_RELATION_MODEL` becomes `CURRENT / NOT_STARTED` after this validated gate is saved.

P13.2 must add explicit provenance/origin relations without yet implementing evidence independence, contradiction resolution, verification promotion or live cutover.