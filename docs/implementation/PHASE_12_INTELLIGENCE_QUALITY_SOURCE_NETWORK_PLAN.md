# Phase 12 — Intelligence Quality and Source Network Foundation Plan

Date: 2026-09-01
Status: `APPROVED_FOR_IMPLEMENTATION / P12_0_VALIDATED`
Project: K-Geopolitical Monitor
Roadmap: `ROADMAP.md / v4.0`
Decision: `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md`
Analysis: `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md`

## 1. Objective

Build a materially broader, measurable and maintainable public-source network and strengthen the source operating model without weakening validated truth/provenance/coverage boundaries.

Phase 12 does not claim exhaustive global coverage and does not activate production/live, public publication, shared runtime or paid providers.

## 2. Design Rules

- Preserve `PROJECT_LOCAL_ONLY` canonical runtime storage.
- Prefer public/free sources first.
- Every external source/integration receives an explicit integration record.
- Adapter/source identity is not evidence independence.
- Publisher/domain count is not automatically underlying-origin count.
- Translation does not create an independent source.
- Discovery/index services do not become factual corroboration merely by discovering a link.
- Source failure remains isolated and visible.
- Deterministic CI does not depend on live network availability.
- Coverage metrics measure configured requirements; they do not prove universal completeness.
- Model/LLM assistance may propose extraction/classification but cannot directly promote claim verification.
- Broad egress is not narrowed until the real approved source destination inventory is measured.

## 3. P12.0 — Canonical Convergence

State: `VALIDATED`
Gate: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`
Result: `docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_0_CANONICAL_CONVERGENCE_VALIDATED.md`
Validation commit: `374beb4664cd92a4f41063cbbe30f6830ee3a831`
Validation CI: run `33517021594`, job `99886494759`, `318 passed, 1 warning / SUCCESS`

Completed work:
- reconciled architecture with E9A closure/ROADMAP v4;
- reconciled security policy with completed E9A.6 evidence;
- reconciled integrations/source policy with owner-only candidate runtime and Phase 12 rules;
- reviewed secondary canonical documents for stale current-state claims;
- preserved historical decisions/ADRs;
- completed full deterministic regression.

## 4. P12.1 — Source Portfolio Contract

State: `NEXT / NOT_STARTED`

Define a durable/versioned source-portfolio contract for:
- canonical source ID/name and publisher/organization identity;
- source class/role;
- region/language scope;
- ownership/operator responsibility;
- public/free/credentialed access mode;
- licensing/terms notes where relevant;
- expected freshness/cadence;
- adapter/parser identity/version;
- required outbound destination/protocol;
- fallback/replacement source;
- availability/degradation state;
- data classification;
- provenance/origin characteristics and independence caveats;
- owner/review status;
- reputation/status linkage without automatic truth promotion.

Gate:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

## 5. P12.2 — Adapter Framework v2

State: `PLANNED`

Required capabilities:
- reusable HTTPS read-only transport;
- bounded timeout/payload/pagination/record limits;
- RSS/Atom and JSON framework support;
- source-specific parsing extensions;
- deterministic adapter/source identity checks;
- collection-attempt persistence and reproducibility linkage;
- no secret leakage to logs;
- deterministic fixture testing;
- source-failure isolation;
- live smoke workflows separate from deterministic regression.

Gate: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

## 6. P12.3 — Priority Authoritative Source Pack

State: `PLANNED`

Select and validate a materially broader authoritative public-source pack, subject to source-specific technical/legal review. Candidate classes include UN/UN agencies, EU institutions, NATO, OSCE, official foreign-affairs/government/defence sources, sanctions/regulatory/legal public sources and humanitarian/security institutions.

Selection criteria include strategic relevance, diversity, public accessibility, machine readability where possible, local-language/multilingual value, freshness, provenance clarity and maintenance cost.

Source count is not independent corroboration count.

Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

## 7. P12.4 — Local-Language and Media Discovery Pack

State: `PLANNED`

Goals: expand priority region/language discovery, preserve source-language/region attribution, expose local-language gaps, preserve publisher/underlying-origin uncertainty and translation isolation, and define quality/maintenance rules for source onboarding.

Start with bounded priority regions rather than claiming all global languages are covered.

Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

## 8. P12.5 — Source Health and Egress Inventory

State: `PLANNED`

Measure source availability, last-success/last-attempt, freshness/staleness, adapter error rate, parser/drift signals, replacement readiness, destination domain/protocol inventory and outbound dependency categories.

Distinguish source unavailable, source stale, adapter/parser failure, network failure and unmeasured state.

Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

## 9. P12.6 — Validation Matrix

State: `PLANNED`

Required evidence includes full x64/native ARM64 regression, source-contract validation, adapter fixtures, source identity fail-closed tests, provenance/origin invariants, translation independence, region/language/coverage isolation, coverage-to-verification isolation, reputation-to-truth isolation, reproducibility linkage, failure isolation, `PROJECT_LOCAL_ONLY`, no public API/dashboard exposure and no shared/mixed runtime storage.

Controlled-live evidence includes selected authoritative and local-language/media live smoke, source-failure visibility, persisted attempts, real availability/staleness coverage behavior and outbound destination inventory.

Phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

## 10. Explicit Non-Goals

Phase 12 does not implement Phase 13 semantic verification v2, deploy public API/dashboard, connect public GPT Action, activate Business/publication, enable shared/team runtime, replace SQLite for hypothetical scale, activate paid providers without separate approval, claim complete global coverage, automatically change truth policy from drift metrics, or set `PRODUCTION_LIVE = OPERATIONAL`.

## 11. Security Constraints

Current explicit candidate exceptions remain public SSH TCP/22 from `0.0.0.0/0` and broad outbound egress. Phase 12 owns the egress inventory, not automatic egress restriction. Private-admin/SSH final disposition belongs to later owner operational activation unless separately requested.

## 12. Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me may be used only as a non-canonical operator/navigation surface for public, non-sensitive URLs, RSS feeds, source names/classes and public analytical resources. It must not store credentials, private runtime state, canonical evidence, sensitive findings or monitoring state and must not become a coverage authority.

## 13. Exact Next Point

Next engineering activity:
`P12.1_SOURCE_PORTFOLIO_CONTRACT_AND_GOVERNANCE`

State:
`NEXT / NOT_STARTED`

No P12.2 implementation begins until P12.1 is validated and saved to canonical state.
