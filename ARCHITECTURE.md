# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 1.9
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Live/Controlled Acquisition -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring -> Coverage -> Strategic Alerts -> Region/Language Scope -> Advanced Geopolitical Graph -> Advanced Forecasting

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
- Advanced Forecasting - next baseline

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
- M4 compatibility projection;
- explicit canonical actor/event/claim/finding graph projections;
- evidence-backed relationship lifecycle and preserved material history;
- temporal validity intervals and historical snapshots;
- bounded cycle-safe causal/influence traversal;
- advanced explainable graph query facade;
- cross-layer M8/M10/M11 confidence and source-independence isolation.

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
- alert priority, region/language attribution and graph intelligence are downstream metadata/analysis and must not increase evidence confidence or independent-origin count.

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

## Phase 9 Boundary

Advanced Forecasting must extend existing forecasting, calibration, historical-validation and adaptive-learning components rather than create a parallel forecasting stack.

Phase 9 must preserve:

- explicit evidence and graph provenance for forecast inputs;
- distinction between observed facts, graph relationships, assumptions and forecast outputs;
- historical calibration and measurable forecast performance;
- deterministic/project-local baseline execution;
- no source-independence or verification inflation from forecast confidence;
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

## Current State

- Implementation: BASELINE_VALIDATED through M11
- ROADMAP Phase 5: BASELINE_VALIDATED
- ROADMAP Phase 6: BASELINE_VALIDATED
- ROADMAP Phase 7: BASELINE_VALIDATED
- ROADMAP Phase 8: BASELINE_VALIDATED
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled-pilot live integrations: VALIDATED
- Strategic alert baseline: VALIDATED
- Region/language coverage baseline: VALIDATED
- Advanced geopolitical graph baseline: VALIDATED
- External graph providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 9 Advanced Forecasting preparation
- Next engineering work package: M12 Advanced Forecasting preparation and delta audit
- Production/live operational maturity: NOT_OPERATIONAL
