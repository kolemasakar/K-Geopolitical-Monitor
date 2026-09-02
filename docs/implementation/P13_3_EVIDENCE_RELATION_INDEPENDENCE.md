# Phase 13 P13.3 — Evidence Relation and Independence Assessment

Date: 2026-09-02
Status: `VALIDATED`
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`
Parent gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`
Validation anchor: `639d6b2e64d618edfbe742636cb2ac0f663c68ee`

## Purpose

P13.3 introduces a typed, append-only evidence-to-semantic-claim relation layer and a separate versioned evidentiary-independence assessment layer built on P13.1 semantic claims and P13.2 provenance.

Evidence relation and independence are not final truth decisions. P13.3 does not resolve contradiction lifecycles, promote verification states, calculate factual confidence, or cut over live analysis.

## Additive Schema

Migration `025_semantic_evidence_relation_independence.sql` adds:
- `semantic_evidence_relation_versions`;
- `semantic_independence_assessment_versions`.

Both are append-only and use superseding versions rather than destructive mutation.

## Typed Evidence Relations

Supported claim-scoped relation types:
- `SUPPORTS`;
- `CONTRADICTS`;
- `QUALIFIES`;
- `CONTEXT_ONLY`;
- `ATTRIBUTION_ONLY`;
- `DUPLICATE_OR_SAME_ORIGIN`.

Each evidence relation points to a P13.1 semantic claim version and a P13.2 provenance entity version. Optional raw-item linkage is fail-closed against the provenance entity's raw-item identity.

A typed evidence relation does not change verification state and does not itself resolve a contradiction.

## Independence Assessment

Supported states:
- `INDEPENDENT`;
- `NOT_INDEPENDENT`;
- `UNKNOWN`;
- `MIXED`.

Pairwise independence assessments are versioned separately from evidence relations and require an auditable rationale code and assessment method/version.

The fail-closed inference helper may establish only:
- `NOT_INDEPENDENT` when evidence is duplicate/same-origin or connected through a current provenance derivation path;
- `UNKNOWN` for unresolved or insufficient provenance;
- `MIXED` for mixed origin.

It deliberately never infers `INDEPENDENT` from absence of a known derivation path. Explicit `INDEPENDENT` assessments require `EXPLICIT_DISTINCT_UNDERLYING_ORIGINS` or a recorded manual-review rationale.

Different publisher, source ID, hostname, domain or language is never sufficient independence proof.

## Current-Provenance Rule

Automated derivation-path inference uses only the latest version of each P13.2 provenance-relation identity. Historical superseded derivation edges remain auditable history but cannot permanently determine the current independence state after a provenance correction.

## Deterministic Validation

Validated tests cover:
- all six evidence-relation types;
- syndication and translation chains remaining `NOT_INDEPENDENT`;
- two publications citing the same official statement remaining `NOT_INDEPENDENT`;
- different publishers/languages without origin proof remaining `UNKNOWN`;
- explicit `UNKNOWN` and `MIXED` provenance fail-closed behavior;
- explicit-rationale requirement for `INDEPENDENT`;
- append-only evidence and independence histories;
- claim/reference identity mismatch failure;
- current-only provenance graph after a superseded derivation edge;
- schema proof that P13.4/P13.5 contradiction, verification and factual-confidence fields are absent.

Validation evidence:
- x64 CI run `33575533714`, job `100078564552`: `434 passed, 1 warning / SUCCESS`;
- native ARM64 run `33575533657`, job `100078564729`: native `aarch64`, `434 passed, 1 warning / SUCCESS`;
- ARM64 bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- systemd unit contract validation: PASS.

The single warning remains the existing FastAPI/Starlette TestClient deprecation warning.

## Compatibility Boundary

- P13.1 semantic claim versions are referenced, not rewritten.
- P13.2 provenance entities/relations are referenced, not duplicated.
- legacy `claims/evidence/live_analysis_*` remain readable and unchanged.
- legacy host/source count remains compatibility state only and is not accepted as semantic independence proof.
- no live analytical cutover occurs.

## Scope Boundary

Not implemented in P13.3:
- typed contradiction lifecycle/resolution — P13.4;
- verification policy engine and multidimensional factual confidence — P13.5;
- live compatibility cutover and Phase 13 validation matrix — P13.6.

## Truth / Runtime Boundaries

- publisher/publication is not automatically underlying origin;
- syndication/repost/translation/citation does not create independent corroboration;
- official-source status proves the statement/document exists, not automatically the substantive event claim;
- evidence relation and independence metadata cannot by themselves promote verification state;
- source/domain/language count is not independent-origin count;
- coverage confidence remains separate from factual verification confidence.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

No public ingress, backend HTTPS, private GPT Action, shared runtime, paid-provider activation or production/live operation is implied by P13.3 engineering work.

## Closure / Continuation

Gate saved: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.

P13.4 becomes `CURRENT / NOT_STARTED` and is responsible for typed contradiction objects and resolution lifecycle. Verification promotion remains P13.5; live cutover remains P13.6.