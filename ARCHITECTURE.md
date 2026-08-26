# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 1.5
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Live/Controlled Acquisition -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring -> Coverage

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

## Implemented and Validated Baseline

The repository contains validated baselines for:

- persistence and domain foundations;
- evidence and verification;
- event intelligence and correlation;
- forecasting and adaptive-learning components;
- knowledge graph and relationship analysis;
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
- deterministic source identities and repeated-collection provenance.

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

M7 adds two integrations approved only for controlled pilot use:

- Consilium press-release RSS: Official sources;
- GDELT DOC 2.0 API: Structured data discovery metadata.

Both are read-only and require no credentials in the current controlled pilot.

GDELT metadata is discovery/index evidence only. Original publishers or primary sources remain the factual Source of Truth for linked content.

Live network checks are isolated from deterministic CI in a manual smoke workflow.

## Validation State

M5 full test cycle: PASS - 57 tests, run 32953343877.
M6 controlled pilot baseline: PASS - 62 tests, run 32961649091.
M7 deterministic regression: PASS - 68 tests, run 32962379499.
M7 live-source smoke: PASS - run 32962576874.

## Current State

- Implementation: BASELINE_VALIDATED through M7
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled-pilot live integrations: VALIDATED
- Production/global external integrations: NONE_APPROVED
- ROADMAP Phase 5: ACTIVE
- Next engineering milestone: M8 Live End-to-End Controlled Pilot Processing
- Production/live operational maturity: NOT_OPERATIONAL
