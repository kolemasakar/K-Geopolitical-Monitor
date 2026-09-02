# Project Checkpoint — P13.2 Provenance / Underlying-Origin Relation Model Validated

Date: 2026-09-02
Project: K-Geopolitical Monitor
State: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`

## Validation Anchor

Commit: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`

Validation evidence:
- x64 CI run `33558425194`, job `100024835794`: `420 passed, 1 warning / SUCCESS`;
- native ARM64 run `33558425252`, job `100024836399`: native `aarch64`, `420 passed, 1 warning / SUCCESS`;
- bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- systemd unit contract: PASS.

## Saved Gate

`P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`

Validated implementation:
- migration `024_semantic_provenance_origin_relation_model.sql`;
- `src/kgeopolitical_monitor/semantic_provenance.py`;
- compatibility-preserving additions to `src/kgeopolitical_monitor/provenance.py`;
- deterministic provenance regression coverage;
- append-only provenance entity, claim-role and relation persistence;
- explicit unknown/mixed origin handling;
- source/raw traceability and URL secret-leak guards;
- no P13.3-P13.6 truth-policy cutover.

## Epistemic Boundary

Publisher/publication is distinct from underlying origin. Citation, syndication, reposting and translation do not create independent corroboration. Official-source status proves the statement/document exists, not automatically the substantive event claim. P13.2 provenance metadata cannot by itself promote verification state or factual confidence.

## Runtime Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

No public ingress, backend HTTPS, private GPT Action, shared runtime or paid-provider activation is implied by this checkpoint.

## Continuation Point

Phase 13 remains active.

P13.0: `VALIDATED`.
P13.1: `VALIDATED`.
P13.2: `VALIDATED`.
P13.3: `CURRENT / NOT_STARTED`.
P13.4-P13.6: `PLANNED / NOT_STARTED`.

Next gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.