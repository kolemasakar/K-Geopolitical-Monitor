# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.12
Status: ACTIVE / ROADMAP_V4 / PHASE_13_ACTIVE / P13.3_VALIDATED / P13.4_CURRENT

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
- `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md` — active Phase 13 plan;
- `docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE_RESULT.md` — latest validated work-package result;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED.md` — latest saved gate checkpoint.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 12 final closure HEAD: `3211994450c11698a553f5249e3ecec94079b5ad`;
- P12.3: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- P12.4: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- P12.5: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- P12.6: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- P13.3: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- current engineering activity: `P13.4_TYPED_CONTRADICTION_MODEL`;
- P13.4: `CURRENT / NOT_STARTED`;
- P13.5-P13.6: `PLANNED / NOT_STARTED`;
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

Phase 13 addresses the gap between the project's strong epistemic policy and the historical executable analytical baseline.

Audited baseline remains compatibility state until a later validated cutover:
- legacy `claims/evidence` are minimal;
- live claim identity is normalized-title based;
- `live_analysis_evidence` uses `origin_host`;
- live verification uses distinct host count as a historical `PARTLY_VERIFIED` threshold;
- baseline confidence derives an independence term from source-ID count;
- contradiction reasoning is minimal.

These are not the rules for the new semantic layer.

### P13.0 Validated Contract

Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.
Validation anchor: `4422fae5e2a4546585a43237d2124f466c457543`.

- x64 run `33554568574`, job `100012110127`: `399 passed, 1 warning / SUCCESS`;
- native ARM64 run `33554568570`, job `100012110488`: native `aarch64`, `399 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.0 creates no database migration. It validates the fail-closed architecture for subsequent additive semantic persistence:
- semantic claim identity is not headline identity;
- one publication may contain multiple claims;
- publisher/publication, cited source and underlying origin are distinct provenance concepts;
- typed evidence relations (`SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`) do not themselves determine final truth state;
- evidentiary independence is explicit and cannot be inferred from different hosts/domains/publishers/languages;
- contradiction becomes typed/versioned analytical state;
- verification promotion remains policy-controlled and auditable;
- extraction confidence, factual verification confidence and coverage confidence remain separate;
- model/LLM extraction may propose structured objects but cannot directly promote canonical truth.

### P13.1 Validated Package

Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.

- x64 run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`;
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.1 is the first schema-bearing Phase 13 package and is additive only:
- migration `023_structured_semantic_claim_model.sql` adds append-only `semantic_claim_versions` and `semantic_claim_links`;
- semantic claim identity is explicit/caller-controlled rather than inferred from normalized headline or matching text;
- structured fields cover proposition, claimant/actor, subject, object/theme, event/action type, polarity, modality, time, location, quantity, original language and extraction metadata;
- `semantic_claim_links` associate semantic versions with legacy claims, live-analysis claims and raw items without declaring evidence stance, provenance origin or independence;
- Unicode/original-language content is preserved;
- `extraction_confidence` is extraction-only and cannot promote factual truth;
- P13.2-P13.5 fields for origin, independence, contradiction and verification policy are intentionally absent.

### P13.2 Validated Package

Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.
Validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.

- x64 run `33558425194`, job `100024835794`: `420 passed, 1 warning / SUCCESS`;
- native ARM64 run `33558425252`, job `100024836399`: native `aarch64`, `420 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.2 adds explicit provenance/origin persistence without truth promotion:
- migration `024_semantic_provenance_origin_relation_model.sql` adds append-only provenance entities, claim provenance roles and provenance relations;
- publication/publisher, immediate acquired source, cited/quoted source and underlying origin are distinct;
- official statements/documents, wire reports, datasets, social/user-provided and unresolved/mixed origins are represented explicitly;
- citation, syndication, repost, translation and derivation relations do not create independent corroboration;
- `UNKNOWN/UNRESOLVED` origin remains explicit rather than inferred from different publisher/domain/language;
- source/raw traceability fails closed on identity mismatch and canonical URLs reject credential leakage;
- legacy provenance API compatibility is preserved;
- P13.3 independence/evidence stance, P13.4 contradiction, P13.5 verification/confidence and P13.6 cutover remain outside this package.

### P13.3 Validated Package

Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.
Validation anchor: `639d6b2e64d618edfbe742636cb2ac0f663c68ee`.

- x64 run `33575533714`, job `100078564552`: `434 passed, 1 warning / SUCCESS`;
- native ARM64 run `33575533657`, job `100078564729`: native `aarch64`, `434 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.3 adds typed evidence relations and explicit pairwise evidentiary-independence assessment without final truth promotion:
- migration `025_semantic_evidence_relation_independence.sql` adds append-only `semantic_evidence_relation_versions` and `semantic_independence_assessment_versions`;
- evidence relations are `SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY` or `DUPLICATE_OR_SAME_ORIGIN`;
- independence states are `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN` and `MIXED`;
- same-origin, syndication, translation, citation and current derivation paths do not create independent corroboration;
- different publisher/domain/language, source, host or item identity is not sufficient independence proof;
- absence of a known derivation path remains `UNKNOWN`, not automatically `INDEPENDENT`;
- automated inference uses only current P13.2 provenance-relation versions while superseded edges remain audit history;
- evidence relation and independence metadata do not themselves determine or promote final verification state;
- P13.4 contradiction lifecycle, P13.5 verification/confidence and P13.6 live cutover remain outside this package.

### P13.4 Current Package

`P13.4_TYPED_CONTRADICTION_MODEL / CURRENT_NOT_STARTED`.

P13.4 must add typed, versioned contradiction objects and an auditable unresolved/evolving/resolved lifecycle across dimensions including occurrence/existence, attribution/responsibility, actor identity, quantity/value, time, location, status/outcome and scope/extent. A claim/denial pair is not automatically resolved by source reputation or independence metadata.

Verification promotion and multidimensional factual confidence remain P13.5. Live analytical cutover remains P13.6.

Planned Phase 13 sequence:
`P13.0 validated contract -> P13.1 validated semantic claims -> P13.2 validated provenance/origin -> P13.3 validated evidence/independence -> P13.4 contradictions -> P13.5 verification/confidence -> P13.6 live cutover/validation`.

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
- Phase 13 — `APPROVED / ACTIVE_ENGINEERING_PHASE`; P13.0-P13.3 validated, P13.4 current/not started.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, public sharing, public backend exposure, shared runtime transition or paid-provider activation is implied by Phase 13 engineering work.