# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 1.4
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring -> Controlled Pilot Coverage

## Core Components

- Source Registry
- Ingestion Layer
- Event Processing Layer
- Verification Engine
- Relationship Analysis Layer
- Forecasting Layer
- Reporting Layer
- Operational Monitoring Runtime
- Operational Intelligence Output
- Controlled Pilot Source Adapter
- Pilot Coverage Reporting

## Implemented and Validated Baseline

The repository contains validated baselines for:

- persistence and domain foundations;
- evidence and verification;
- event intelligence and correlation;
- forecasting and adaptive-learning components;
- knowledge graph and relationship analysis;
- graph persistence baseline;
- causal and temporal graph analysis;
- intelligence query baseline;
- project-local monitoring watch and run persistence;
- controlled monitoring cycle orchestration;
- failure isolation, retry metadata and interrupted-run recovery;
- ranked operational findings with evidence references and explanation requirements;
- project-local JSONL controlled source ingestion;
- source-class enforcement and source/raw-item provenance persistence;
- persistent pilot coverage reports with explicit gaps and coverage confidence;
- deterministic controlled-pilot execution across cadence windows and restart.

These components represent a project-local validated baseline and must not be interpreted as live production or global operational maturity.

## Runtime and Shared Infrastructure Boundary

The Shared Infrastructure Architecture Review selected HYBRID architecture.

The approved ADR requires:

- project-specific domain logic and canonical stores remain local;
- runtime storage remains PROJECT_LOCAL_ONLY;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- any future shared runtime storage requires a new explicit architecture approval.

M6 extends the same boundary to controlled source inputs: pilot JSONL inputs must remain under the project-local data/pilot_sources path.

## External Integration Boundary

The M6 controlled pilot baseline intentionally uses deterministic project-local source fixtures.

No production external provider is enabled by this architecture state.

A live public-source pilot requires an explicit integration record defining provider, data contract, authentication mode, Source of Truth, provenance, fallback and failure isolation before activation.

## Validation State

M5 full test cycle: PASS.

Evidence:
- implementation commit: 1bd258e17cd99b94aa2c751f2fb9f10459f4457c
- GitHub Actions run: 32953343877
- result: 57 passed in 1.05s

M6 controlled pilot baseline: PASS.

Evidence:
- validation checkpoint: c1ef35841e85fdc1d3b1c2c02cd88ef8ae379af2
- GitHub Actions run: 32961649091
- result: 62 passed in 0.91s

## Current State

- Implementation: BASELINE_VALIDATED through M6
- M4 acceptance: PASS
- M5 full test cycle: PASS
- M6 controlled pilot baseline: PASS
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Production external integrations: NONE_APPROVED
- Live public-source pilot: READY_FOR_INTEGRATION_REVIEW
- Production/live operational maturity: NOT_OPERATIONAL
