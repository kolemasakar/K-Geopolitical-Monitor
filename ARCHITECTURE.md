# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 2.0
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Live/Controlled Acquisition -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring -> Coverage -> Strategic Alerts -> Region/Language Scope -> Advanced Geopolitical Graph -> Advanced Forecasting -> Full Reporting Environment

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
- Full Reporting Environment - next baseline

## Implemented and Validated Baseline

The repository contains validated baselines for:

- persistence and domain foundations;
- evidence and verification;
- event intelligence and correlation;
- forecasting and adaptive-learning components;
- project-local operational monitoring, failure isolation, retry and recovery;
- ranked operational findings with evidence references and explanations;
- controlled and live read-only source acquisition;
- provenance, collection audit and source failure isolation;
- origin-based M8 verification independence;
- strategic alert policies, lifecycle and priority/cadence separation;
- watch-scoped region/language requirements and coverage reports;
- translation-attribution isolation from evidence confidence and source independence;
- durable advanced geopolitical graph persistence;
- deterministic graph node and logical edge identity;
- explicit canonical actor/event/claim/finding graph projections;
- evidence-backed relationship lifecycle and preserved material history;
- temporal validity intervals and historical snapshots;
- bounded cycle-safe causal/influence traversal;
- advanced explainable graph query facade;
- durable forecast, forecast-version and scenario-version persistence;
- typed immutable forecast provenance inputs;
- immutable scenario update lifecycle with raw/calibrated probability separation;
- durable outcome resolution and exact-version forecast evaluation;
- Brier/calibration metrics with PARTIAL/AMBIGUOUS non-scoring;
- reproducible calibration history with explicit minimum sample contract;
- horizon/scenario performance summaries;
- advanced read-only forecast query/explanation facade;
- cross-layer M8/M10/M11/M12 confidence and source-independence isolation.

These components represent a controlled project-local validated baseline and must not be interpreted as global production maturity.

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
- alert priority, region/language attribution, graph intelligence and forecast outputs are downstream metadata/analysis and must not increase evidence confidence or independent-origin count.

## Advanced Geopolitical Graph Boundary

M11 extends and converges the M4 graph baseline rather than creating a second graph subsystem.

Graph model:

- graph nodes carry deterministic canonical references;
- graph edges carry deterministic logical identities, relation class, graph-local confidence, lifecycle status, validity and observation timestamps;
- edge evidence is stored separately from logical relation identity;
- material relationship changes preserve immutable history;
- current-state queries exclude invalidated/resolved relationships while historical queries retain them;
- causal/influence traversal is bounded, cycle-safe and deterministic;
- advanced queries expose graph IDs, canonical references and evidence references.

Canonical truth boundary:

- canonical project objects remain the Source of Truth;
- actor references are explicit inputs rather than a new actor truth store;
- canonical events remain owned by the events table;
- M8 claims and findings are traceability projections;
- graph inference is not source evidence;
- graph confidence does not modify M8 confidence or independent-origin count;
- graph operations do not automatically assign VERIFIED status;
- no external graph service is required or approved by the baseline.

## Advanced Forecasting Boundary

M12 extends existing forecasting, calibration, historical-validation and adaptive-learning components rather than creating a parallel forecasting stack.

Forecast model:

- forecast identity is deterministic by target, horizon and evaluation deadline;
- forecast versions and scenario versions are immutable historical records;
- raw probability, calibrated probability and scenario confidence are distinct values;
- typed input kinds distinguish source evidence, canonical events, graph relationships, operational findings and analyst assumptions;
- durable input references fail closed when the referenced project object does not exist;
- graph relationships are analytical inputs and never become independent source evidence;
- outcome resolution is evidence-backed and separate from forecast creation;
- PARTIAL and AMBIGUOUS outcomes remain unscored rather than receiving fabricated binary values;
- calibration history is reproducible from exact evaluation-ID cohorts and method/version metadata;
- baseline calibration history measures performance and does not rewrite persisted scenario probabilities;
- advanced forecast queries are read-only and expose version, provenance, outcome, evaluation and calibration history.

Canonical truth boundary:

- forecasts are analytical outputs, not facts;
- forecast probability and scenario confidence are not evidence confidence;
- forecasting cannot increase M8 independent-origin count or verification status;
- forecasting cannot mutate M11 graph state;
- no forecast automatically becomes a canonical event or verified claim;
- no external forecasting provider is required or approved by the baseline.

## Phase 10 Boundary

Full Reporting Environment must assemble existing validated outputs rather than create new truth stores.

Phase 10 must preserve:

- evidence and source provenance in strategic, global, regional, event and forecast reports;
- explicit distinction between observed facts, verification state, graph inference and forecast scenarios;
- report reproducibility from persisted project-local inputs;
- deterministic/project-local baseline execution;
- no verification or confidence inflation caused by report presentation;
- PROJECT_LOCAL_ONLY runtime storage.

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

## Current State

- Implementation: BASELINE_VALIDATED through M12
- ROADMAP Phase 5: BASELINE_VALIDATED
- ROADMAP Phase 6: BASELINE_VALIDATED
- ROADMAP Phase 7: BASELINE_VALIDATED
- ROADMAP Phase 8: BASELINE_VALIDATED
- ROADMAP Phase 9: BASELINE_VALIDATED
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled-pilot live integrations: VALIDATED
- Strategic alert baseline: VALIDATED
- Region/language coverage baseline: VALIDATED
- Advanced geopolitical graph baseline: VALIDATED
- Advanced forecasting baseline: VALIDATED
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 10 Full Reporting Environment preparation
- Next engineering work package: M13 Full Reporting Environment delta audit and implementation plan
- Production/live operational maturity: NOT_OPERATIONAL
