# ROADMAP

Version: 2.4
Status: APPROVED
Project: K-Geopolitical Monitor

## Development principle

Minimal Functional Core First.

The project is developed through validation stages. Implementation does not equal validation.

Implementation milestone labels M0-M13 are engineering work packages and are not identical to ROADMAP phase numbers.

No ROADMAP Phase 12 and no M14 are approved at this checkpoint.

## Phases

## Phase 0 - Project Foundation

Goals:
- establish project governance;
- approve documentation standards;
- preserve approved product concept.

Gate:
PHASE_0_APPROVED

## Phase 1 - Minimal Functional Core Specification

Goals:
- define minimum end-to-end monitoring pipeline;
- define contracts for sources, events, evidence, verification, forecasting and reports.

## Phase 2 - Minimal Functional Core Implementation

Implement source registry, discovery, event normalization, entity resolution, deduplication, verification, storyline linking, importance scoring, forecasting and reporting.

## Phase 3 - Core Validation and Calibration

Validate evidence handling, contradictions, event lifecycle, forecast updates and report quality.

## Phase 4 - Adaptive Learning Foundation

Implement controlled detection of source drift, platform changes, relationship changes and forecast performance changes.

## Phase 5 - Controlled Pilot Monitoring

Validated engineering foundation:
- M5 project-local operational baseline: PASS;
- M6 deterministic controlled pilot baseline: PASS;
- M7 live public-source acquisition pilot: PASS;
- M8 live end-to-end controlled pilot processing: PASS;
- Consilium RSS live smoke: PASS;
- GDELT DOC 2.0 live smoke: PASS;
- source provenance and collection audit: PASS;
- origin-based verification independence: PASS;
- live-source failure isolation: PASS;
- project-local operational finding projection: PASS.

Phase 5 engineering baseline status:
BASELINE_VALIDATED

Phase 5 completion does not approve production/global operation, unattended continuous monitoring, shared runtime storage or automatic VERIFIED status.

## Phase 6 - Strategic Alerts and Continuous Monitoring

Validated engineering foundation:
- persisted watch alert policies: PASS;
- trigger thresholds and traceable finding-to-alert projection: PASS;
- stable deduplication and cross-cycle updates: PASS;
- OPEN/UPDATED/INVALIDATED/RESOLVED lifecycle: PASS;
- restart persistence and priority/cadence separation: PASS;
- project-local runtime storage: PASS.

M9 hardened regression:
- GitHub Actions run 32965387054;
- 82 passed in 1.71s.

Phase 6 engineering baseline status:
BASELINE_VALIDATED

## Phase 7 - Multi-Region Expansion

Validated engineering foundation:
- canonical region/language registries: PASS;
- watch-scoped region/language requirements: PASS;
- raw-item attribution and coverage reporting: PASS;
- cross-watch attribution isolation: PASS;
- translation metadata verification-isolation: PASS;
- project-local runtime storage: PASS.

M10 regression:
- GitHub Actions run 32966128001;
- 88 passed in 2.07s.

Phase 7 engineering baseline status:
BASELINE_VALIDATED

## Phase 8 - Advanced Geopolitical Graph

Validated engineering foundation:
- M4 graph fragments converged into one durable M11 graph contract: PASS;
- migration 010 graph persistence: PASS;
- deterministic node/logical-edge identity: PASS;
- actor/event/claim/finding projection: PASS;
- evidence-backed relationship lifecycle and material history: PASS;
- temporal validity and historical snapshots: PASS;
- bounded cycle-safe causal/influence traversal: PASS;
- advanced explainable IntelligenceQuery facade: PASS;
- M8/M10/M11 truth-isolation: PASS;
- project-local runtime storage: PASS;
- external graph provider dependency: NONE.

M11 final regression:
- GitHub Actions run 32973378757;
- 118 passed in 4.24s.

Phase 8 engineering baseline status:
BASELINE_VALIDATED

## Phase 9 - Advanced Forecasting

Validated engineering foundation:
- durable forecast identity and immutable version history: PASS;
- raw/calibrated probability separation: PASS;
- typed provenance-bound inputs and fail-closed references: PASS;
- immutable scenario lifecycle and signal analysis: PASS;
- durable outcome resolution and exact-version evaluation: PASS;
- PARTIAL/AMBIGUOUS non-scoring: PASS;
- reproducible calibration history and performance breakdowns: PASS;
- advanced forecast query/provenance/history facade: PASS;
- M8/M11 truth-state isolation: PASS;
- project-local runtime storage: PASS;
- external forecasting provider dependency: NONE.

M12 final regression:
- GitHub Actions run 32980859938;
- 154 passed in 8.19s.

Phase 9 engineering baseline status:
BASELINE_VALIDATED

## Phase 10 - Full Reporting Environment

Validated engineering foundation:
- migration 015 common report snapshot/section/reference persistence: PASS;
- deterministic immutable report identities and fail-closed canonical references: PASS;
- one common ReportAssembler with typed provenance: PASS;
- source evidence, graph inference and forecast scenario separation: PASS;
- Strategic Alert report: PASS;
- Global Geopolitical Brief: PASS;
- Regional/Country Brief with explicit region/language coverage metadata: PASS;
- Event Dossier: PASS;
- report-scoped Storyline Report without canonical storyline truth table: PASS;
- version-anchored Forecast Report: PASS;
- scope-only Strategic Outlook: PASS;
- deterministic structured representation: PASS;
- deterministic Markdown rendering: PASS;
- restart rendering reproducibility: PASS;
- M8/M10/M11/M12 read-only isolation: PASS;
- project-local runtime database enforcement: PASS;
- external reporting/publishing provider dependency: NONE.

M13 validation progression:
- M13.1 run 32982639826 - 160 passed in 11.40s;
- M13.2 run 32989895962 - 170 passed in 12.00s;
- M13.3-M13.5 run 32992328055 - 193 passed in 10.98s;
- M13.6 run 32993269910 - 199 passed in 12.10s.

Phase 10 engineering baseline status:
BASELINE_VALIDATED

Phase 10 completion does not approve external publishing/delivery, global operational coverage, shared runtime storage, production dashboards or production/live OPERATIONAL status.

## Phase 11 - Global Operational Coverage

Validated engineering foundation:
- explicit deterministic coverage contracts and typed requirements: PASS;
- migrations 016-017 durable coverage snapshots/results and per-source collection attempts: PASS;
- adapter/item source identity fail-closed integrity: PASS;
- SOURCE_CLASS and SOURCE_ID/SOURCE_AVAILABILITY convergence: PASS;
- REGION_LANGUAGE convergence with watch isolation: PASS;
- explicit persisted freshness evaluation: PASS;
- SATISFIED/GAP/UNAVAILABLE/STALE/UNKNOWN/UNMEASURED status separation: PASS;
- deterministic coverage_ratio and coverage_confidence with distinct semantics: PASS;
- source count cannot inflate coverage units: PASS;
- immutable historical/latest coverage query: PASS;
- M13 Global/Regional coverage reporting integration without a parallel report store: PASS;
- UNKNOWN and UNMEASURED remain visible in structured and Markdown output: PASS;
- M8/M10/M11/M12/M13 isolation: PASS;
- GLOBAL scope does not suppress explicit gaps or imply universal completeness: PASS;
- project-local runtime database enforcement: PASS;
- external coverage provider dependency: NONE.

Phase 11 validation progression:
- P11.1 run 32996565227 - 203 passed in 15.48s;
- P11.2 run 32997440380 - 210 passed in 16.63s;
- P11.3 run 32997961490 - 217 passed in 27.46s;
- P11.4 run 32999092257 - 219 passed in 20.55s;
- P11.5 run 32999835225 - 223 passed in 83.96s;
- P11.6 run 33000478908 - 226 passed in 17.67s.

Phase 11 engineering baseline status:
BASELINE_VALIDATED

Phase 11 validates the ability to explicitly define, measure, persist, query and report operational coverage. It does not prove complete real-time monitoring of every country, language, actor, storyline or source. Production/live status remains NOT_OPERATIONAL.

## Unnumbered Post-Phase-11 Owner-Only GPT Pilot

This activity is not ROADMAP Phase 12 and does not create M14.

Validated preparation:
- owner-only private K-Geopolitical Monitor GPT configured;
- Web Search enabled;
- Code Interpreter/Data Analysis enabled;
- no Knowledge files required for initial pilot;
- no backend Action/API connected;
- unattended supervisor and cadence-safe live operational cycle implemented and regression-tested;
- GitHub Actions run 33012596904: 236 passed.

Final pilot matrix:
- test_case_count: 18;
- passed_count: 18;
- failed_count: 0;
- blocked_count: 0;
- critical truth-boundary violations: 0;
- hallucinated/untraceable source failures: 0;
- verification-boundary failures: 0;
- coverage-boundary failures: 0;
- backend-access hallucination failures: 0.

Closure validation:
- GPT-18/full matrix closure run 33046581445: SUCCESS;
- owner-only pilot plan closure run 33046621582: SUCCESS;
- post-pilot retrospective/expansion-plan run 33046677596: SUCCESS.

Pilot status:
OWNER_ONLY_PILOT_PASS

The pilot validates user-facing research and truth-boundary behavior for continued owner-only use. It does not approve production/live operation, public sharing, external delivery, shared runtime storage or backend Action access.

## Approved Unnumbered Post-Pilot Expansion Workstreams

These workstreams are post-Phase-11 engineering/planning activities. They are not a new numbered ROADMAP phase.

### E1 - Automatic Translation Foundation

State:
BASELINE_VALIDATED

Validated foundation:
- migration 018 durable raw_item_translations store: PASS;
- original raw-item text remains unchanged: PASS;
- translated text stored separately: PASS;
- source/target language and method/provider/version metadata: PASS;
- SUCCESS/FAILED/UNAVAILABLE/UNSUPPORTED/AMBIGUOUS states: PASS;
- ambiguity/failure remains visible: PASS;
- versioned retranslation history: PASS;
- live translation inherits normalized original publisher host: PASS;
- non-live fallback origin uses source identity: PASS;
- translation never creates new independent-source credit: PASS;
- M8 verification and independent-origin count unchanged: PASS;
- restart persistence: PASS;
- external translation provider dependency: NONE.

E1 canonical regression:
- GitHub Actions run 33244484173;
- 241 passed in 37.10s.

E1 completion does not activate external automatic translation and does not approve production/live operation.

### Remaining workstreams

Execution order:
- E2 Source Reputation and Status History - P0 - APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION - CURRENT;
- E3 Private GPT Backend Action API - P0 - APPROVED_FOR_DESIGN;
- E4 Free Unattended Runtime Deployment - P0 - APPROVED_FOR_VALIDATION;
- E5 Admin Read-Only Dashboard - P1 - PLANNED;
- E6 Reproducibility Instrumentation - P1 - PLANNED;
- E7 Forecast Probability Semantics - P1 - PLANNED;
- E8 Controlled External Sharing / Public GPT - DEFERRED - NOT_APPROVED;
- E9 Shared Production Runtime - DEFERRED - NOT_APPROVED.

Post-pilot invariants:
- runtime storage remains PROJECT_LOCAL_ONLY;
- no shared runtime database;
- no implicit mixed storage;
- no translation-based source independence;
- no graph-based source independence;
- no forecast-to-fact promotion;
- no coverage-to-verification promotion;
- no report-presentation truth inflation;
- no public-web substitution for persisted backend state;
- no external provider activation without explicit approval.

## Current implementation checkpoint

- Product Concept: APPROVED
- Roadmap: APPROVED
- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph: BASELINE_VALIDATED
- ROADMAP Phase 9 Advanced Forecasting: BASELINE_VALIDATED
- ROADMAP Phase 10 Full Reporting Environment: BASELINE_VALIDATED
- ROADMAP Phase 11 Global Operational Coverage: BASELINE_VALIDATED
- Owner-only private GPT pilot: SUCCESSFUL, 18/18 PASS
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- Shared Infrastructure Architecture Review: COMPLETE; HYBRID adopted
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Controlled-pilot external integrations: 2
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External coverage providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- External translation provider: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Private GPT backend Action/API: NOT_CONNECTED
- Unattended cloud runtime: NOT_DEPLOYED
- Public sharing: DEFERRED
- Shared production runtime: NOT_APPROVED
- Current engineering activity: E2 Source Reputation and Status History design and local implementation
- Next roadmap phase: NONE_APPROVED
- Production/live operational status: NOT_OPERATIONAL
