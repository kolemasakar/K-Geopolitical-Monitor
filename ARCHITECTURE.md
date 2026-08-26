# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 1.2
Status: APPROVED

## Purpose

Define the initial system architecture boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Ingestion -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting

## Core Components

- Source Registry
- Ingestion Layer
- Event Processing Layer
- Verification Engine
- Relationship Analysis Layer
- Forecasting Layer
- Reporting Layer

## Implemented Baseline

The repository contains implementation baselines for:

- persistence and domain foundations;
- evidence and verification;
- event intelligence and correlation;
- forecasting and adaptive-learning components;
- knowledge graph and relationship analysis;
- graph persistence baseline;
- causal and temporal graph analysis;
- intelligence query baseline.

These components are baseline implementations and must not be interpreted as production or operational maturity.

## M5 Infrastructure Boundary

The Shared Infrastructure Architecture Review is complete and recommends HYBRID architecture:

- project-specific domain logic and canonical stores remain local;
- narrow common contracts may be standardized first;
- shared component extraction requires proven multi-project use and compatibility tests;
- implicit mixed storage and direct cross-project canonical-store mutation are prohibited.

The corresponding ADR remains PROPOSED. Cross-project extraction and shared runtime storage remain blocked until explicit architecture approval.

## Current State

- Implementation: BASELINE_IMPLEMENTED through M4
- M4 acceptance: PASS
- Full regression CI: PASS
- M5 readiness: PASS
- M5 implementation: READY_TO_START; NOT_STARTED
- Operational maturity: NOT_OPERATIONAL
