# ROADMAP

Version: 1.9
Status: APPROVED
Project: K-Geopolitical Monitor

## Development principle

Minimal Functional Core First.

The project is developed through validation stages. Implementation does not equal validation.

Implementation milestone labels M0-M12 are engineering work packages and are not identical to ROADMAP phase numbers.

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

Scope:
- limited storylines;
- limited sources;
- validation-oriented design.

## Phase 2 - Minimal Functional Core Implementation

Implement:
- source registry;
- discovery;
- event normalization;
- entity resolution;
- deduplication;
- verification;
- storyline linking;
- importance scoring;
- forecasting;
- reporting.

## Phase 3 - Core Validation and Calibration

Validate:
- evidence handling;
- contradictions;
- event lifecycle;
- forecast updates;
- report quality.

## Phase 4 - Adaptive Learning Foundation

Implement controlled detection of:
- source drift;
- platform changes;
- relationship changes;
- forecast performance changes.

## Phase 5 - Controlled Pilot Monitoring

Expand carefully:
- regions;
- actors;
- source classes;
- scheduled monitoring.

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

Add:
- trigger detection;
- invalidation detection;
- priority watches.

Validated engineering foundation:
- persisted watch alert policies: PASS;
- importance/confidence/verification-rank trigger thresholds: PASS;
- traceable finding-to-alert projection: PASS;
- stable normalized-title alert deduplication: PASS;
- repeated-evaluation idempotence: PASS;
- cross-cycle alert update: PASS;
- OPEN/UPDATED/INVALIDATED/RESOLVED state support: PASS;
- explicit invalidation history: PASS;
- restart persistence: PASS;
- NORMAL/HIGH/CRITICAL priority ordering: PASS;
- priority/cadence separation: PASS;
- project-local runtime storage: PASS.

M9 hardened regression:
- GitHub Actions run 32965387054;
- 82 passed in 1.71s.

Phase 6 engineering baseline status:
BASELINE_VALIDATED

Phase 6 completion does not approve external notification providers, unattended production scheduling, global coverage, shared runtime storage or production/live OPERATIONAL status.

## Phase 7 - Multi-Region Expansion

Expand regional and language coverage.

Validated engineering foundation:
- canonical region registry: PASS;
- canonical language registry: PASS;
- watch-scoped region/language requirements: PASS;
- raw-item region/language attribution: PASS;
- required/observed/missing scope reporting: PASS;
- coverage ratio persistence: PASS;
- cross-watch attribution isolation: PASS;
- restart persistence: PASS;
- translation metadata verification-isolation: PASS;
- project-local runtime storage: PASS.

M10 regression:
- GitHub Actions run 32966128001;
- 88 passed in 2.07s.

Phase 7 engineering baseline status:
BASELINE_VALIDATED

Phase 7 completion does not approve global production coverage, automatic translation providers, shared runtime storage or production/live OPERATIONAL status.

## Phase 8 - Advanced Geopolitical Graph

Develop:
- actor graph;
- event graph;
- relationship analysis.

Validated engineering foundation:
- M4 graph fragments converged into one durable M11 graph contract: PASS;
- migration 010 graph persistence: PASS;
- deterministic node and logical edge identity: PASS;
- explicit actor-reference and canonical event projection: PASS;
- M8 claim/finding traceability projection: PASS;
- evidence-backed relationship lifecycle: PASS;
- SUPPORTS/CONTRADICTS/CONTEXT evidence roles: PASS;
- ACTIVE/UPDATED/INVALIDATED/RESOLVED relationship states: PASS;
- preserved material relationship history: PASS;
- temporal validity and snapshot queries: PASS;
- bounded cycle-safe causal/influence traversal: PASS;
- advanced explainable IntelligenceQuery facade: PASS;
- M8/M10/M11 confidence and source-independence isolation: PASS;
- project-local runtime storage: PASS;
- external graph provider dependency: NONE.

M11 final regression:
- GitHub Actions run 32973378757;
- 118 passed in 4.24s.

Phase 8 engineering baseline status:
BASELINE_VALIDATED

Phase 8 completion does not approve hosted graph providers, graph-generated verification promotion, shared runtime storage or production/live OPERATIONAL status.

## Phase 9 - Advanced Forecasting

Develop:
- scenario models;
- calibration;
- long-term forecasting.

Current preparation scope:
- audit the existing forecasting, calibration, historical-validation and adaptive-learning baselines;
- define the M12 delta without duplicating existing forecasting modules;
- preserve evidence, temporal and graph provenance in forecast inputs;
- preserve PROJECT_LOCAL_ONLY runtime storage.

Current engineering activity:
- M12 Advanced Forecasting preparation and delta audit.

## Phase 10 - Full Reporting Environment

Support:
- strategic alerts;
- global briefs;
- regional briefs;
- event dossiers;
- forecast reports.

## Phase 11 - Global Operational Coverage

Implement measurable coverage contracts and coverage confidence.

## Current implementation checkpoint

- Product Concept: APPROVED
- Roadmap: APPROVED
- Engineering implementation: BASELINE_VALIDATED through M11
- M5 full test cycle: PASS - 57 tests, GitHub Actions run 32953343877
- M6 controlled pilot baseline: PASS - 62 tests, GitHub Actions run 32961649091
- M7 deterministic regression: PASS - 68 tests, GitHub Actions run 32962379499
- M7 live source smoke: PASS - GitHub Actions run 32962576874
- M8 deterministic regression: PASS - 73 tests, GitHub Actions run 32963096313
- M8 live end-to-end controlled pilot: PASS - GitHub Actions run 32963354135
- M9 hardened regression: PASS - 82 tests, GitHub Actions run 32965387054
- M10 multi-region/language regression: PASS - 88 tests, GitHub Actions run 32966128001
- M11 advanced geopolitical graph regression: PASS - 118 tests, GitHub Actions run 32973378757
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph: BASELINE_VALIDATED
- Shared Infrastructure Architecture Review: COMPLETE; HYBRID adopted
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Controlled-pilot external integrations: 2
- External graph providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 9 Advanced Forecasting preparation
- Next engineering work package: M12 Advanced Forecasting preparation and delta audit
- Production/live operational status: NOT_OPERATIONAL
