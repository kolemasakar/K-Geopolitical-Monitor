# ROADMAP

Version: 2.1
Status: APPROVED
Project: K-Geopolitical Monitor

## Development principle

Minimal Functional Core First.

The project is developed through validation stages. Implementation does not equal validation.

Implementation milestone labels M0-M13 are engineering work packages and are not identical to ROADMAP phase numbers.

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

Implement measurable coverage contracts and coverage confidence.

Preparation requirements:
- audit existing M6/M7/M8/M10 coverage semantics and reporting surfaces;
- define measurable operational coverage without treating coverage as factual verification confidence;
- preserve original-origin evidence independence;
- preserve PROJECT_LOCAL_ONLY runtime storage;
- do not claim global operational coverage until explicit acceptance gates pass.

Current engineering activity:
Phase 11 Global Operational Coverage preparation and delta audit.

## Current implementation checkpoint

- Product Concept: APPROVED
- Roadmap: APPROVED
- Engineering implementation: BASELINE_VALIDATED through M13
- M5 full test cycle: PASS - 57 tests, GitHub Actions run 32953343877
- M6 controlled pilot baseline: PASS - 62 tests, GitHub Actions run 32961649091
- M7 deterministic regression: PASS - 68 tests, GitHub Actions run 32962379499
- M7 live source smoke: PASS - GitHub Actions run 32962576874
- M8 deterministic regression: PASS - 73 tests, GitHub Actions run 32963096313
- M8 live end-to-end controlled pilot: PASS - GitHub Actions run 32963354135
- M9 hardened regression: PASS - 82 tests, GitHub Actions run 32965387054
- M10 multi-region/language regression: PASS - 88 tests, GitHub Actions run 32966128001
- M11 advanced geopolitical graph regression: PASS - 118 tests, GitHub Actions run 32973378757
- M12 advanced forecasting regression: PASS - 154 tests, GitHub Actions run 32980859938
- M13 full reporting environment regression: PASS - 199 tests, GitHub Actions run 32993269910
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph: BASELINE_VALIDATED
- ROADMAP Phase 9 Advanced Forecasting: BASELINE_VALIDATED
- ROADMAP Phase 10 Full Reporting Environment: BASELINE_VALIDATED
- Shared Infrastructure Architecture Review: COMPLETE; HYBRID adopted
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Controlled-pilot external integrations: 2
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 11 Global Operational Coverage preparation
- Next engineering activity: Phase 11 delta audit and implementation planning
- Production/live operational status: NOT_OPERATIONAL
