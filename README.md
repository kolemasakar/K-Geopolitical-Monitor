# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.8
Status: ACTIVE / ROADMAP_V4 / PHASE_13_ACTIVE / P13.0_PENDING_VALIDATION

## Purpose

K-Geopolitical Monitor supports discovery, provenance-aware verification, geopolitical analysis, forecasting, reporting, operational monitoring and explicit coverage assessment of significant developments.

## Canonical Documentation

- `ROADMAP.md` — ROADMAP v4 and current phase state;
- `ARCHITECTURE.md` — architecture/truth/storage/runtime boundaries;
- `SECURITY_AND_DATA_POLICY.md` — security/data policy;
- `EXTERNAL_INTEGRATIONS.md` — integration/source rules;
- `SOURCE_POLICY.md` — source/provenance governance;
- `DATA_MODELS.md` — canonical data-model summary;
- `PROJECT_HISTORY.md` — chronological project record;
- `docs/implementation/PHASE_12_INTELLIGENCE_QUALITY_SOURCE_NETWORK_PLAN.md` — Phase 12 closure;
- `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md` — active Phase 13 implementation contract/plan;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_6_PHASE_12_VALIDATED.md` — latest closed-phase checkpoint.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 12 final closure HEAD: `3211994450c11698a553f5249e3ecec94079b5ad`;
- P12.3: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- P12.4: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- P12.5: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- P12.6: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- current engineering activity: `P13.0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT`;
- P13.0: `CURRENT / IMPLEMENTED_PENDING_VALIDATION`;
- P13.1-P13.6: `PLANNED / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## Phase 12 Final Closure Evidence

- x64 CI: run `33552777066`, job `100006077954`, `391 passed, 1 warning / SUCCESS`;
- native ARM64: run `33552776997`, job `100006077747`, native `aarch64`, `391 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS;
- gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`.

Known Phase 12 source/network limitations remain explicit: European Parliament unattended acquisition degradation, Haberturk item-URL failure observation, OSCE stale observed content, limited `uk/ru/pl/tr` language slice, broad outbound egress and public SSH candidate exceptions.

## Phase 13 — Semantic Verification and Provenance Intelligence

Phase 13 addresses the gap between the project's strong epistemic policy and the current executable analytical baseline.

Audited baseline:
- legacy `claims/evidence` are minimal;
- live claim identity is still normalized-title based;
- `live_analysis_evidence` uses `origin_host`;
- live verification currently uses distinct host count as a `PARTLY_VERIFIED` threshold;
- baseline confidence derives an independence term from source-ID count;
- contradiction reasoning is minimal.

These remain historical compatibility behavior until a later Phase 13 cutover. They are **not** the rules for the new semantic layer.

### P13.0 Current Contract

`P13.0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT`

P13.0 creates no database migration. It establishes the fail-closed architecture for subsequent additive semantic persistence:
- semantic claim identity is not headline identity;
- one publication may contain multiple claims;
- publisher/publication, cited source and underlying origin are distinct provenance concepts;
- typed evidence relations (`SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`) do not themselves determine final truth state;
- evidentiary independence is explicit and cannot be inferred from different hosts/domains/publishers/languages;
- contradiction becomes typed/versioned analytical state;
- verification promotion remains policy-controlled and auditable;
- extraction confidence, factual verification confidence and coverage confidence remain separate;
- model/LLM extraction may propose structured objects but cannot directly promote canonical truth.

Planned Phase 13 work packages:
`P13.0 contract -> P13.1 semantic claims -> P13.2 provenance/origin -> P13.3 evidence/independence -> P13.4 contradictions -> P13.5 verification/confidence -> P13.6 live cutover/validation`.

## Local-Language / Translation Boundary

Original-language Unicode content and source URL remain preserved. **Translation remains a separate derived representation**; translation does not create another source, publisher, underlying origin or independent corroboration. The validated `uk/ru/pl/tr` slice remains explicitly non-global.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status, portfolio metadata, source health and freshness are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- adapter/source/domain/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count;
- source/domain/media/language/adapter/item/host count is not independent-origin count;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- missing/uninstrumented tool history is never reconstructed and labeled exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state.

## Runtime / Security State

- owner-only OCI Ubuntu 24.04 ARM64 runtime remains candidate-ready;
- public KGM HTTP/HTTPS/database/API/dashboard ingress: not approved/not deployed;
- backend HTTPS: not deployed;
- private GPT backend Action: not connected;
- dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public GPT sharing: user-deferred;
- production/live: not operational;
- paid providers: `NONE_APPROVED`.

Remaining explicit owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

## ROADMAP v4

- Phase 12 — validated with known limitations; P12.0-P12.6 validated gates remain canonical.
- Phase 13 — `APPROVED / ACTIVE_ENGINEERING_PHASE`; P13.0 current/pending validation.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, public sharing, public backend exposure, shared runtime transition or paid-provider activation is implied by Phase 13 engineering work.
