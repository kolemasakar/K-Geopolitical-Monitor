# P13.2 Provenance / Underlying-Origin Relation Model — Result

Date: 2026-09-02
Status: `VALIDATED`
Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`
Validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`

## Result

P13.2 is validated as the additive provenance/origin layer over P13.1 semantic claims.

Migration `024_semantic_provenance_origin_relation_model.sql` adds append-only provenance entity versions, semantic-claim provenance-role versions and provenance-relation versions while preserving legacy source/raw/provenance APIs and all historical analytical state.

Validated behavior includes:
- explicit separation of publication, publisher, immediate acquired source, cited/quoted source and underlying origin;
- typed provenance entities for official statements/documents, wire reports, datasets, social/user-provided origins and unresolved/mixed origin cases;
- explicit derivation relations including citation, syndication, repost, translation and other derivation paths;
- append-only versioning/supersession across provenance entities, claim-role assignments and entity relations;
- fail-closed source/raw-item identity matching and URL credential-leak guards;
- `UNKNOWN/UNRESOLVED` and `MIXED` provenance retained without invented precision;
- compatibility preservation for the existing legacy provenance API;
- no evidentiary independence, evidence stance, contradiction resolution, verification promotion or factual-confidence logic introduced in P13.2.

## Validation Evidence

Exact implementation/validation commit: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.

- x64 CI run `33558425194`, job `100024835794`: `420 passed, 1 warning / SUCCESS`.
- native ARM64 run `33558425252`, job `100024836399`: native `aarch64`, `420 passed, 1 warning / SUCCESS`.
- ARM64 bootstrap shell validation: PASS.
- unattended one-tick smoke: PASS.
- systemd unit contract validation: PASS.

The single warning remains the existing FastAPI/Starlette TestClient deprecation warning.

## Scope Boundary

P13.2 intentionally does not implement:
- evidence stance or evidentiary independence — P13.3;
- typed contradiction lifecycle — P13.4;
- verification policy engine or multidimensional factual confidence — P13.5;
- live analytical cutover — P13.6.

A provenance record establishes traceable origin/derivation metadata only. It does not establish that a claim is true, that two records are independent, or that a verification threshold has been met.

Syndication, reposting, translation and citation remain derivation/provenance relationships and do not create independent corroboration by themselves.

## Truth / Runtime Boundaries

- publisher/publication is not automatically the underlying origin;
- an official statement establishes `actor said X`, not automatically `X happened`;
- different publisher/domain/language does not create independent corroboration;
- provenance certainty is not factual verification confidence;
- source reputation, source health, coverage and freshness remain non-truth operators;
- no live analytical cutover occurred.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

P13.2 does not activate public ingress, backend HTTPS, private GPT Action, shared runtime, paid providers or production/live operation.

## Next Package

`P13.3_EVIDENCE_RELATION_INDEPENDENCE` becomes `CURRENT / NOT_STARTED` after this gate is saved.

P13.3 must add typed evidence-to-claim relations and explicit independence assessment using P13.2 provenance rather than source/domain/language counts. Contradiction resolution and verification promotion remain reserved for later packages.