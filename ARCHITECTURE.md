# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 1.3
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring

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
- ranked operational findings with evidence references and explanation requirements.

These components represent a project-local validated baseline and must not be interpreted as live production or global operational maturity.

## M5 Infrastructure Boundary

The Shared Infrastructure Architecture Review selected HYBRID architecture.

The approved ADR requires:

- project-specific domain logic and canonical stores remain local;
- M5 runtime storage remains PROJECT_LOCAL_ONLY;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- any future shared runtime storage requires a new explicit architecture approval even after the successful M5 test cycle.

## Validation State

M5 full test cycle: PASS.

Evidence:
- implementation commit: 1bd258e17cd99b94aa2c751f2fb9f10459f4457c
- GitHub Actions run: 32953343877
- result: 57 passed in 1.05s

## Current State

- Implementation: BASELINE_VALIDATED through M5
- M4 acceptance: PASS
- M5 readiness: PASS
- M5 full test cycle: PASS
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled pilot readiness: READY
- Production/live operational maturity: NOT_OPERATIONAL
