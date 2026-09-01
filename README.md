# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.3
Status: ACTIVE / ROADMAP_V4_PHASE_12 / P12_2_VALIDATED

## Purpose

K-Geopolitical Monitor supports discovery, provenance-aware verification, geopolitical analysis, forecasting, reporting, operational monitoring and explicit coverage assessment of significant developments.

## Canonical Documentation

- `ROADMAP.md` — ROADMAP v4 and current Phase 12 state;
- `ARCHITECTURE.md` — architecture/truth/storage/runtime boundaries;
- `SECURITY_AND_DATA_POLICY.md` — security/data policy;
- `EXTERNAL_INTEGRATIONS.md` — integration/source rules;
- `SOURCE_POLICY.md` — source/provenance governance;
- `DATA_MODELS.md` — canonical data-model summary;
- `PROJECT_HISTORY.md` — chronological project record;
- `docs/implementation/PHASE_12_INTELLIGENCE_QUALITY_SOURCE_NETWORK_PLAN.md` — Phase 12 plan;
- `docs/implementation/P12_2_LIVE_ADAPTER_FRAMEWORK_V2.md` — P12.2 implementation;
- `docs/implementation/P12_2_LIVE_ADAPTER_FRAMEWORK_V2_RESULT.md` — P12.2 result;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED.md` — current checkpoint.

## Current State

- Product concept: `APPROVED`;
- strategic ROADMAP: `APPROVED / v4`;
- Phase 0-11 engineering line: validated baseline;
- owner-only private GPT pilot: `18/18 PASS`;
- E1-E7: validated baselines;
- E8 Controlled External Sharing / Public GPT: `USER_DEFERRED_UNTIL_SEPARATE_REQUEST`;
- E9A Owner-Only Production Runtime Hardening: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- E9 Shared Production Runtime: `DEFERRED / NOT_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- P12.0: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- P12.1: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- P12.2: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- current/next engineering activity: `P12.3_PRIORITY_AUTHORITATIVE_SOURCE_PACK / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P12.2 Validation Evidence

- implementation commit: `f2635cc5724b24ed7f3b880c50a67a4ca0f849fa`;
- validation commit: `cb6866e82d5dc4a26042e0b9d08e9098aae10ecb`;
- CI run: `33523574819`;
- job: `99908604206`;
- result: `346 passed, 1 warning / SUCCESS`.

## Live Adapter Framework v2

P12.2 adds an additive governed framework over the validated M7 collector:

- bounded read-only HTTPS GET transport;
- fail-closed non-HTTPS/credential rejection for public-anonymous acquisition;
- deterministic RSS and Atom parsing;
- bounded JSON-list parsing;
- reusable public feed/JSON adapter contracts;
- deterministic source/adapter/version/item identity;
- exact P12.1 portfolio review/access/adapter/outbound-host enforcement;
- compatibility with canonical collection attempts, ingestion/provenance and E6 reproducibility;
- deterministic local fixtures independent of live network availability;
- source-failure isolation.

P12.2 does not activate a source merely because a v2 adapter class exists. Existing Consilium/GDELT v2 classes are reusable adapter definitions, not automatic runtime switches.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status and source-portfolio metadata are not truth operators;
- adapter/source/domain count is not independent-origin count;
- portfolio approval does not establish evidence independence;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- presentation cannot strengthen upstream evidence;
- coverage metrics do not modify factual confidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- missing/uninstrumented tool history is never reconstructed and labeled exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state.

## Runtime / Security State

- owner-only OCI Ubuntu 24.04 ARM64 runtime: real-host validated and candidate-ready;
- public KGM HTTP/HTTPS/database/API/dashboard ingress: not approved/not deployed;
- backend HTTPS: not deployed;
- private GPT backend Action: not connected;
- dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public GPT sharing: user-deferred;
- production/live: not operational.

Remaining explicit owner-approved candidate networking exceptions:

- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

## Source / Integration State

Validated controlled-live starting integrations remain:

- Consilium press-release RSS;
- GDELT DOC 2.0 discovery/index metadata.

P12.2 added reusable governed adapter infrastructure but seeded and activated no new external source. P12.3 is the next gate for a priority authoritative source pack.

No paid source/data/translation/graph/forecast/reporting/coverage/notification provider is approved.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`; Start.me remains non-canonical.

## ROADMAP v4

- Phase 12 — ACTIVE; P12.0, P12.1 and P12.2 validated; P12.3 NEXT/NOT_STARTED.
- Phase 13 — approved sequential / not started.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, Business migration, public sharing, public backend exposure or shared runtime transition is implied by P12.2 validation.
