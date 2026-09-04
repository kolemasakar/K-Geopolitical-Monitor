# P13.5 Verification Policy Engine and Multidimensional Confidence

Date: 2026-09-04
Status: `VALIDATED`
Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`
Implementation / validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`
Parent canonical closure HEAD: `f771ce0154e24b2218b309d8b3e6b880b408a146`

## Purpose

P13.5 introduces an additive policy-controlled semantic verification layer over the validated P13.1-P13.4 model. It replaces canonical reliance on legacy evidence-count and source-ID-count shortcuts without deleting those historical compatibility APIs.

P13.5 does not perform the P13.6 live compatibility cutover.

## Additive Persistence

Migration `027_semantic_verification_policy_confidence.sql` adds append-only:

- `semantic_verification_policy_versions`;
- `semantic_factual_confidence_versions`;
- `semantic_verification_decision_versions`.

No legacy `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence`, P13.1 semantic claim, P13.2 provenance, P13.3 evidence/independence or P13.4 contradiction row is destructively rewritten.

## Policy Contract

Canonical policy versions preserve permanent fail-closed invariants:

- evidence count alone cannot promote verification;
- different source/host/domain/publisher/language count cannot establish semantic independence;
- official-source status alone cannot promote substantive event truth;
- source reputation alone cannot promote verification;
- coverage confidence/coverage metadata cannot promote factual verification;
- `VERIFIED` requires an explicit current `INDEPENDENT` pair whose two evidence relations are current `SUPPORTS` relations for the claim;
- current `CONTRADICTS` evidence blocks `VERIFIED`;
- any current unresolved/evolving/detected P13.4 contradiction involving the claim blocks `VERIFIED`;
- policy confidence minimums are multidimensional and may be strengthened by later policy versions but cannot be weakened below the canonical floor.

## Multidimensional Factual Confidence

`semantic_factual_confidence_versions` stores qualitative dimensions separately:

- evidence sufficiency;
- provenance independence;
- authority/proximity;
- contradiction resolution;
- temporal freshness;
- extraction certainty;
- translation certainty;
- claim-specific certainty.

Each factual dimension is `UNKNOWN`, `LOW`, `MEDIUM` or `HIGH`.

Coverage is recorded separately as `coverage_limitation = UNKNOWN | LIMITED | ADEQUATE`. The P13.5 model stores no `coverage_confidence` field and no single canonical factual-confidence scalar. The Python model deliberately exposes `presentation_scalar = None` and `coverage_confidence = None`.

A high authority/proximity assessment is contextual input, not proof of substantive truth. An official statement still establishes that the actor made the statement, not automatically that the underlying event claim is true.

## Decision Snapshot Contract

A decision is append-only and versioned per immutable semantic claim version. At record time the service automatically snapshots:

- the global-latest version of every current P13.3 evidence-relation identity that belongs to the claim;
- the global-latest version of every current P13.3 independence-assessment identity that belongs to the claim;
- the global-latest version of every current P13.4 contradiction identity involving the claim;
- the current approved verification-policy version;
- the current multidimensional factual-confidence version.

This prevents a caller from omitting a current contradiction, selecting superseded evidence as current, or using a stale independence assessment as proof for a current supporting pair.

## Verification States

P13.5 retains the compatibility vocabulary:

- `DETECTED`;
- `PARTLY_VERIFIED`;
- `VERIFIED`;
- `DISPUTED`;
- `UNVERIFIABLE`.

The vocabulary is retained for compatibility; promotion semantics are policy-controlled.

`PARTLY_VERIFIED` requires current supporting semantic evidence plus minimum multidimensional confidence and is blocked by current disputed semantic state.

`VERIFIED` requires the explicit current independent supporting pair and stronger multidimensional confidence, with no current contradicting evidence and no active P13.4 contradiction.

`DISPUTED` requires current contradicting evidence or an active contradiction.

`UNVERIFIABLE` requires an explicit `LIMITED` coverage limitation plus low/unknown claim-specific certainty. Mere absence of two sources is not an `UNVERIFIABLE` rule.

## Compatibility Boundary

Legacy `src/kgeopolitical_monitor/verification.py` remains readable, including its historical `evidence_count >= 2` behavior. Legacy `src/kgeopolitical_monitor/confidence_engine.py` also remains readable, including its historical scalar/source-ID-count calculation. Neither module is modified or imported by the P13.5 canonical semantic verification service.

Deterministic compatibility tests prove those legacy APIs still work while the P13.5 schema contains no legacy scalar confidence, `source_reliability` or `independent_origin_count` shortcut column.

## Append-Only / Audit Boundary

Policies, factual-confidence profiles and decisions reject SQL UPDATE/DELETE. Decision transition codes (`INITIAL`, `HOLD`, `PROMOTE`, `DEMOTE`, `DISPUTE`, `MARK_UNVERIFIABLE`) are audit metadata and must match the requested transition.

## Validation Evidence

Exact implementation / validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`.

- x64 run `33849149736`, job `100947736040`: `475 passed, 2 warnings / SUCCESS`.
- native ARM64 run `33849149742`, job `100947736318`: native `aarch64`, `475 passed, 2 warnings / SUCCESS`.
- ARM64 bootstrap shell validation: PASS.
- unattended one-tick smoke: PASS.
- systemd unit contract validation: PASS.

The warnings are dependency deprecations in FastAPI/Starlette TestClient and the Starlette/anyio `BlockingPortal` alias; neither is a P13.5 semantic/runtime failure.

## Scope Exclusions

P13.5 intentionally does not implement:

- P13.6 live-analysis compatibility cutover;
- automatic migration of legacy live verification states;
- public ingress/backend HTTPS/private GPT Action deployment;
- shared runtime;
- paid-provider activation;
- production/live operation.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## Next Package

`P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX` becomes `CURRENT / NOT_STARTED` after this gate is saved.

P13.6 must validate compatibility/cutover and close the Phase 13 strategic gate without treating old count-based live fields as canonical semantic truth.