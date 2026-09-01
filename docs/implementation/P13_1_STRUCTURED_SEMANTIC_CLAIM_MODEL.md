# Phase 13 P13.1 — Structured Semantic Claim Model

Date: 2026-09-01
Status: `IMPLEMENTED / VALIDATION_PENDING`
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`
Parent phase: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE`
Parent gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`

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

## Validation Requirements

- migration idempotence through canonical database initialization;
- Unicode/original-language preservation;
- explicit identity independent of identical wording;
- immutable version/supersession behavior;
- structured JSON dimensions;
- extraction-confidence validation and truth-confidence separation;
- compatibility links to legacy/live/raw targets;
- link target fail-closed validation;
- schema guard proving P13.2-P13.5 truth fields are absent;
- full x64 regression;
- native ARM64 regression plus bootstrap/unattended/systemd checks.

## Runtime / Security Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

P13.1 does not activate public ingress, backend HTTPS, GPT Action, shared runtime, paid providers or autonomous truth promotion.
