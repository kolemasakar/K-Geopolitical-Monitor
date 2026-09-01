# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.4
Status: ACTIVE / ROADMAP_V4_PHASE_12 / P12_3_VALIDATED

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
- `docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK.md` — P12.3 implementation;
- `docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md` — P12.3 result;
- `docs/implementation/P12_3_CONTROLLED_LIVE_SOURCE_MATRIX.md` — P12.3 controlled-live evidence;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED.md` — current checkpoint.

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
- current/next engineering activity: `P12.4_LOCAL_LANGUAGE_AND_MEDIA_DISCOVERY_PACK / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P12.3 Validation Evidence

- validation anchor: `038122e44139d6ff23bc5d79bb50a8dee3c38cde`;
- x64 CI: run `33527433110`, job `99921745359`, `356 passed, 1 warning / SUCCESS`;
- native ARM64: run `33527433197`, job `99921746285`, `356 passed, 1 warning / SUCCESS`;
- controlled-live repeat: run `33527433106`, job `99921745640`, `3 SUCCESS / 1 European Parliament DEGRADED`.

P12.3 is validated with explicit degradation, not as a 4/4-health claim.

## Priority Authoritative Source Pack

Validated governed source states:

- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition: the official endpoint returns anti-bot HTML to the unattended runner rather than RSS XML;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

All pack sources are public/free, use P12.1 governance and P12.2-compatible read-only HTTPS adapter paths. The European Parliament official endpoint remains canonical; no anti-bot bypass or third-party mirror substitution is authorized.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status and source-portfolio metadata are not truth operators;
- adapter/source/domain/item count is not independent-origin count;
- portfolio approval does not establish evidence independence;
- acquisition/parser success or failure does not promote factual verification;
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

Previously validated controlled-live integrations remain Consilium press-release RSS and GDELT DOC 2.0 discovery/index metadata.

P12.3 adds the governed authoritative source pack described above. Controlled-live acquisition is currently successful for European Commission, GOV.UK and OSCE; European Parliament unattended RSS is explicitly `DEGRADED`.

GDELT discovery is not independent factual corroboration. No source count is treated as independent-origin count.

No paid source/data/translation/graph/forecast/reporting/coverage/notification provider is approved.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`; Start.me remains non-canonical.

## ROADMAP v4

- Phase 12 — ACTIVE; P12.0-P12.3 validated; P12.4 NEXT/NOT_STARTED.
- Phase 13 — approved sequential / not started.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, Business migration, public sharing, public backend exposure or shared runtime transition is implied by P12.3 validation.
