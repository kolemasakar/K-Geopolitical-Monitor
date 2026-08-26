# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 1.8
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Live/Controlled Acquisition -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring -> Coverage -> Strategic Alerts -> Region/Language Scope -> Advanced Geopolitical Graph

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
- Advanced Geopolitical Graph - next baseline

## Implemented and Validated Baseline

The repository contains validated baselines for:

- persistence and domain foundations;
- evidence and verification;
- event intelligence and correlation;
- forecasting and adaptive-learning components;
- M4 knowledge graph and relationship analysis;
- causal and temporal graph analysis;
- intelligence query baseline;
- project-local monitoring watch and run persistence;
- controlled monitoring cycle orchestration;
- failure isolation, retry metadata and interrupted-run recovery;
- ranked operational findings with evidence references and explanation requirements;
- deterministic project-local controlled-source ingestion;
- source-class enforcement and source/raw-item provenance persistence;
- persistent pilot coverage reports;
- live read-only Consilium RSS acquisition;
- live read-only GDELT DOC 2.0 discovery acquisition;
- per-source live collection failure isolation and collection audit;
- deterministic source identities and repeated-collection provenance;
- collection-scoped live analysis;
- deterministic claim grouping;
- original-origin evidence independence;
- DETECTED/PARTLY_VERIFIED M8 baseline status handling;
- project-local live operational finding projection with claim/raw-item/origin traceability;
- real-network PARTIAL collection continuation under external-source failure;
- persisted strategic-alert policies;
- evidence-aware strategic-alert triggers;
- stable alert deduplication and cross-cycle updates;
- OPEN/UPDATED/INVALIDATED/RESOLVED strategic-alert state;
- persistent strategic-alert event history;
- alert restart persistence;
- priority ordering for due watches without cadence bypass;
- canonical project-local region and language registries;
- watch-scoped region/language requirements;
- raw-item region/language attribution;
- region/language coverage and gap reports;
- translation-attribution isolation from evidence confidence and source independence.

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

M8 establishes the following baseline rules:

- adapter identity does not establish evidence independence;
- original publisher/origin host is the baseline independence unit;
- a single independent origin remains DETECTED;
- at least two distinct original origins are required for PARTLY_VERIFIED;
- same-origin duplicate observations must not increase verification status;
- VERIFIED is never assigned automatically by the M8 baseline.

M9 and M10 preserve those rules. Alert priority and region/language attribution are operational/coverage metadata only and must not change evidence confidence or verification status.

## Strategic Alert Boundary

M9 establishes:

- alerts derive only from persisted operational findings;
- alert thresholds may use finding importance, confidence and verification rank;
- stable normalized-title deduplication prevents repeated-cycle duplicates;
- later same-title findings update an existing alert;
- invalidation and resolution preserve history;
- invalidated/resolved alerts do not silently reopen;
- CRITICAL priority does not bypass cadence;
- no external notification provider is enabled by the engineering baseline.

## Region and Language Boundary

M10 establishes:

- explicit normalized region and language registries;
- watch-scoped required region/language pairs;
- watch-scoped raw-item attribution;
- explicit missing-scope coverage reports;
- translations and region/language tags do not create additional independent origins;
- translations and region/language tags do not modify M8 confidence or verification status;
- cross-watch attribution leakage is blocked.

## Phase 8 Boundary

Advanced Geopolitical Graph must extend the existing M4 graph baseline rather than create a second graph implementation.

Phase 8 may integrate:

- actor/entity graph views;
- event graph views;
- operational findings and strategic alerts as graph-linked intelligence artifacts;
- region/language scope as graph metadata where appropriate;
- temporal and causal relationship queries over validated graph facts.

Phase 8 must preserve:

- provenance for graph facts and derived links;
- M8 source-independence semantics;
- temporal semantics;
- project-local canonical storage;
- no confidence inflation from graph degree, region count or language count alone.

## Validation State

M5 full test cycle: PASS - 57 tests, run 32953343877.
M6 controlled pilot baseline: PASS - 62 tests, run 32961649091.
M7 deterministic regression: PASS - 68 tests, run 32962379499.
M7 live-source smoke: PASS - run 32962576874.
M8 deterministic regression: PASS - 73 tests, run 32963096313.
M8 live end-to-end controlled pilot: PASS - run 32963354135.
M9 hardened regression: PASS - 82 tests, run 32965387054.
M10 multi-region/language regression: PASS - 88 tests, run 32966128001.

## Current State

- Implementation: BASELINE_VALIDATED through M10
- ROADMAP Phase 5: BASELINE_VALIDATED
- ROADMAP Phase 6: BASELINE_VALIDATED
- ROADMAP Phase 7: BASELINE_VALIDATED
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled-pilot live integrations: VALIDATED
- Strategic alert baseline: VALIDATED
- Region/language coverage baseline: VALIDATED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 8 Advanced Geopolitical Graph preparation
- Next engineering milestone: M11 Advanced Geopolitical Graph baseline
- Production/live operational maturity: NOT_OPERATIONAL
