# P13.4 Typed Contradiction Model and Resolution Lifecycle

Date: 2026-09-02
Status: `VALIDATED`
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`
Project: K-Geopolitical Monitor
Parent gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`
Parent closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`
Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`

## Validation Evidence

- x64 run `33594740585`, job `100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594740549`, job `100135812546`: native `aarch64`, `447 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

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

`CAUSAL_INTERPRETATION` is explicitly modeled analytical disagreement; its existence does not convert a causal hypothesis into established fact.

## Lifecycle

Implemented states:
- `DETECTED`;
- `UNRESOLVED`;
- `EVOLVING`;
- `RESOLVED`.

A non-resolved version must use reconciliation code `NONE`. A `RESOLVED` version requires both a non-`NONE` reconciliation code and an explanatory note.

Resolution describes reconciliation of the contradiction object, not an automatic declaration that either claim is true. Historical disagreement remains preserved in prior append-only versions. Reconciliation codes are descriptive and intentionally contain no `LEFT_TRUE` / `RIGHT_TRUE` shortcuts.

## P13.3 Evidence Linkage

`semantic_contradiction_evidence_links` links a contradiction version to evidence relation versions with side `LEFT`/`RIGHT` and roles `CLAIM_EVIDENCE`, `CONTRADICTION_TRIGGER`, `QUALIFIER`, `RESOLUTION_CONTEXT`.

The service fails closed unless the contradiction and evidence versions exist, the evidence belongs to the selected claim side, and that evidence relation version is current for its P13.3 evidence identity at link time.

A P13.3 `CONTRADICTS` relation does not automatically create or resolve a P13.4 contradiction object.

## Compatibility Boundary

Legacy `src/kgeopolitical_monitor/contradictions.py` remains unchanged as historical compatibility state. The canonical P13.4 implementation is additive in `src/kgeopolitical_monitor/semantic_contradictions.py`.

P13.4 introduces no automatic resolution from source reputation, source class/official status, publisher/domain/language count, P13.3 independence state, source health/freshness, graph inference, forecast output or coverage metadata.

## Scope Exclusions

P13.4 intentionally does not implement:
- canonical verification promotion — P13.5;
- multidimensional factual confidence — P13.5;
- live semantic verification cutover — P13.6;
- production/live activation.

No `verification_state`, `verification_status`, `factual_confidence`, `coverage_confidence`, `verification_policy`, `truth_state`, source-reputation score or legacy independent-origin count is stored in the P13.4 schema.

## Validated Regression Coverage

Validation proved:
- every typed contradiction dimension persists;
- `DETECTED -> EVOLVING -> RESOLVED` history is append-only;
- explicit reconciliation rules fail closed;
- contradiction identity drift is rejected;
- evidence links enforce current P13.3 relation versions and correct claim side;
- P13.3 `CONTRADICTS` does not auto-create/resolve P13.4 objects;
- both new persistence surfaces reject UPDATE/DELETE;
- P13.5 truth/confidence fields are absent;
- legacy `Contradiction` compatibility remains readable.

## Runtime Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Public ingress, backend HTTPS, private GPT Action, shared runtime, paid providers and production/live operation remain unchanged.

## Next Package

P13.5 — Verification Policy Engine and Multidimensional Confidence — may become current only through the separate P13.4 closure/state-sync. P13.4 validation itself does not implement P13.5 behavior.