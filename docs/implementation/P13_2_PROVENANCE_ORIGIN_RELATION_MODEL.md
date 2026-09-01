# Phase 13 P13.2 — Provenance / Underlying-Origin Relation Model

Date: 2026-09-01
Status: `IMPLEMENTED_PENDING_VALIDATION`
Expected gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`
Parent gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`

## Purpose

P13.2 adds an explicit, append-only provenance/origin relation layer tied to P13.1 semantic claim versions and existing source/raw objects.

It records provenance identity and derivation. It does **not** decide evidentiary independence, evidence stance, contradiction resolution, verification state or factual confidence.

## Additive Schema

Migration `024_semantic_provenance_origin_relation_model.sql` adds:
- `semantic_provenance_entity_versions`;
- `semantic_claim_provenance_role_versions`;
- `semantic_provenance_relation_versions`.

All three tables are append-only. Corrections create later versions with explicit supersession rather than mutating historical provenance.

## Provenance Entities

Supported entity kinds:
- `PUBLICATION`;
- `PUBLISHER`;
- `SOURCE_ENDPOINT`;
- `OFFICIAL_STATEMENT`;
- `OFFICIAL_DOCUMENT`;
- `WIRE_REPORT`;
- `DATASET`;
- `SOCIAL_POST`;
- `USER_PROVIDED`;
- `OTHER`;
- `UNKNOWN`;
- `MIXED`.

Entities may retain source ID, raw-item ID, canonical public URL, language and JSON metadata where those identities are actually known.

`UNKNOWN` and `MIXED` entities deliberately cannot claim a concrete source ID, raw-item ID or URL. This prevents unresolved provenance from acquiring invented precision.

Source/raw references fail closed: referenced records must exist, and an explicitly supplied source must agree with the source stored on the referenced raw item.

Canonical URLs are limited to HTTP/HTTPS and reject embedded userinfo credentials or common sensitive query-credential keys.

## Claim Provenance Roles

A semantic claim version may be associated with provenance entities using explicit roles:
- `PUBLICATION`;
- `PUBLISHER`;
- `IMMEDIATE_ACQUIRED_SOURCE`;
- `CITED_SOURCE`;
- `QUOTED_SOURCE`;
- `UNDERLYING_ORIGIN`;
- `PROVENANCE_CONTEXT`.

Attribution state is provenance metadata, not factual confidence:
- `OBSERVED`;
- `ASSERTED`;
- `UNRESOLVED`;
- `MIXED`.

`UNRESOLVED` and `MIXED` are valid only for `UNDERLYING_ORIGIN` and must point to `UNKNOWN` and `MIXED` entity kinds respectively. Unknown origin therefore remains explicitly unresolved instead of being inferred from publisher/domain/language differences.

## Entity-to-Entity Provenance Relations

Versioned relation types:
- `PUBLISHED_BY`;
- `ACQUIRED_FROM`;
- `CITES`;
- `QUOTES`;
- `SYNDICATED_FROM`;
- `REPOSTED_FROM`;
- `TRANSLATED_FROM`;
- `DERIVED_FROM`;
- `DATA_EXTRACTED_FROM`;
- `OTHER`.

Direction is explicit: the subject entity has the stated relationship to the object entity. For example:

`Reuters publication -> CITES -> official government statement`

and separately:

`Reuters publication -> PUBLISHED_BY -> Reuters publisher`.

This preserves the distinction between publisher and underlying source/origin.

Concrete derivation edges cannot use `UNKNOWN` or `MIXED` entities because doing so would fabricate a chain where the origin is unresolved.

## Epistemic Boundary

P13.2 does not introduce or populate:
- `independence_state`;
- evidence stance/relation such as `SUPPORTS` or `CONTRADICTS`;
- contradiction state;
- verification state;
- factual confidence;
- coverage confidence.

Every P13.2 dataclass exposes fail-safe semantics showing that a provenance record or derivation does not establish independence and does not change verification state.

Syndication, repost and translation relations therefore remain same/derived provenance relationships; they never create independent corroboration by themselves.

## Compatibility Boundary

- P13.1 semantic claim versions are referenced, not rewritten.
- Existing `sources`, `raw_items`, `live_source_provenance`, legacy `claims/evidence`, and `live_analysis_*` remain readable and unchanged.
- The older translation table's `underlying_origin_id/origin_kind` fields remain historical compatibility metadata and are not treated as P13.2 semantic-origin proof.
- No live analytical cutover occurs in P13.2.

## Deterministic Validation Targets

Tests cover:
- Reuters-publication -> official-statement citation/origin chain;
- explicit publication/publisher separation;
- append-only entity, claim-role and relation versions;
- source/raw traceability and mismatch failure;
- explicit `UNKNOWN/UNRESOLVED` and `MIXED` origin states;
- syndication/translation chains without independence promotion;
- URL credential leakage guards;
- schema proof that P13.3-P13.5 fields are absent;
- canonical migration idempotence.

## Runtime / Security Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

P13.2 does not activate public ingress, backend HTTPS, private GPT Action, shared runtime, paid providers or production/live operation.

## Validation Rule

Implementation is not validation. The gate may be marked validated only after full x64 and native ARM64 regression evidence is green and saved.

P13.3 must not start before P13.2 is implemented, validated and saved.