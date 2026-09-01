# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.0
Status: ACTIVE / ROADMAP_V4_PHASE_12

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
- `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md` — owner-approved ROADMAP v4 direction;
- `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md` — post-E9A development analysis;
- `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md` — final E9A candidate evidence;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_ROADMAP_V4_PHASE_12_READY.md` — Phase 12 transition checkpoint;
- `BOOTSTRAP_PACKAGE_2026-09-01_K-GEOPOLITICAL-MONITOR_ROADMAP_V4_PHASE_12_TRANSITION.md` — current transition bootstrap.

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
- production/live: `NOT_OPERATIONAL`;
- active numbered ROADMAP phase: `Phase 12 — Intelligence Quality and Source Network Foundation`;
- current engineering activity: `P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`.

## Canonical Validation Evidence Retained

- Phase 11: 226 passed, run `33000478908`;
- private GPT pilot: 18/18 PASS;
- E1: 241 passed, run `33244484173`;
- E2: 248 passed, run `33244795277`;
- E3: 254 passed, run `33247311921`;
- E4 real host: run `33258520620`, SUCCESS;
- E5: x64 282 passed run `33263584520`; native ARM64 `33263584515`, SUCCESS;
- E6: x64 290 passed run `33264133429`; native ARM64 `33264133407`, SUCCESS;
- E7: x64 294 passed run `33265984585`; native ARM64 `33265984622`, SUCCESS;
- E9A.6 real OCI state-preserving validation: run `33486944907`, SUCCESS;
- rpcbind persistent closure: run `33488954688`, SUCCESS;
- final E9A x64: `318 passed, 1 warning`, run `33503085538`, SUCCESS;
- final E9A native ARM64: native `aarch64`, `318 passed, 1 warning`, run `33503085489`, SUCCESS;
- post-E9A canonical sync: `318 passed, 1 warning`, run `33504369245`, SUCCESS.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status is not an automatic truth/falsehood operator;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- report presentation cannot strengthen upstream evidence;
- `coverage_ratio` and `coverage_confidence` do not modify factual confidence;
- `GLOBAL` is intended scope, not proof of exhaustive world coverage;
- missing local-language evidence remains explicit;
- missing/uninstrumented exact tool/search history is never reconstructed and labeled exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state;
- runtime-health instrumentation cannot imply unavailable coverage, source-health, uptime, verification or production facts.

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

Remaining explicit owner-approved candidate exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

These are not equivalent to final least-privilege production networking.

## Source / Integration State

Validated controlled-live starting integrations:
- Consilium press-release RSS;
- GDELT DOC 2.0 discovery/index metadata.

Phase 12 is approved to broaden this source network under explicit source/integration records, fail-closed acquisition, origin-independence rules, public/free-first preference and deterministic fixture testing.

No paid source/data/translation/graph/forecast/reporting/coverage/notification provider is activated by Phase 12.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`; Start.me remains non-canonical.

## ROADMAP v4

Sequential approved phases:
- Phase 12 — Intelligence Quality and Source Network Foundation — ACTIVE;
- Phase 13 — Semantic Verification and Provenance Intelligence — approved sequential / not started;
- Phase 14 — Owner Operational Intelligence Activation — approved sequential / not started;
- Phase 15 — Forecast Calibration and Performance Intelligence — approved sequential / not started;
- Phase 16 — Delivery, Operator Experience and Quality Feedback — approved sequential / not started.

Conditional only:
- Phase 17 external publication readiness — not activated;
- Phase 18 shared/team runtime — new architecture approval required.

P12.0 must validate before P12.1 begins. No production launch, Business migration, public sharing, public backend exposure or shared runtime transition is implied by ROADMAP v4 approval.
