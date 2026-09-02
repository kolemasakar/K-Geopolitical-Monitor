# P13.3 Evidence Relation and Independence Assessment — Result

Date: 2026-09-02
Status: `VALIDATED`
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`
Validation anchor: `639d6b2e64d618edfbe742636cb2ac0f663c68ee`

## Result

P13.3 is validated as the additive evidence-relation and evidentiary-independence layer over P13.1 semantic claims and P13.2 provenance.

Migration `025_semantic_evidence_relation_independence.sql` adds append-only evidence relation versions and append-only pairwise independence assessment versions. No legacy/live analytical rows are destructively rewritten.

Validated behavior includes:
- typed evidence relations: `SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`;
- explicit independence states: `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, `MIXED`;
- fail-closed inference from P13.2 provenance rather than publisher/source/domain/language counts;
- same-origin, syndication, translation, citation and other current derivation paths remain non-independent;
- unresolved provenance remains `UNKNOWN`; mixed provenance remains `MIXED`;
- absence of a known derivation path never auto-promotes evidence to `INDEPENDENT`;
- explicit `INDEPENDENT` persistence requires an auditable compatible rationale such as reviewed distinct underlying origins;
- provenance corrections use only the latest version of each provenance-relation identity for current inference, while superseded edges remain historical audit data;
- evidence/independence records remain versioned and append-only;
- relation/reference/claim identity mismatches fail closed.

## Validation Evidence

Exact implementation/validation commit: `639d6b2e64d618edfbe742636cb2ac0f663c68ee`.

- x64 CI run `33575533714`, job `100078564552`: `434 passed, 1 warning / SUCCESS`.
- native ARM64 run `33575533657`, job `100078564729`: native `aarch64`, `434 passed, 1 warning / SUCCESS`.
- ARM64 bootstrap shell validation: PASS.
- unattended one-tick smoke: PASS.
- systemd unit contract validation: PASS.

The single warning remains the existing FastAPI/Starlette TestClient deprecation warning.

## Epistemic Boundary

P13.3 records how evidence bears on a claim and whether a pair of evidence records is known to be independent. Neither record type is itself a final verification decision.

Different publisher, source ID, hostname, domain or language is not sufficient evidence of independence. Citation, syndication, reposting and translation do not create independent corroboration by themselves. An official statement establishes that the actor made the statement, not automatically that the substantive event claim is true.

`CONTRADICTS` is an evidence relation only in P13.3; typed contradiction objects and resolution lifecycle remain P13.4.

## Scope Boundary

P13.3 intentionally does not implement:
- typed contradiction lifecycle/resolution — P13.4;
- verification policy engine or multidimensional factual confidence — P13.5;
- live compatibility cutover / Phase 13 validation matrix — P13.6.

Evidence relation, independence metadata, source reputation, source health, freshness, graph probability, forecast probability and coverage confidence cannot by themselves promote factual verification state.

## Runtime Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

P13.3 does not activate public ingress, backend HTTPS, private GPT Action, shared runtime, paid providers or production/live operation.

## Next Package

`P13.4_TYPED_CONTRADICTION_MODEL` becomes `CURRENT / NOT_STARTED` after this gate is saved.

P13.4 must model contradiction dimensions and lifecycle without turning source reputation or independence metadata into automatic truth resolution. Verification promotion remains reserved for P13.5.