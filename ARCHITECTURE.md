# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 2.1
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Live/Controlled Acquisition -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring -> Coverage -> Strategic Alerts -> Region/Language Scope -> Advanced Geopolitical Graph -> Advanced Forecasting -> Full Reporting Environment -> Global Operational Coverage

## Core Components

- Source Registry
- Controlled Pilot Source Adapter
- Live Public-Source Adapters
- Source Collection Audit
- Ingestion Layer
- Event Processing Layer
- Verification Engine
- Relationship Analysis Layer
- Forecasting Layer
- Reporting Layer
- Operational Monitoring Runtime
- Operational Intelligence Output
- Pilot Coverage Reporting
- Live End-to-End Analysis
- Strategic Alert Layer
- Region/Language Coverage Layer
- Advanced Geopolitical Graph
- Advanced Forecasting
- Full Reporting Environment
- Global Operational Coverage - next baseline preparation

## Implemented and Validated Baseline

Validated foundations include:

- persistence, evidence, verification and event intelligence;
- project-local operational monitoring, retry/recovery and ranked findings;
- controlled/live read-only acquisition with provenance and source-failure isolation;
- original-origin M8 evidence independence;
- strategic alert policies/lifecycle and priority/cadence separation;
- watch-scoped region/language attribution and coverage reporting;
- translation-attribution isolation from evidence confidence/source independence;
- durable advanced graph identity, projection, lifecycle, history, temporal/causal traversal and explainable queries;
- durable advanced forecasting identity, immutable scenario versions, typed provenance, outcome evaluation, calibration history and explainable queries;
- durable immutable report snapshots, sections and typed references;
- one common report assembler for strategic/global/regional/event/storyline/forecast/outlook reports;
- deterministic structured and Markdown report rendering;
- report rendering reproducibility after restart;
- cross-layer M8/M10/M11/M12 truth-state isolation through reporting.

These components represent a controlled project-local validated engineering baseline and must not be interpreted as global production maturity.

## Runtime and Shared Infrastructure Boundary

The approved Shared Infrastructure ADR requires:

- HYBRID architecture;
- project-specific domain logic and canonical stores remain local;
- runtime storage remains PROJECT_LOCAL_ONLY;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- any future shared runtime storage requires a new explicit architecture approval.

## External Integration Boundary

Controlled-pilot integrations:

- Consilium press-release RSS: Official sources;
- GDELT DOC 2.0 API: Structured data discovery metadata.

Both are read-only and require no credentials in the current controlled pilot.

GDELT metadata is discovery/index evidence only. Original publishers or primary sources remain the factual Source of Truth for linked content.

Live network checks remain isolated from deterministic CI in manual smoke workflows.

External-source availability is not assumed. A collection may be COMPLETED, PARTIAL or FAILED, and every source failure must remain visible in the collection audit.

## Verification Boundary

- adapter identity does not establish evidence independence;
- original publisher/origin host is the baseline independence unit;
- a single independent origin remains DETECTED;
- at least two distinct original origins are required for PARTLY_VERIFIED;
- same-origin duplicate observations must not increase verification status;
- VERIFIED is never assigned automatically by the current baseline;
- alert priority, region/language attribution, graph intelligence, forecast outputs and report presentation must not increase evidence confidence or independent-origin count.

## Advanced Geopolitical Graph Boundary

M11 converges M4 graph fragments into one durable project-local graph contract.

- canonical project objects remain Source of Truth;
- graph inference is not source evidence;
- graph confidence does not modify M8 confidence or independent-origin count;
- graph operations do not automatically assign VERIFIED;
- no external graph service is required or approved.

## Advanced Forecasting Boundary

M12 extends existing forecasting/calibration/history components rather than creating a parallel stack.

- forecast versions and scenario versions are immutable;
- raw probability, calibrated probability and scenario confidence are distinct;
- source evidence, canonical events, graph relationships, findings and analyst assumptions remain typed separately;
- forecasts are analytical outputs, not facts;
- forecasting cannot increase M8 independent-origin count/verification status or mutate M11 graph state;
- no external forecasting provider is required or approved.

## Full Reporting Environment Boundary

M13 adds one canonical presentation subsystem over existing validated state.

Durable reporting model:

- `report_snapshots` stores immutable report identity/metadata;
- `report_sections` stores ordered typed presentation sections;
- `report_references` stores typed upstream traceability;
- all approved report types use this same model;
- Storyline Report is report-scoped composition and does not create a canonical storyline table.

Reporting semantics:

- observed facts, verification state, analytical context, graph inference, forecast scenarios, analyst assumptions and coverage metadata remain explicitly distinguishable;
- source evidence remains distinct from graph inference;
- forecast probabilities/confidence remain forecast analytics;
- incomplete regional coverage remains visible;
- report assembly/ranking/rendering cannot modify upstream truth;
- deterministic structured and Markdown representations are rendered from the same persisted snapshot;
- restart rendering must be identical;
- runtime report database resolution uses the existing project-local storage policy;
- no external publishing/delivery provider is required or approved.

## Phase 11 Boundary

Global Operational Coverage is the next preparation baseline.

Phase 11 must:

- extend measurable coverage semantics rather than claim coverage from report volume;
- preserve M8 original-origin evidence independence;
- keep coverage confidence separate from factual verification confidence;
- make missing/failed/unknown coverage explicit;
- preserve PROJECT_LOCAL_ONLY runtime storage unless a new architecture decision explicitly changes it;
- not declare global operational maturity before dedicated acceptance gates pass.

## Validation State

M5 full test cycle: PASS - 57 tests, run 32953343877.
M6 controlled pilot baseline: PASS - 62 tests, run 32961649091.
M7 deterministic regression: PASS - 68 tests, run 32962379499.
M7 live-source smoke: PASS - run 32962576874.
M8 deterministic regression: PASS - 73 tests, run 32963096313.
M8 live end-to-end controlled pilot: PASS - run 32963354135.
M9 hardened regression: PASS - 82 tests, run 32965387054.
M10 multi-region/language regression: PASS - 88 tests, run 32966128001.
M11 advanced geopolitical graph final regression: PASS - 118 tests, run 32973378757.
M12 advanced forecasting final regression: PASS - 154 tests, run 32980859938.
M13 full reporting environment final implementation regression: PASS - 199 tests, run 32993269910.

## Current State

- Implementation: BASELINE_VALIDATED through M13
- ROADMAP Phase 5: BASELINE_VALIDATED
- ROADMAP Phase 6: BASELINE_VALIDATED
- ROADMAP Phase 7: BASELINE_VALIDATED
- ROADMAP Phase 8: BASELINE_VALIDATED
- ROADMAP Phase 9: BASELINE_VALIDATED
- ROADMAP Phase 10: BASELINE_VALIDATED
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled-pilot live integrations: VALIDATED
- Strategic alert baseline: VALIDATED
- Region/language coverage baseline: VALIDATED
- Advanced geopolitical graph baseline: VALIDATED
- Advanced forecasting baseline: VALIDATED
- Full reporting environment baseline: VALIDATED
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 11 Global Operational Coverage preparation
- Next engineering activity: Phase 11 delta audit and implementation planning
- Production/live operational maturity: NOT_OPERATIONAL
