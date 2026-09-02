# P13.4 Typed Contradiction Model and Resolution Lifecycle

Date: 2026-09-02
Status: `IMPLEMENTED_PENDING_VALIDATION`
Expected gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`
Project: K-Geopolitical Monitor
Parent gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`
Parent closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`

## Objective

Implement an additive, typed, versioned contradiction layer over P13.1 semantic claim versions with optional auditable linkage to current P13.3 evidence relations.

P13.4 models analytical disagreement and its lifecycle. It does **not** determine which claim is factually true, promote verification state, calculate factual/coverage confidence, or cut over the legacy/live analytical path.

## Additive Schema

Migration: `026_semantic_contradiction_model.sql`.

New tables:
- `semantic_contradiction_versions`;
- `semantic_contradiction_evidence_links`.

Existing legacy `claims`, `evidence`, `live_analysis_*`, `contradictions.py`, P13.1 semantic claims, P13.2 provenance and P13.3 evidence/independence state are not destructively rewritten.

Both new tables are immutable after insert through SQL `UPDATE`/`DELETE` rejection triggers. Contradiction lifecycle changes are recorded by appending a new contradiction version with explicit supersession.

## Contradiction Identity

A contradiction identity binds:
- one left immutable `semantic_claim_version_id`;
- one right immutable `semantic_claim_version_id`;
- one typed contradiction dimension.

The two claim version IDs must exist and must be different.

Once the contradiction identity exists, later lifecycle versions cannot silently replace either claim version or the contradiction dimension. A contradiction involving a newly versioned semantic claim requires a new contradiction identity rather than retroactively changing the old analytical object.

## Typed Dimensions

Implemented dimensions:
- `OCCURRENCE_EXISTENCE`;
- `ATTRIBUTION_RESPONSIBILITY`;
- `ACTOR_IDENTITY`;
- `QUANTITY_VALUE`;
- `TIME`;
- `LOCATION`;
- `STATUS_OUTCOME`;
- `SCOPE_EXTENT`;
- `CAUSAL_INTERPRETATION`;
- `OTHER`.

`CAUSAL_INTERPRETATION` is an explicitly modeled analytical contradiction dimension; its existence does not convert a causal hypothesis into established fact.

## Lifecycle

Implemented states:
- `DETECTED`;
- `UNRESOLVED`;
- `EVOLVING`;
- `RESOLVED`.

A non-resolved version must use reconciliation code `NONE`.

A `RESOLVED` contradiction version requires:
- a non-`NONE` reconciliation code;
- an explanatory note.

Resolution is a statement about the contradiction object's analytical reconciliation, not an automatic declaration that the left or right claim is true. Historical disagreement remains preserved in prior append-only versions.

Reconciliation vocabulary is descriptive rather than truth-selecting. It includes new evidence, occurrence/scope/time/location/attribution/quantity/actor/status/causal reconciliation, superseded information, manual review and `OTHER`. There are intentionally no `LEFT_TRUE` / `RIGHT_TRUE` codes.

## P13.3 Evidence Linkage

`semantic_contradiction_evidence_links` may link a contradiction version to evidence relation versions with:
- side: `LEFT` or `RIGHT`;
- role: `CLAIM_EVIDENCE`, `CONTRADICTION_TRIGGER`, `QUALIFIER`, `RESOLUTION_CONTEXT`.

The service fails closed unless:
- the contradiction version exists;
- the evidence relation version exists;
- the evidence relation belongs to the semantic claim version identified by the selected side;
- the evidence relation is the **current** version of its P13.3 evidence identity at link time.

Superseded evidence remains historical P13.3 audit state but cannot be silently attached as current contradiction evidence.

A P13.3 `CONTRADICTS` evidence relation does not automatically create or resolve a P13.4 contradiction object.

## Compatibility Boundary

Legacy `src/kgeopolitical_monitor/contradictions.py` remains unchanged as historical compatibility state. The canonical P13.4 implementation is additive in `src/kgeopolitical_monitor/semantic_contradictions.py`.

P13.4 introduces no automatic reasoning from:
- source reputation;
- source class or official status;
- publisher/domain/language count;
- P13.3 independence state;
- source health/freshness;
- graph/forecast/coverage metadata.

Those signals cannot by themselves resolve substantive truth.

## Scope Exclusions

P13.4 intentionally does not implement:
- canonical verification promotion — P13.5;
- multidimensional factual confidence — P13.5;
- live semantic verification cutover — P13.6;
- production/live activation.

No `verification_state`, `verification_status`, `factual_confidence`, `coverage_confidence`, `verification_policy`, `truth_state`, source-reputation score or legacy independent-origin count is stored in the P13.4 contradiction schema.

## Deterministic Validation Coverage

Candidate regression coverage includes:
- every typed contradiction dimension;
- versioned `DETECTED -> EVOLVING -> RESOLVED` lifecycle with preserved history;
- explicit reconciliation requirements;
- contradiction identity drift rejection;
- current P13.3 evidence relation and side-scope enforcement;
- proof that P13.3 `CONTRADICTS` does not auto-create/resolve P13.4 objects;
- SQL append-only enforcement;
- schema boundary checks excluding P13.5 truth/confidence fields;
- legacy `Contradiction` container compatibility.

## Runtime Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

P13.4 implementation does not activate public ingress, backend HTTPS, private GPT Action, shared runtime, paid providers or production/live operation.

## Validation State

Implementation is not yet the gate. Required next evidence:
- full x64 regression on the implementation candidate;
- full native ARM64 regression;
- ARM64 bootstrap/unattended/systemd PASS;
- exact candidate SHA/run/job IDs saved before canonical closure.

Until those checks are green, P13.4 remains `IMPLEMENTED_PENDING_VALIDATION` and P13.5 must not start.