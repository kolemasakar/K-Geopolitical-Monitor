# P13.6 — Live Compatibility Cutover Result

Date: 2026-09-04
Status: `VALIDATED`
Package: `P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX`
Implementation / validation anchor: `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`
Evidence-save HEAD: `2a482eb85b118fa5ea46396fa92707733dad5159`
Strategic closure validation anchor: `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`
Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` — `VALIDATED`

## Validation Evidence

Implementation validation:
- x64 run `33857212159`, job `100973174656`: `489 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857212157`, job `100973174256`: native `aarch64`, `489 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Evidence-save validation:
- x64 run `33857629735`, job `100974493101`: `493 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857629714`, job `100974493074`: native `aarch64`, `493 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Strategic closure validation:
- x64 run `33861302915`, job `100986128743`: `497 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33861302926`, job `100986128780`: native `aarch64`, `497 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

The warnings are dependency deprecation warnings in the FastAPI/Starlette/anyio test stack, not a P13.6 functional failure.

## Validated Scope

P13.6 adds `src/kgeopolitical_monitor/semantic_live_compatibility.py`, a read-only projection over existing validated state. New database migration: `NONE`; migration 028: `NONE`; canonical migration set remains through `027_semantic_verification_policy_confidence.sql`.

The projection reuses:
- explicit P13.1 `LIVE_ANALYSIS_CLAIM` links;
- current P13.5 semantic verification decisions;
- actual persisted E6 reproducibility bundles when they exist.

Validated behavior:
- legacy `PARTLY_VERIFIED`/`VERIFIED` never becomes semantic truth by fallback;
- legacy scalar confidence never becomes P13.5 factual confidence;
- URL-host counts, `origin_host` and `independent_origin_count` never establish semantic independence;
- superseded-only links fail closed as `STALE_LINK`;
- multiple current semantic identities fail closed as `AMBIGUOUS_CURRENT_LINKS`;
- exactly one current semantic link without a decision remains `LINKED_NO_DECISION`;
- semantic state is exposed only from an unambiguous current P13.5 decision;
- missing reproducibility instrumentation remains `NOT_INSTRUMENTED` with no reconstructed exact query/run metadata;
- projection/restart is deterministic and does not rewrite legacy or semantic rows.

## Epistemic Result

P13.6 closes the compatibility gap without importing historical M8 analytical shortcuts into the canonical semantic layer. It does not make a historical live-analysis record evidence of independent origin, factual truth, coverage completeness or production readiness.

Publisher/publication is not automatically the underlying origin. Repost/syndication/translation/citation does not create independent corroboration. Official-source status is not automatically substantive event truth. Source reputation, source health and coverage are not truth operators. Coverage confidence cannot promote factual verification confidence.

## Data / Runtime / Security Result

- migration 028: `NONE`;
- legacy live rows: `PRESERVED / NOT_REWRITTEN`;
- semantic rows: `PRESERVED / NOT_REWRITTEN`;
- production/live operational status: `NOT_OPERATIONAL`;
- runtime storage mode: `PROJECT_LOCAL_ONLY`;
- public API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- private GPT Action: `NOT_CONNECTED`;
- paid providers: `NONE_APPROVED`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## Gate Decision

P13.6 is validated and Phase 13 closes at `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED` using the green synchronized closure candidate `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be` as the strategic validation anchor.

Phase 14 operational activation is not implied and still requires `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
