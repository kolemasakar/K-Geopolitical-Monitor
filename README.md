# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.5
Status: ACTIVE / ROADMAP_V4_PHASE_12 / P12_4_VALIDATED

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
- `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK.md` — P12.4 implementation;
- `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md` — P12.4 result;
- `docs/implementation/P12_4_CONTROLLED_LIVE_LANGUAGE_SOURCE_MATRIX.md` — P12.4 controlled-live evidence;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED.md` — current checkpoint.

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
- P12.3: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- P12.4: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- current/next engineering activity: `P12.5_SOURCE_HEALTH_EGRESS_INVENTORY / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P12.4 Validation Evidence

Validation anchor: `595d7f0f0e6316e95aca518bb9309e615f239479`.

- x64 CI: run `33531518780`, job `99935566406`, `370 passed, 1 warning / SUCCESS`;
- native ARM64: run `33531518525`, job `99935564828`, native `aarch64`, `370 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS;
- controlled-live: run `33531518652`, job `99935565895`, `4 SUCCESS / 0 FAILED`.

## Local-Language and Media Discovery Pack

Validated initial language slice:

- `uk` — Ukrainska Pravda — `ACTIVE`;
- `ru` — Meduza — `ACTIVE`;
- `pl` — RMF24 — `ACTIVE`;
- `tr` — Haberturk — `ACTIVE`.

All four are public/free anonymous HTTPS media/discovery inputs using P12.1 governance and P12.2-compatible adapters. The controlled-live probe succeeded for transport/parsing on all four paths; zero native-query matches at a source are not transport failures.

Original-language Unicode content and source URL are preserved. Translation remains a separate derived representation and does not create another source or independent origin.

The `uk/ru/pl/tr` pack is a prioritized initial language slice, not global language coverage, continuous source-health proof or exhaustive regional coverage.

## P12.3 Retained Degradation

European Parliament Press Releases remains `DEGRADED` for unattended RSS acquisition because its official endpoint returns anti-bot HTML to the runner. The official endpoint remains canonical; no anti-bot bypass or third-party canonical mirror substitution is authorized.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status and source-portfolio metadata are not truth operators;
- adapter/source/domain/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count;
- portfolio approval does not establish evidence independence;
- acquisition/parser success or failure does not promote factual verification;
- translation remains derived and creates no independent origin;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
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

P12.5 owns measured source-health/freshness and real egress inventory before any outbound restriction proposal.

## Source / Integration State

Previously validated integrations remain Consilium press-release RSS and GDELT DOC 2.0 discovery/index metadata. P12.3 authoritative sources remain governed, including explicit European Parliament degradation. P12.4 adds the validated initial local-language media-discovery slice above.

GDELT discovery is not independent factual corroboration. No source, media, domain, adapter or language count is treated as independent-origin count.

No paid source/data/translation/graph/forecast/reporting/coverage/notification provider is approved.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`; Start.me remains non-canonical.

## ROADMAP v4

- Phase 12 — ACTIVE; P12.0-P12.4 validated; P12.5 NEXT/NOT_STARTED.
- Phase 13 — approved sequential / not started.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, Business migration, public sharing, public backend exposure or shared runtime transition is implied by P12.4 validation.
