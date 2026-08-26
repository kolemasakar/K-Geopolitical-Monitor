# ROADMAP

Version: 1.7
Status: APPROVED
Project: K-Geopolitical Monitor

## Development principle

Minimal Functional Core First.

The project is developed through validation stages. Implementation does not equal validation.

Implementation milestone labels M0-M10 are engineering work packages and are not identical to ROADMAP phase numbers.

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

Current preparation scope:
- define canonical region identifiers and region groups;
- define language coverage metadata independent from evidence truth;
- bind monitoring watches to explicit region/language scope;
- measure region/language coverage and gaps;
- ensure region or language priority does not inflate verification confidence;
- preserve original-source provenance across translated or indexed observations;
- preserve PROJECT_LOCAL_ONLY runtime storage.

Current engineering activity:
- M10 Multi-Region and Language Coverage baseline preparation.

## Phase 8 - Advanced Geopolitical Graph

Develop:
- actor graph;
- event graph;
- relationship analysis.

## Phase 9 - Advanced Forecasting

Develop:
- scenario models;
- calibration;
- long-term forecasting.

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
- Engineering implementation: BASELINE_VALIDATED through M9
- M5 full test cycle: PASS - 57 tests, GitHub Actions run 32953343877
- M6 controlled pilot baseline: PASS - 62 tests, GitHub Actions run 32961649091
- M7 deterministic regression: PASS - 68 tests, GitHub Actions run 32962379499
- M7 live source smoke: PASS - GitHub Actions run 32962576874
- M8 deterministic regression: PASS - 73 tests, GitHub Actions run 32963096313
- M8 live end-to-end controlled pilot: PASS - GitHub Actions run 32963354135
- M9 hardened regression: PASS - 82 tests, GitHub Actions run 32965387054
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- Shared Infrastructure Architecture Review: COMPLETE; HYBRID adopted
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Controlled-pilot external integrations: 2
- External notification providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 7 Multi-Region Expansion preparation
- Next engineering gate: M10 Multi-Region and Language Coverage baseline
- Production/live operational status: NOT_OPERATIONAL
