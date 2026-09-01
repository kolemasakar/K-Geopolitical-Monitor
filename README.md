# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.6
Status: ACTIVE / ROADMAP_V4_PHASE_12 / P12_5_VALIDATED_WITH_MEASURED_DEGRADATION

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
- `docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY.md` — P12.5 implementation;
- `docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md` — P12.5 result;
- `docs/implementation/P12_5_CONTROLLED_LIVE_SOURCE_HEALTH_MATRIX.md` — P12.5 controlled-live evidence;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_5_SOURCE_HEALTH_EGRESS_VALIDATED.md` — current checkpoint.

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
- P12.5: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- current/next engineering activity: `P12.6_PHASE_12_VALIDATION_MATRIX / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## P12.5 Validation Evidence

Validation anchor: `92d0c0516351e2af7ba836d3ae711dd414d22023`.

- x64 CI: run `33533313297`, job `99941475948`, `382 passed, 1 warning / SUCCESS`;
- native ARM64: run `33533313313`, job `99941475266`, native `aarch64`, `382 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS;
- controlled-live: run `33533313654`, job `99941475574`, workflow `SUCCESS`, `10/10` source paths measured, `8 SUCCESS / 2 FAILED`.

P12.5 validates measurement completeness and egress inventory, not an all-sources-healthy claim.

## P12.5 Measured Health / Freshness

Controlled-live findings:
- European Parliament Press Releases — governed `DEGRADED`; measured `UNAVAILABLE / PARSER`;
- Haberturk — governed `ACTIVE`; measured `UNAVAILABLE / UNKNOWN` because an item `original_url` failed HTTP/HTTPS validation;
- OSCE Latest News — acquisition `HEALTHY`; observed publisher content `STALE`;
- Consilium and European Commission — acquisition `HEALTHY`, zero bounded watch matches, content freshness `UNKNOWN`;
- GDELT, Meduza, RMF24, Ukrainska Pravda and GOV.UK — acquisition `HEALTHY` in the probe; content freshness is recorded only when a parseable source timestamp exists.

A governed portfolio state and a measured operational observation are deliberately separate. P12.5 did not silently rewrite P12.3/P12.4 governance from a single probe.

## Measured Egress Inventory

P12.5 inventoried ten current HTTPS host requirements:
`api.gdeltproject.org`, `ec.europa.eu`, `feeds.osce.org`, `meduza.io`, `rss.haberturk.com`, `www.consilium.europa.eu`, `www.europarl.europa.eu`, `www.gov.uk`, `www.pravda.com.ua`, `www.rmf24.pl`.

This is measurement evidence, not a deployed firewall allowlist. Broad outbound egress remains an explicit owner-approved candidate exception pending a separate decision.

## Local-Language and Media Discovery Pack

P12.4 validated the initial governed language slice:
- `uk` — Ukrainska Pravda;
- `ru` — Meduza;
- `pl` — RMF24;
- `tr` — Haberturk.

P12.4's bounded validation observed four successful acquisition/parser paths. P12.5 is the later health measurement and therefore records the Haberturk item-URL validation failure separately without erasing the historical P12.4 result.

Original-language Unicode content and source URL are preserved. Translation remains a separate derived representation and does not create another source or independent origin.

The `uk/ru/pl/tr` pack is a prioritized initial language slice, not global language coverage, continuous source-health proof or exhaustive regional coverage.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status and source-portfolio metadata are not truth operators;
- adapter/source/domain/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count;
- operational source health or content freshness does not promote factual verification;
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

P12.5 measured outbound requirements but did not deploy egress restriction.

## Source / Integration State

Consilium and GDELT remain validated baseline integrations. P12.3 authoritative and P12.4 local-language/media packs remain governed. P12.5 adds the validated read-only health/freshness/egress assessment layer and explicit current controlled-live observations.

GDELT discovery is not independent factual corroboration. No source, media, domain, adapter, host or language count is treated as independent-origin count.

No paid source/data/translation/graph/forecast/reporting/coverage/notification provider is approved.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`; Start.me remains non-canonical.

## ROADMAP v4

- Phase 12 — ACTIVE; P12.0-P12.5 validated; P12.6 NEXT/NOT_STARTED.
- Phase 13 — approved sequential / not started.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, Business migration, public sharing, public backend exposure, outbound firewall restriction or shared runtime transition is implied by P12.5 validation.
