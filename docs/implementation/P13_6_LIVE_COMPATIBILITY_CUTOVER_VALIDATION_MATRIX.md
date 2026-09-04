# P13.6 — Live Compatibility Cutover / Phase 13 Validation Matrix

Date: 2026-09-04
Status: `VALIDATED`
Package: `P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX`
Implementation / validation anchor: `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`
Evidence-save HEAD: `2a482eb85b118fa5ea46396fa92707733dad5159`
Strategic closure validation anchor: `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`
Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` — `VALIDATED`

## P13.6 Validation Evidence

Implementation validation:
- x64 run `33857212159`, job `100973174656`: `489 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857212157`, job `100973174256`: native `aarch64`, `489 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Evidence-save validation:
- x64 run `33857629735`, job `100974493101`: `493 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857629714`, job `100974493074`: native `aarch64`, `493 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Strategic closure validation:
- x64 run `33861302915`, job `100986128743`: `497 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33861302926`, job `100986128780`: native `aarch64`, `497 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

## Phase 13 Validation Chain

| Package | Gate / state | Validation anchor / closure evidence | Permanent boundary |
|---|---|---|---|
| P13.0 | `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED` | `4422fae5e2a4546585a43237d2124f466c457543`; x64 `33554568574/100012110127`; ARM64 `33554568570/100012110488`; `399 passed, 1 warning / SUCCESS` | semantic claim != headline; count shortcut forbidden |
| P13.1 | `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED` | `69c3282077ad8dd90ef239c0594be56f9363bfe5`; `408 passed, 1 warning / SUCCESS` | explicit identity; links are non-evidentiary |
| P13.2 | `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED` | `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`; `420 passed, 1 warning / SUCCESS` | publisher/publication != underlying origin |
| P13.3 | `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED` | implementation `639d6b2e64d618edfbe742636cb2ac0f663c68ee`; closure `9023dc22d36525b4dc9babbf21d97d184a1c110e`; `438 passed, 1 warning / SUCCESS` | different host/source/language != independence |
| P13.4 | `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED` | implementation `d4dbb8a8098cef960194935bd94d4640fd719050`; closure `f771ce0154e24b2218b309d8b3e6b880b408a146`; `463 passed, 2 warnings / SUCCESS` | reconciliation != factual winner |
| P13.5 | `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED` | implementation `0f0d746c538dc5ce8f010fb80f8afbe00685414a`; formal closure `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3`; x64 `33856550956/100971101911`; ARM64 `33856550913/100971101835`; `480 passed, 2 warnings / SUCCESS` | explicit current independent SUPPORTS + multidimensional policy; no canonical scalar |
| P13.6 | `VALIDATED` | implementation `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`; evidence-save `2a482eb85b118fa5ea46396fa92707733dad5159`; closure `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`; `497 passed, 2 warnings / SUCCESS` | read-only bridge; no legacy truth promotion; exact history only if instrumented |

## Validated P13.6 Compatibility Contract

P13.6 adds `src/kgeopolitical_monitor/semantic_live_compatibility.py` as a read-only projection over already validated persistence. There is no database migration. Migration 028: `NONE`. The canonical migration set remains through `027_semantic_verification_policy_confidence.sql`.

The projection uses:
- explicit P13.1 `LIVE_ANALYSIS_CLAIM` links;
- current P13.5 semantic verification decisions;
- persisted E6 reproducibility bundles when they actually exist.

Fail-closed projection states include `UNLINKED`, `STALE_LINK`, `LINKED_NO_DECISION`, `LINKED_WITH_DECISION`, `AMBIGUOUS_CURRENT_LINKS`.

Validated rules:
- historical `PARTLY_VERIFIED` or `VERIFIED` never becomes semantic verification by fallback;
- legacy scalar confidence never becomes P13.5 factual confidence;
- `origin_host`, distinct-host counts and `independent_origin_count` never establish semantic independence;
- stale/superseded-only semantic links fail closed;
- multiple current semantic identities fail closed rather than selecting a winner;
- one current semantic link without a P13.5 decision remains `LINKED_NO_DECISION`;
- only an unambiguous current P13.5 decision supplies semantic verification state;
- absent E6 instrumentation remains `NOT_INSTRUMENTED`; exact query/run metadata is never reconstructed;
- projection/restart is deterministic and does not rewrite legacy or semantic rows.

## Epistemic Matrix Boundary

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation do not create independent corroboration;
- an official statement establishes that the actor/institution made the statement, not automatically underlying-event truth;
- source reputation, source portfolio state, source health and freshness are not truth operators;
- extraction confidence is not factual verification confidence;
- source/domain/media/language/adapter/item/host count is not independent-origin count;
- graph inference and forecast probability cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- unavailable persisted state is not replaced by ad hoc web research;
- reconstructed/uninstrumented history is not labeled exact.

A failed source does not prove an event did not occur. A successful probe does not prove exhaustive coverage.

## Runtime / Security Matrix Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

- public KGM API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- backend HTTPS: `NOT_DEPLOYED`;
- private GPT Action: `NOT_CONNECTED`;
- paid providers: `NONE_APPROVED`;
- shared/mixed canonical runtime storage: `BLOCKED`;
- public SSH TCP/22 from `0.0.0.0/0`: retained owner-approved candidate exception;
- broad outbound egress: retained owner-approved candidate exception.

## Strategic Closure Decision

P13.0-P13.6 are validated and the strategic gate `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` is granted using the green synchronized closure candidate `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be` as validation anchor.

Phase 14 remains `APPROVED_SEQUENTIAL / NOT_STARTED` and requires `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
