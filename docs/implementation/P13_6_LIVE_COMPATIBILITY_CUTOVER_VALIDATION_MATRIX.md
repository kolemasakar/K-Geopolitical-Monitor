# P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix

Date: 2026-09-04
Status: `IMPLEMENTATION_VALIDATED / STRATEGIC_CLOSURE_PENDING`
Project: K-Geopolitical Monitor
Package: `P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX`
Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` — `PENDING_CANONICAL_CLOSURE`
Implementation / validation anchor: `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`
P13.5 final closure baseline: `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3`

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P13.6 Implementation Validation

- x64 run `33857212159`, job `100973174656`: `489 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857212157`, job `100973174256`: native `aarch64`, `489 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

The two warnings are dependency deprecation warnings in the FastAPI/Starlette/anyio test stack and are not a P13.6 functional failure.

## Architecture Decision — No Migration 028

P13.6 adds **no database migration**. Canonical migrations remain through `027_semantic_verification_policy_confidence.sql`.

The read-only compatibility projection reuses already validated stores:
- P13.1 `semantic_claim_links` for explicit `LIVE_ANALYSIS_CLAIM` association;
- P13.5 `semantic_verification_decision_versions` for canonical semantic verification state;
- E6 `research_audit_runs` and related tables for actual persisted reproducibility metadata.

A parallel bridge table would duplicate canonical state and increase semantic-drift risk.

## Implemented Read-Only Bridge

Module: `src/kgeopolitical_monitor/semantic_live_compatibility.py`.
Model version: `P13.6-1.0`.

Compatibility states:
- `UNLINKED`;
- `STALE_LINK`;
- `LINKED_NO_DECISION`;
- `LINKED_WITH_DECISION`;
- `AMBIGUOUS_CURRENT_LINKS`.

Fail-closed semantics:
- a historical legacy live status is never used as fallback semantic verification;
- legacy scalar confidence is never promoted into P13.5 multidimensional factual confidence;
- `origin_host` and `independent_origin_count` never establish semantic independence;
- an explicit link to a superseded semantic version becomes `STALE_LINK` if its current replacement is not linked;
- multiple current semantic identities become `AMBIGUOUS_CURRENT_LINKS`; the bridge does not choose a winner;
- semantic verification state appears only from an unambiguous current P13.5 decision.

## Reproducibility Binding

P13.6 reads `ReproducibilityStore.bundle_for_collection(collection_id)`.

- `NOT_INSTRUMENTED`: no E6 record exists; run/query/cutoff fields remain null;
- `INSTRUMENTED_COMPLETED`: persisted terminal E6 audit exists;
- `INSTRUMENTED_FAILED`: persisted failed E6 audit exists.

Exact query text, research cutoff, instrumentation version and research-run ID are exposed only from persisted E6 state. Missing instrumentation is never reconstructed.

## Non-Destructive / Restart Contract

- legacy `live_analysis_*` rows are not updated or deleted;
- P13.1-P13.5 semantic rows are not updated or deleted;
- no compatibility shadow table is created;
- repeated projection and a new service instance are deterministic for unchanged database state;
- `LiveEndToEndProcessor` remains readable historical compatibility behavior;
- normalized-title grouping, URL-host counts and scalar legacy confidence remain historical fields, not canonical semantic truth.

## Phase 13 Validation Matrix

| Package | Gate / anchor | Validation evidence | Result / permanent boundary |
| --- | --- | --- | --- |
| P13.0 | `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED` / `4422fae5e2a4546585a43237d2124f466c457543` | x64 `33554568574 / 100012110127`; ARM64 `33554568570 / 100012110488`; `399 passed, 1 warning / SUCCESS` | semantic identity, provenance, evidence, independence, contradiction and policy are distinct |
| P13.1 | `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED` / `69c3282077ad8dd90ef239c0594be56f9363bfe5` | x64 `33555804493 / 100016206225`; ARM64 `33555804396 / 100016205406`; `408 passed, 1 warning / SUCCESS` | headline/text identity is not automatic semantic identity |
| P13.2 | `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED` / `6cd37a334b122ae5de2b4cb6272f9cc222f1f174` | x64 `33558425194 / 100024835794`; ARM64 `33558425252 / 100024836399`; `420 passed, 1 warning / SUCCESS` | publisher/publication is not automatically underlying origin |
| P13.3 | `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED` / closure `9023dc22d36525b4dc9babbf21d97d184a1c110e` | x64 `33594299961 / 100134512548`; ARM64 `33594299979 / 100134512479`; `438 passed, 1 warning / SUCCESS` | source/domain/language difference is not independence |
| P13.4 | `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED` / closure `f771ce0154e24b2218b309d8b3e6b880b408a146` | x64 `33848458616 / 100945599309`; ARM64 `33848458681 / 100945599390`; `463 passed, 2 warnings / SUCCESS` | contradiction reconciliation is not automatic truth selection |
| P13.5 | `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED` / closure `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3` | x64 `33856550956 / 100971101911`; ARM64 `33856550913 / 100971101835`; `480 passed, 2 warnings / SUCCESS` | count/official/reputation/coverage shortcuts cannot promote semantic truth |
| P13.6 | implementation `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4` | x64 `33857212159 / 100973174656`; ARM64 `33857212157 / 100973174256`; `489 passed, 2 warnings / SUCCESS` | legacy live compatibility cannot override current P13.5 semantic decisions |

All ARM64 rows above refer to native `aarch64` validation; P13.3+ closure evidence also preserves host/bootstrap/unattended/systemd validation where applicable.

## Permanent Truth / Coverage Boundaries

- publisher/publication is not automatically underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- an official statement establishes that the actor made the statement, not automatically that the underlying event occurred;
- source reputation, source portfolio, health and freshness are not truth operators;
- source/domain/host/language/adapter/item count is not independent-origin count;
- historical `PARTLY_VERIFIED` or `VERIFIED` does not create a P13.5 decision;
- semantic extraction confidence is not factual verification confidence;
- coverage confidence/limitation cannot promote factual verification;
- contradiction reconciliation is not automatic truth selection;
- graph inference and forecast probability cannot promote factual verification;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- unavailable persisted state is not replaced by ad hoc web research;
- uninstrumented or reconstructed tool history is never labeled exact.

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

## Strategic Closure Rule

P13.6 implementation is validated, but `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` is not granted by this file alone.

The strategic gate requires:
- saved P13.6 result/checkpoint;
- canonical ROADMAP/README/DATA_MODELS/Phase-13-plan/history synchronization;
- exact-head x64 and native ARM64 closure regressions after that synchronization.

Phase 14 remains `APPROVED_SEQUENTIAL / NOT_STARTED` and requires the separate owner decision `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED` before operational activation.
