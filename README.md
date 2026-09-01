# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.2
Status: ACTIVE / ROADMAP_V4_PHASE_12 / P12_1_VALIDATED

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
- `docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md` — P12.0 result;
- `docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT.md` — P12.1 implementation;
- `docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT_RESULT.md` — P12.1 result;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED.md` — current checkpoint.

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
- current/next engineering activity: `P12.2_LIVE_ADAPTER_FRAMEWORK_V2 / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P12.1 Validation Evidence

- implementation/validation commit: `905a727d85701bf43d18de2d5216b83ab9a2b8bd`;
- CI run: `33520371480`;
- job: `99897786494`;
- result: `334 passed, 1 warning / SUCCESS`;
- migration: `022_source_portfolio_contract.sql`;
- durable table: `source_portfolio_versions`.

P12.1 is governance infrastructure. It activates no new source and approves no paid provider.

## Source Portfolio Contract

The versioned source portfolio records:

- canonical source/publisher identity;
- source class and role;
- region/language scope;
- access/cost/authentication mode;
- expected freshness and collection cadence;
- adapter identity/version;
- required outbound HTTPS hostnames;
- fallback sources;
- availability/degradation state;
- data classification;
- origin/provenance characteristics and independence constraints;
- licensing/terms notes;
- owner/reviewer/review state;
- explicit paid-provider approval state.

Portfolio versions are immutable. Later versions supersede earlier versions rather than mutating them.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status and source-portfolio metadata are not truth operators;
- portfolio approval does not establish evidence independence;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- presentation cannot strengthen upstream evidence;
- coverage metrics do not modify factual confidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- missing local-language evidence remains explicit;
- missing/uninstrumented tool history is never reconstructed and labeled exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state;
- runtime-health instrumentation cannot imply unavailable coverage/source-health/verification/production facts.

## Runtime / Security State

- owner-only OCI Ubuntu 24.04 ARM64 runtime: real-host validated and candidate-ready;
- application writable path: `/opt/k-geopolitical-monitor/data`;
- rpcbind TCP/UDP port 111: removed; persistent closure validated after reboot;
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

P12.1 added no new live source. P12.2 is the next gate and will connect reusable adapter behavior to the validated source-portfolio governance model.

No paid source/data/translation/graph/forecast/reporting/coverage/notification provider is approved.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`; Start.me remains non-canonical.

## ROADMAP v4

- Phase 12 — ACTIVE; P12.0 and P12.1 validated; P12.2 NEXT/NOT_STARTED.
- Phase 13 — approved sequential / not started.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, Business migration, public sharing, public backend exposure or shared runtime transition is implied by P12.1 validation.
