# ROADMAP

Version: 1.4
Status: APPROVED
Project: K-Geopolitical Monitor

## Development principle

Minimal Functional Core First.

The project is developed through validation stages. Implementation does not equal validation.

Implementation milestone labels M0-M6 are engineering work packages and are not identical to ROADMAP phase numbers.

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
- project-local source adapter and provenance: PASS;
- coverage reporting and explicit gaps: PASS.

Next Phase 5 activity:
- live public-source controlled pilot through explicit integration records and source-specific validation.

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
- Engineering implementation: BASELINE_VALIDATED through M6
- M4 validation: PASS
- M5 engineering work package: BASELINE_VALIDATED
- M5 full test cycle: PASS - 57 tests, GitHub Actions run 32953343877
- M6 Controlled Pilot Monitoring baseline: PASS - 62 tests, GitHub Actions run 32961649091
- Shared Infrastructure Architecture Review: COMPLETE; HYBRID adopted
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Production external integrations: NONE_APPROVED
- Current roadmap activity: Phase 5 Controlled Pilot Monitoring
- Next gate: live public-source controlled pilot integration validation
- Production/live operational status: NOT_OPERATIONAL
