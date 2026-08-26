# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 2.2
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
- Global Operational Coverage

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
- durable operational coverage contracts, requirements, immutable snapshots and per-requirement results;
- per-source collection attempts and adapter/item identity integrity;
- source-class, source-availability, region/language and freshness convergence;
- historical coverage queries and coverage-aware reporting through the existing M13 report store;
- cross-layer M8/M10/M11/M12/M13 truth-state isolation through Phase 11.

These components represent a controlled project-local validated engineering baseline and must not be interpreted as complete global production maturity.

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

External-source availability is not assumed. A collection may be COMPLETED, PARTIAL or FAILED, and every source failure must remain visible in collection audit/attempt state.

## Verification Boundary

- adapter identity does not establish evidence independence;
- original publisher/origin host is the baseline independence unit;
- a single independent origin remains DETECTED;
- at least two distinct original origins are required for PARTLY_VERIFIED;
- same-origin duplicate observations must not increase verification status;
- VERIFIED is never assigned automatically by the current baseline;
- alert priority, region/language attribution, graph intelligence, forecast outputs, coverage metrics and report presentation must not increase evidence confidence or independent-origin count.

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

M13 provides one canonical presentation subsystem over existing validated state.
- `report_snapshots` stores immutable report identity/metadata;
- `report_sections` stores ordered typed presentation sections;
- `report_references` stores typed upstream traceability;
- all approved report types use this same model;
- Storyline Report is report-scoped composition and does not create a canonical storyline table;
- observed facts, verification state, analytical context, graph inference, forecast scenarios, assumptions and coverage metadata remain distinguishable;
- reporting cannot modify upstream truth;
- deterministic structured and Markdown representations are rendered from the same persisted snapshot;
- runtime report DB uses the existing project-local storage policy;
- no external publishing/delivery provider is required or approved.

## Global Operational Coverage Boundary

Phase 11 adds one coverage-measurement layer over existing M6/M7/M10 state and M13 presentation.

Durable coverage model:
- `operational_coverage_contracts` declares explicit scope/window/freshness identity;
- `operational_coverage_requirements` stores typed required units;
- `operational_coverage_snapshots` stores immutable aggregate assessments;
- `operational_coverage_requirement_results` explains every required unit;
- `source_collection_attempts` preserves per-source acquisition availability state.

Baseline measurable dimensions:
- SOURCE_CLASS;
- SOURCE_ID / SOURCE_AVAILABILITY;
- REGION_LANGUAGE;
- FRESHNESS.

Baseline statuses:
- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE;
- UNKNOWN;
- UNMEASURED.

Coverage semantics:
- coverage_ratio is satisfied required units / required units;
- coverage_confidence is known assessment states / required units;
- UNKNOWN and UNMEASURED reduce coverage confidence;
- coverage confidence is not factual verification confidence;
- source count, graph degree, forecast count and report count cannot inflate coverage;
- translation attribution does not create source independence;
- GLOBAL is an explicit scope key, not a universal-completeness claim;
- historical coverage state remains immutable and queryable;
- Phase 11 coverage reports use the existing M13 report store;
- no external coverage provider is required or approved.

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
Phase 11 global operational coverage final implementation regression: PASS - 226 tests, run 33000478908.

## Current State

- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- ROADMAP Phase 5: BASELINE_VALIDATED
- ROADMAP Phase 6: BASELINE_VALIDATED
- ROADMAP Phase 7: BASELINE_VALIDATED
- ROADMAP Phase 8: BASELINE_VALIDATED
- ROADMAP Phase 9: BASELINE_VALIDATED
- ROADMAP Phase 10: BASELINE_VALIDATED
- ROADMAP Phase 11: BASELINE_VALIDATED
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled-pilot live integrations: VALIDATED
- Strategic alert baseline: VALIDATED
- Region/language coverage baseline: VALIDATED
- Advanced geopolitical graph baseline: VALIDATED
- Advanced forecasting baseline: VALIDATED
- Full reporting environment baseline: VALIDATED
- Global operational coverage measurement baseline: VALIDATED
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External coverage providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 11 completed and BASELINE_VALIDATED
- Next roadmap phase: NONE_APPROVED; roadmap extension required
- Production/live operational maturity: NOT_OPERATIONAL
