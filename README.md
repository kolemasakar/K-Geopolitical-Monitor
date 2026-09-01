# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.1
Status: ACTIVE / ROADMAP_V4_PHASE_12 / P12_0_VALIDATED

## Purpose

K-Geopolitical Monitor is designed for discovery, provenance-aware verification, geopolitical analysis, forecasting, reporting, operational monitoring and explicit coverage assessment of significant developments.

## Canonical Documentation

- `PROJECT_CONCEPT_FOUNDATION.md` — approved product intent;
- `ROADMAP.md` — ROADMAP v4.0 and current Phase 12 development line;
- `ARCHITECTURE.md` — current architecture/truth/storage/runtime boundaries;
- `SECURITY_AND_DATA_POLICY.md` — current security/data policy;
- `EXTERNAL_INTEGRATIONS.md` — current integration/source rules;
- `SOURCE_POLICY.md` — source/provenance governance;
- `PROJECT_HISTORY.md` — chronological project record;
- `docs/implementation/PHASE_12_INTELLIGENCE_QUALITY_SOURCE_NETWORK_PLAN.md` — Phase 12 implementation plan;
- `docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md` — validated P12.0 result;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_0_CANONICAL_CONVERGENCE_VALIDATED.md` — P12.0 checkpoint;
- `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md` — owner-approved ROADMAP v4 direction;
- `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md` — final E9A candidate evidence.

## Current State

- Product concept: `APPROVED`;
- ROADMAP: `APPROVED / v4.0`;
- Phase 0-11 engineering line: validated baseline;
- owner-only private GPT pilot: `18/18 PASS`;
- E1-E7: validated baselines;
- E8 Controlled External Sharing / Public GPT: `USER_DEFERRED_UNTIL_SEPARATE_REQUEST`;
- E9A Owner-Only Production Runtime Hardening: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- E9 Shared Production Runtime: `DEFERRED / NOT_APPROVED`;
- intended current runtime users: `1 / OWNER_ONLY`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime storage: blocked pending new explicit architecture approval;
- P12.0: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- current/next engineering activity: `P12.1_SOURCE_PORTFOLIO_CONTRACT_AND_GOVERNANCE / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P12.0 Validation Evidence

- validation commit: `374beb4664cd92a4f41063cbbe30f6830ee3a831`;
- CI run: `33517021594`;
- job: `99886494759`;
- result: `318 passed, 1 warning / SUCCESS`.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status is not an automatic truth/falsehood operator;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- presentation cannot strengthen upstream evidence;
- coverage metrics do not modify factual confidence;
- `GLOBAL` is intended scope, not proof of exhaustive world coverage;
- missing local-language evidence remains explicit;
- missing/uninstrumented exact tool/search history is never reconstructed and labeled exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state;
- runtime-health instrumentation cannot imply unavailable coverage/source-health/uptime/verification/production facts.

## Runtime / Security State

- owner-only OCI Ubuntu 24.04 ARM64 runtime: real-host validated and candidate-ready;
- systemd hardening: validated;
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

Validated controlled-live starting integrations:
- Consilium press-release RSS;
- GDELT DOC 2.0 discovery/index metadata.

P12.0 activated no new source. P12.1 is the next gate and is not started. Phase 12 source expansion remains subject to explicit source/integration records, fail-closed acquisition, origin-independence rules, public/free-first preference and deterministic fixture testing.

No paid source/data/translation/graph/forecast/reporting/coverage/notification provider is activated by Phase 12.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`; Start.me remains non-canonical.

## ROADMAP v4

- Phase 12 — Intelligence Quality and Source Network Foundation — ACTIVE; P12.0 validated; P12.1 NEXT/NOT_STARTED.
- Phase 13 — Semantic Verification and Provenance Intelligence — approved sequential / not started.
- Phase 14 — Owner Operational Intelligence Activation — approved sequential / not started.
- Phase 15 — Forecast Calibration and Performance Intelligence — approved sequential / not started.
- Phase 16 — Delivery, Operator Experience and Quality Feedback — approved sequential / not started.
- Phase 17 external publication readiness — conditional/not activated.
- Phase 18 shared/team runtime — conditional/new architecture approval required.

No production launch, Business migration, public sharing, public backend exposure or shared runtime transition is implied by ROADMAP v4 approval or P12.0 validation.
