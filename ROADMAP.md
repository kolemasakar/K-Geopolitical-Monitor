# ROADMAP

Version: 1.5
Status: APPROVED
Project: K-Geopolitical Monitor

## Development principle

Minimal Functional Core First.

The project is developed through validation stages. Implementation does not equal validation.

Implementation milestone labels M0-M8 are engineering work packages and are not identical to ROADMAP phase numbers.

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
- Consilium RSS live smoke: PASS;
- GDELT DOC 2.0 live smoke: PASS;
- source provenance and collection audit: PASS.

Current Phase 5 activity:
- M8 live end-to-end controlled pilot processing from approved live-source collection through verification/analysis and operational output.

Phase 5 is not complete until the live end-to-end processing gate passes.

## Phase 6 - Strategic Alerts and Continuous Monitoring

Add:
- trigger detection;
- invalidation detection;
- priority watches.

## Phase 7 - Multi-Region Expansion

Expand regional and language coverage.

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
- Engineering implementation: BASELINE_VALIDATED through M7
- M5 full test cycle: PASS - 57 tests, GitHub Actions run 32953343877
- M6 controlled pilot baseline: PASS - 62 tests, GitHub Actions run 32961649091
- M7 deterministic regression: PASS - 68 tests, GitHub Actions run 32962379499
- M7 live source smoke: PASS - GitHub Actions run 32962576874
- Shared Infrastructure Architecture Review: COMPLETE; HYBRID adopted
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Controlled-pilot external integrations: 2
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 5 Controlled Pilot Monitoring
- Next engineering gate: M8 Live End-to-End Controlled Pilot Processing
- Production/live operational status: NOT_OPERATIONAL
