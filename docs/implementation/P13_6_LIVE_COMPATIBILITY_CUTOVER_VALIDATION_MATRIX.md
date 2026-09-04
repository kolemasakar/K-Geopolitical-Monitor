# P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix

Date: 2026-09-04
Status: `IMPLEMENTED / VALIDATION_PENDING`
Project: K-Geopolitical Monitor
Current package: `P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX`
Expected strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
Base / final P13.5 closure HEAD: `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3`

## Objective

P13.6 provides a non-destructive compatibility projection between historical `live_analysis_*` state and the canonical P13.1-P13.5 semantic stack. The compatibility layer must make old analytical output readable without importing historical normalized-title, URL-host-count, `independent_origin_count`, evidence-count or scalar-confidence shortcuts into semantic truth.

P13.6 does not activate production/live operation, public ingress, shared runtime, paid providers or Phase 14.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P13.5 Formal Closure Baseline

P13.5 gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.

Implementation validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`.
- x64 `33849149736 / 100947736040`: `475 passed, 2 warnings / SUCCESS`;
- native ARM64 `33849149742 / 100947736318`: `475 passed, 2 warnings / SUCCESS`, native `aarch64`, bootstrap/unattended/systemd PASS.

Final formal closure HEAD: `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3`.
- x64 `33856550956 / 100971101911`: `480 passed, 2 warnings / SUCCESS`;
- native ARM64 `33856550913 / 100971101835`: `480 passed, 2 warnings / SUCCESS`, native `aarch64`, bootstrap/unattended/systemd PASS.

The two warnings are dependency deprecation warnings in the FastAPI/Starlette/anyio test stack, not a P13.5 functional failure.

## Architecture Decision — No Migration 028 for Compatibility Projection

P13.6 adds **no database migration** for the compatibility bridge. Canonical migrations remain through `027_semantic_verification_policy_confidence.sql`.

A new bridge table would duplicate state already represented by three validated canonical layers:
- P13.1 `semantic_claim_links` already provides an explicit `LIVE_ANALYSIS_CLAIM` link;
- P13.5 `semantic_verification_decision_versions` already provides versioned current semantic verification decisions;
- E6 `research_audit_runs` and related reproducibility tables already bind actual instrumented research to source collection IDs.

The P13.6 service therefore projects those existing stores read-only. This reduces parallel truth stores, migration risk and semantic drift.

## Implemented Compatibility Projection

Module: `src/kgeopolitical_monitor/semantic_live_compatibility.py`.
Model version: `P13.6-1.0`.

Compatibility states:
- `UNLINKED` — historical live claim has no explicit P13.1 semantic link;
- `STALE_LINK` — only superseded semantic claim versions are linked;
- `LINKED_NO_DECISION` — exactly one current semantic version is explicitly linked, but it has no current P13.5 decision;
- `LINKED_WITH_DECISION` — exactly one current semantic version is linked and has a current P13.5 decision;
- `AMBIGUOUS_CURRENT_LINKS` — multiple current semantic claim identities are linked and the bridge refuses to choose one.

The projection records historical live values explicitly as legacy compatibility fields. Their semantics remain historical:
- `verification_status` is not canonical semantic verification;
- legacy scalar `confidence` is not P13.5 multidimensional factual confidence;
- `independent_origin_count` and `origin_host` are not semantic independence;
- normalized-title grouping is not semantic claim identity.

`semantic_verification_state` is exposed **only** from a current P13.5 decision. There is no fallback from legacy status.

## Current-Version Fail-Closed Rule

A P13.1 link to a semantic version does not remain current merely because the historical row still exists.

P13.6 compares every linked semantic version with the global latest version of its `semantic_claim_id`:
- an old linked version whose current replacement is not linked becomes `STALE_LINK`;
- multiple distinct current semantic identities become `AMBIGUOUS_CURRENT_LINKS`;
- neither case produces a semantic verification state.

This prevents superseded or ambiguous semantic mappings from becoming hidden truth shortcuts.

## Reproducibility Binding

P13.6 uses `ReproducibilityStore.bundle_for_collection(collection_id)`.

States:
- `NOT_INSTRUMENTED` — no E6 research audit exists for the collection; query/run/cutoff metadata remain null;
- `INSTRUMENTED_COMPLETED` — an actually persisted terminal E6 audit exists;
- `INSTRUMENTED_FAILED` — an actually persisted failed E6 audit exists.

Exact query text, research cutoff, instrumentation version and research-run ID are exposed only from persisted E6 records. Missing instrumentation is never reconstructed from a watch, source URL, citation or current conversation.

## Non-Destructive / Restart Contract

The compatibility service is read-only:
- no legacy live row is updated or deleted;
- no semantic claim/evidence/decision row is updated or deleted;
- no compatibility shadow table is created;
- repeated projection and a new service instance yield deterministic results from the same canonical database state;
- existing `LiveEndToEndProcessor` remains the historical compatibility producer and is not silently rewritten in P13.6.

## Deterministic Validation Coverage

`tests/test_semantic_live_compatibility.py` covers:
- legacy `PARTLY_VERIFIED` plus two URL hosts remains `UNLINKED` with no semantic state;
- an explicit current P13.1 link without P13.5 decision remains `LINKED_NO_DECISION`;
- a P13.5 `DETECTED` decision remains canonical even when legacy status is `PARTLY_VERIFIED` and scalar confidence is `1.0`;
- multiple current semantic links fail closed as `AMBIGUOUS_CURRENT_LINKS`;
- a superseded linked version becomes `STALE_LINK` when its current replacement is not linked;
- an uninstrumented collection does not fabricate research/query metadata;
- an instrumented collection exposes only actual E6 persisted metadata;
- restart/read projection is deterministic and leaves legacy rows/counts unchanged;
- missing compatibility targets fail closed.

## Phase 13 Validation Matrix — Candidate State

| Package | Gate | Candidate state | Permanent boundary |
| --- | --- | --- | --- |
| P13.0 | `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED` | VALIDATED | semantic identity/provenance/evidence/independence/contradiction/policy are distinct |
| P13.1 | `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED` | VALIDATED | headline/text identity is not automatic semantic identity |
| P13.2 | `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED` | VALIDATED | publisher/publication is not automatically underlying origin |
| P13.3 | `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED` | VALIDATED | source/domain/language difference is not independence |
| P13.4 | `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED` | VALIDATED | contradiction reconciliation is not automatic truth selection |
| P13.5 | `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED` | VALIDATED | count/official/reputation/coverage shortcuts cannot promote truth |
| P13.6 | `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` | IMPLEMENTED / VALIDATION_PENDING | legacy live compatibility cannot override semantic policy decisions |

The final P13.6 validation evidence and final Phase 13 decision must be added only after full x64 and native ARM64 regression passes on the implementation candidate and again on the formal closure HEAD.

## Permanent Truth / Coverage Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status establishes the source statement, not automatically the underlying event;
- source reputation, portfolio status, source health and freshness are not truth operators;
- legacy source/domain/host/language/item counts do not establish semantic independence;
- historical `PARTLY_VERIFIED` or `VERIFIED` values do not create P13.5 decisions;
- semantic extraction confidence is not factual verification confidence;
- coverage confidence/limitation cannot promote factual verification;
- graph inference and forecast probability cannot promote factual verification;
- `GLOBAL` remains scope, not proof of exhaustive world coverage;
- unavailable persisted state is not replaced by ad hoc web research;
- missing/uninstrumented tool history is never reconstructed and labeled exact.

## Runtime / Security Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

- public KGM API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- backend HTTPS: `NOT_DEPLOYED`;
- private GPT backend Action: `NOT_CONNECTED`;
- shared/mixed canonical runtime storage: `BLOCKED`;
- paid providers: `NONE_APPROVED`;
- public SSH TCP/22 from `0.0.0.0/0`: retained owner-approved candidate exception;
- broad outbound egress: retained owner-approved candidate exception.

## Candidate Gate Decision

`PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` is **NOT YET GRANTED**.

P13.6 implementation must pass full x64 and native ARM64 validation, then the final result/checkpoint/canonical state synchronization must itself pass exact-head closure regression before Phase 13 can be closed or Phase 14 can become current.
