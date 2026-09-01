# Phase 12 — Intelligence Quality and Source Network Foundation Plan

Date: 2026-09-01
Status: `APPROVED_FOR_IMPLEMENTATION`
Project: K-Geopolitical Monitor
Roadmap: `ROADMAP.md / v4.0`
Decision: `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md`
Analysis: `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md`

## 1. Objective

Build a materially broader, measurable and maintainable public-source network and strengthen the source operating model without weakening the validated truth/provenance/coverage boundaries.

Phase 12 is a source-network and intelligence-input foundation phase. It does not claim exhaustive global coverage and does not activate production/live, public publication, shared runtime or paid providers.

## 2. Design Rules

- Preserve `PROJECT_LOCAL_ONLY` canonical runtime storage.
- Prefer public/free sources first.
- Every external source/integration receives an explicit integration record.
- Adapter/source identity is not evidence independence.
- Publisher/domain count is not automatically underlying-origin count.
- Translation does not create an independent source.
- GDELT or other discovery/index services do not become factual corroboration merely by discovering a link.
- Source failure must remain isolated and visible.
- Deterministic CI must not depend on live network availability.
- Coverage metrics measure configured requirements; they do not prove universal completeness.
- Model/LLM assistance may propose extraction/classification but cannot directly promote claim verification.
- Broad egress is not narrowed until the real approved source destination inventory is measured.

## 3. P12.0 — Canonical Convergence

State: `NEXT`

Required work:
- reconcile `ARCHITECTURE.md` with E9A closure and ROADMAP v4;
- reconcile `SECURITY_AND_DATA_POLICY.md` with completed E9A.6 real-host evidence;
- reconcile `EXTERNAL_INTEGRATIONS.md` with the owner-only candidate runtime and Phase 12 integration rules;
- review `README.md`, `PROJECT_HISTORY.md`, `SOURCE_POLICY.md`, `TEST_PLAN.md`, `DATA_MODELS.md`, `VERIFICATION_MODEL.md`, `FORECASTING_MODEL.md`, `REPORTING_MODEL.md` and other primary documentation for stale current-state claims;
- preserve accepted historical decisions/ADRs as historical records rather than rewriting them;
- run full regression after convergence.

Gate:
`P12_0_CANONICAL_CONVERGENCE_VALIDATED`

## 4. P12.1 — Source Portfolio Contract

State: `PLANNED`

Define a durable/versioned source-portfolio contract for:
- canonical source ID/name;
- publisher/organization identity;
- source class;
- source role: primary / official / media / discovery / structured-data / other approved role;
- region/language scope;
- access mode;
- public/free/credentialed classification;
- expected freshness/cadence;
- adapter/parser identity/version;
- required outbound domain/protocol;
- fallback/replacement source;
- source availability/degradation state;
- provenance/origin characteristics;
- independence caveats;
- licensing/terms notes where relevant;
- owner/review status;
- reputation/status linkage without automatic truth promotion.

Gate:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

## 5. P12.2 — Adapter Framework v2

State: `PLANNED`

Required capabilities:
- reusable HTTPS read-only transport;
- bounded timeout and payload size;
- explicit pagination/record limits;
- RSS/Atom and JSON framework support;
- source-specific parsing extensions;
- deterministic adapter/source identity checks;
- collection-attempt persistence;
- reproducibility/audit linkage;
- no secret leakage to logs;
- deterministic fixture testing;
- one adapter failure must not corrupt/block another source;
- live smoke workflows remain separate from deterministic regression.

Gate:
`P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

## 6. P12.3 — Priority Authoritative Source Pack

State: `PLANNED`

Select and validate a first materially broader authoritative source pack.

Candidate classes, subject to per-source technical/legal review:
- UN and selected UN agencies;
- EU institutions;
- NATO;
- OSCE;
- official foreign-affairs/government/defence sources;
- sanctions/regulatory/legal public sources;
- humanitarian/security institutions.

Selection criteria:
- strategic relevance;
- geographic/institutional diversity;
- public accessibility;
- stable machine-readable interface where possible;
- local-language or multilingual value;
- freshness;
- provenance clarity;
- maintenance cost.

No source is automatically considered independent corroboration of another source solely because it is a separate adapter/domain.

Gate:
`P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

## 7. P12.4 — Local-Language and Media Discovery Pack

State: `PLANNED`

Goals:
- expand discovery for priority regions/languages;
- record source-language and region attribution;
- preserve local-language gaps explicitly;
- preserve publisher/underlying-origin uncertainty;
- preserve translation isolation;
- support media/discovery feeds without treating syndication as corroboration;
- define quality/maintenance rules for source onboarding.

This gate should begin with a bounded priority-region set rather than pretending all global languages are covered at once.

Gate:
`P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

## 8. P12.5 — Source Health and Egress Inventory

State: `PLANNED`

Implement/validate portfolio-level operational measurements:
- source availability;
- last-success / last-attempt;
- freshness/staleness;
- adapter error rate;
- parser/drift signals;
- replacement/fallback readiness;
- destination domain/protocol inventory;
- outbound dependency categories for source collection, OS maintenance and approved tooling.

Output must distinguish:
- source unavailable;
- source stale;
- adapter/parser failure;
- network failure;
- unmeasured state.

Gate:
`P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

## 9. P12.6 — Validation Matrix

State: `PLANNED`

Required deterministic evidence:
- full x64 regression;
- full native ARM64 regression;
- source-contract validation;
- adapter fixture tests;
- source identity fail-closed tests;
- provenance/origin invariants;
- translation independence invariants;
- region/language coverage isolation;
- coverage-to-verification isolation;
- source reputation-to-truth isolation;
- reproducibility linkage;
- failure isolation;
- `PROJECT_LOCAL_ONLY` enforcement;
- no public API/dashboard exposure;
- no shared/mixed runtime storage.

Required controlled-live evidence:
- selected authoritative source pack live smoke;
- selected local-language/media discovery live smoke;
- source failure visibility;
- persisted collection attempts;
- coverage snapshot behavior with real availability/staleness conditions;
- real outbound destination inventory evidence.

Phase gate:
`PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

## 10. Explicit Non-Goals

Phase 12 does not:
- implement Phase 13 semantic claim/verification v2;
- deploy public API/dashboard;
- connect a public GPT Action;
- activate ChatGPT Business/publication;
- enable shared/team runtime;
- replace SQLite because of hypothetical scale;
- activate a paid provider without a separate integration decision;
- claim complete global coverage;
- automatically alter source reputation/truth policy from drift metrics;
- set `PRODUCTION_LIVE = OPERATIONAL`.

## 11. Security Constraints

Current explicit candidate exceptions remain:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Phase 12 owns the **egress inventory**, not automatic egress restriction.
Private-admin/SSH final disposition belongs to the later owner operational activation gate unless separately requested earlier.

## 12. Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me may be used only as a non-canonical operator/navigation surface for public, non-sensitive URLs, RSS feeds, source names and classifications.

It must not store credentials, private runtime state, canonical evidence, sensitive findings or monitoring state and must not become a coverage authority.

## 13. Exact Start Point

The first engineering task in the next chat is:

`P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`

No P12.1 implementation begins until P12.0 is validated and saved to canonical state.
