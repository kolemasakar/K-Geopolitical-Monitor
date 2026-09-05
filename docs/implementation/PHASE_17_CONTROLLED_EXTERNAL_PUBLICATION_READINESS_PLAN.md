# Phase 17 — Controlled External Publication Readiness

Date: 2026-09-05
Plan status: `IN_PROGRESS / CLOSURE_CANDIDATE`
Plan lifecycle: `DEFINED -> VALIDATED_PLAN -> IN_PROGRESS -> COMPLETE / VALIDATED_READY / NOT_ACTIVATED`
Project: K-Geopolitical Monitor
ROADMAP basis: `v4.20`
Strategic phase state: `CONDITIONAL / NOT_ACTIVATED`
Activation gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`
Planning gate: `P17_CONTROLLED_PUBLICATION_READINESS_PLAN_VALIDATED`
Base repository control point: `544eda6267fef8c146c155178809154b6c15c2ae`

## Objective

Validate a controlled, public-safe publication-readiness layer over canonical KGM intelligence without activating publication, public ingress, a public GPT Action, shared runtime, owner execution or paid providers.

Successful Phase 17 engineering may reach `VALIDATED_READY / NOT_ACTIVATED`. Actual publication remains a separate owner decision under `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`.

## Plan Validation

Plan validation anchor: `fef4055a84f582bf8ca5c5cbfbb61644cc297f10`.
- x64 CI run `33931843691`, job `101211866468`: `647 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33931843681`, job `101211866698`: native `aarch64`, `647 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap, unattended one-tick and systemd contract: PASS.

## Historical E8 Boundary

Phase 17 does not reinterpret E8 as an active external/public system.
- `E8_EXTERNAL_SHARING = NOT_ACTIVE`;
- `E8_PUBLIC_ACTION = NOT_APPROVED`;
- `E8_PUBLIC_BACKEND = NOT_DEPLOYED`;
- `E8_PUBLIC_GPT = NOT_PUBLISHED`;
- the owner E3 Action API and E5 admin dashboard are not public contracts and must not be exposed directly;
- Any actual launch gate must revalidate then-current platform eligibility and publication requirements.

## Authoritative Runtime / Security Boundary

- runtime storage remains `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- private GPT Action remains `NOT_CONNECTED`;
- backend HTTPS remains `NOT_DEPLOYED`;
- public sharing remains `NOT_ACTIVE`;
- paid providers remain `NONE_APPROVED`;
- Phase 18 remains separate and is not activated or preapproved.

## Permanent Phase 17 Boundaries

- publication is a derived presentation layer, not canonical truth state;
- publisher/publication identity is not automatically the underlying origin;
- publication lifecycle state, release receipt, views, clicks, downloads or engagement counts are not truth operators;
- publication eligibility cannot promote factual verification;
- public projection references canonical intelligence identifiers and creates no shadow truth store;
- provenance, verification, uncertainty, contradictions and coverage limitations are preserved rather than silently strengthened;
- public-safe redaction and data minimization occur before any export or publication-target boundary;
- secrets, authentication material, owner/admin tokens, private database paths, raw operator feedback and non-public diagnostics are forbidden in public payloads;
- missing, stale, ambiguous or non-public-safe canonical references fail closed;
- exact reproducibility/history claims are emitted only from persisted instrumentation; reconstructed/uninstrumented history is never labeled exact;
- target failure cannot mutate canonical intelligence meaning;
- no real target/provider, public API ingress, public GPT Action, external credential or network listener is activated by Phase 17 engineering;
- paid providers remain forbidden unless separately approved.

## Architecture Separation

`CANONICAL INTELLIGENCE STATE -> PUBLICATION ELIGIBILITY -> PUBLIC-SAFE PROJECTION -> RELEASE MANIFEST -> PUBLICATION PACKAGE -> LOCAL/TEST PUBLICATION TARGET -> RELEASE RECEIPT`

A release receipt proves only publication-target handling. It is publication evidence, not event evidence.

## Planned Phase 17 Sequence

### P17.0 — Controlled Publication Architecture and Safety Contract
State: `VALIDATED`
Gate: `P17_0_CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT_VALIDATED`
Validation anchor: `e7281428cc226c4f68223f3b89503a3aa47a92fa`
- x64 run `33932082220`, job `101212579671`: `658 passed, 2 warnings / SUCCESS`;
- ARM64 run `33932082188`, job `101212579519`: `658 passed, 2 warnings / SUCCESS`, native `aarch64`, host checks PASS.
P17.0 introduces no migration: `NONE_FOR_P17_0`.

### P17.1 — Deterministic Publication Eligibility Policy
State: `VALIDATED`
Gate: `P17_1_PUBLICATION_ELIGIBILITY_POLICY_VALIDATED`
Validation anchor: `3b26863f622b5db3cc07cda156f4ea7b2be9d889`
- x64 run `33932722553`, job `101214469518`: `673 passed, 2 warnings / SUCCESS`;
- ARM64 run `33932722586`, job `101214469696`: `673 passed, 2 warnings / SUCCESS`, native `aarch64`, host checks PASS.
Eligibility requires the canonical P13.5/P13.6 path and cannot use legacy scalar/count shortcuts to promote truth.

### P17.2 — Public-Safe Projection and Redaction
State: `VALIDATED`
Gate: `P17_2_PUBLIC_SAFE_PROJECTION_REDACTION_VALIDATED`
Validation anchor: `8f2e920fd727597286ec691d49c74dd600df35bd`
- x64 run `33935188072`, job `101221628767`: `685 passed, 2 warnings / SUCCESS`;
- ARM64 run `33935188051`, job `101221628733`: `685 passed, 2 warnings / SUCCESS`, native `aarch64`, host checks PASS.
Strict allowlist and fail-closed projection preserve provenance/verification/coverage/reproducibility limitations while omitting owner/admin/raw/private/credential state.

### P17.3 — Release Manifest, Provenance and Reproducibility
State: `VALIDATED`
Gate: `P17_3_RELEASE_MANIFEST_PROVENANCE_VALIDATED`
Validation anchor: `85453a38bacfcb64c69be4d1b671152f6a54849c`
- x64 run `33936315228`, job `101224837960`: `694 passed, 2 warnings / SUCCESS`;
- ARM64 run `33936315269`, job `101224838054`: `694 passed, 2 warnings / SUCCESS`, native `aarch64`, host checks PASS.
Release/package identities bind the exact public payload digest and canonical references. Exact reproducibility references are accepted only from persisted instrumentation; missing instrumentation remains an explicit limitation.
Migration: `NONE`. Migration `033` is not pre-authorized by this plan.

### P17.4 — Provider-Neutral Local/Test Publication Target
State: `VALIDATED`
Gate: `P17_4_PROVIDER_NEUTRAL_PUBLICATION_TARGET_VALIDATED`
Validation anchor: `36548f79cf254621646fa2e2bf863b70944754d2`
- x64 run `33936443430`, job `101225195013`: `701 passed, 2 warnings / SUCCESS`;
- ARM64 run `33936443416`, job `101225194956`: `701 passed, 2 warnings / SUCCESS`, native `aarch64`, host checks PASS.
Implementation is a provider-neutral interface with a deterministic local/in-memory/test sink only.
- canonical automated tests perform no real network publication;
- target failure is isolated from canonical analytical persistence;
- duplicate release effects are deterministically suppressed;
- target receipts are publication evidence only;
- any real target/provider requires a separate explicit owner activation decision.

### P17.5 — Owner Publication Readiness Projection and Approval Gate
State: `VALIDATED`
Gate: `P17_5_OWNER_PUBLICATION_READINESS_PROJECTION_VALIDATED`
Validation anchor: `69010a348cd35fd0b2361c9b32c5baa9428c5816`
- x64 run `33936731551`, job `101226007216`: `707 passed, 2 warnings / SUCCESS`;
- ARM64 run `33936731537`, job `101226007176`: `707 passed, 2 warnings / SUCCESS`, native `aarch64`, host bootstrap/unattended/systemd PASS.
The owner projection is project-local/read-only. Even a complete local-test pipeline yields only `ENGINEERING_READY_NOT_ACTIVATED`; approval and publication effects are `NONE`.

### P17.6 — Phase 17 Validation Matrix / Strategic Readiness Closure
State: `CLOSURE_CANDIDATE`
Readiness gate: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED`
Activation gate remains: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

Closure must confirm publication/truth separation, publisher/publication ≠ underlying-origin proof, receipts/engagement ≠ truth operators, no eligibility truth promotion, redaction before export, owner/admin isolation, preserved provenance/uncertainty/limitations, no reconstructed exact history, deterministic local/test target only, target-failure isolation, no unexpected migration/shadow truth store, `PROJECT_LOCAL_ONLY`, mixed/shared runtime `BLOCKED`, `PRODUCTION_LIVE = NOT_OPERATIONAL`, owner activation separately gated, backend HTTPS/public ingress not deployed, public GPT Action not connected/approved, public sharing inactive, paid providers `NONE_APPROVED`, Phase 18 not activated, exact-head x64 + native ARM64 regression, and ARM64 bootstrap/unattended/systemd PASS.

Successful P17.6 may advance Phase 17 to `VALIDATED_READY / NOT_ACTIVATED`. It must not set publication/sharing to active. Actual publication requires a later explicit owner decision plus then-current platform/security/privacy/exposure/rollback validation.

## Validation Strategy Per Gate

No P17 subphase is promoted from implemented to validated solely because code exists. Validation evidence must reference the exact repository commit tested.
The Phase 17 strategic readiness closure requires both exact-head x64 and native ARM64 validation.

## Non-Goals

No actual external publication/public sharing, GPT Store publication, public GPT Action, public backend/API/dashboard ingress, backend HTTPS production deployment, owner/admin credential reuse, production/live activation, owner unattended activation, Phase 18/shared canonical runtime, cross-project canonical mutation, paid providers, self-modifying policy or replacement of P13.5/P13.6 verification is authorized.

## Current Decision

Plan decision: `IN_PROGRESS / CLOSURE_CANDIDATE`.
P17.0 through P17.5 are validated on exact implementation anchors. P17.6 now requires exact-head x64 and native ARM64 closure-candidate validation. Strategic Phase 17 remains `CONDITIONAL / NOT_ACTIVATED`; no publication activation is implied.
