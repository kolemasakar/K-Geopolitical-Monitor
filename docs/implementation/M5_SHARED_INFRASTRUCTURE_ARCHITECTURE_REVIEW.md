# M5 Shared Infrastructure Architecture Review

Status: REVIEW_COMPLETE
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Purpose

Evaluate whether M5 should use independent repositories, a dedicated Shared Infrastructure repository, or a hybrid architecture.

## Repositories Reviewed

- kolemasakar/K-Geopolitical-Monitor
- kolemasakar/K_Research_Critic
- kolemasakar/K-Trader
- kolemasakar/VoiceBridge
- kolemasakar/AI_general

A separate AI-TOOLKIT repository was not found during the review and is therefore not treated as a verified architecture dependency.

## Current Overlap

### K-Geopolitical Monitor

Owns geopolitical domain semantics and current baselines for:

- sources, raw items, events, claims and evidence;
- verification and confidence;
- forecasting and adaptive learning;
- knowledge graph, relationships, causal and temporal analysis;
- intelligence queries.

### K_Research_Critic

Contains mature Pydantic contracts for tasks, workflow execution, claims, sources, confidence, telemetry and review artifacts.

The models overlap conceptually with Source, Claim, Confidence and provenance concepts, but are tightly coupled to KRC task/workflow identifiers, CriticProfile governance and research execution semantics.

Conclusion: do not import the complete KRC domain model into K-Geopolitical Monitor.

### K-Trader

Contains its own runtime, provider, storage, evidence and market-analysis layers.

Its evidence implementation is market-specific, including VSA and trap analysis.

Conclusion: trading evidence and market models are domain-specific and must remain local to K-Trader.

### VoiceBridge

Provides a product-specific speech/media runtime with its own source tree and CI structure.

No verified requirement was found to make VoiceBridge domain objects canonical for K-Geopolitical Monitor.

Conclusion: consume VoiceBridge capabilities through explicit integration contracts when required; do not share its internal storage or domain state implicitly.

### AI_general

Currently provides the canonical PROJECT_FILE_STANDARD documentation.

Conclusion: AI_general is a governance/standards source, not a verified runtime shared-library repository.

## Architecture Options

### Option 1 - Fully Independent Repositories

Advantages:

- strongest failure isolation;
- clear ownership;
- minimal cross-project coupling.

Disadvantages:

- repeated infrastructure patterns;
- risk of contract drift;
- duplicated provider, telemetry and provenance conventions.

Assessment: safe but inefficient as the project family grows.

### Option 2 - Dedicated Shared Infrastructure Repository Now

Advantages:

- one implementation of common infrastructure;
- centralized versioning and contracts.

Disadvantages:

- current commonality is mostly conceptual rather than proven by identical stable interfaces;
- KRC contracts are workflow-specific;
- K-Trader evidence is market-specific;
- VoiceBridge is media/speech-specific;
- premature extraction would create coupling before boundaries are stable.

Assessment: premature at the current maturity level.

### Option 3 - Hybrid Architecture

Keep project domain logic and canonical stores independent while standardizing narrow cross-project contracts first.

Promote a component to shared infrastructure only after at least two projects demonstrate the same stable requirement and compatibility tests can be defined.

Assessment: recommended.

## Recommended Architecture

HYBRID

### Remain Project-Local

K-Geopolitical Monitor:

- Event and geopolitical Entity semantics;
- Knowledge Graph;
- Causal Intelligence;
- Temporal Graph;
- geopolitical forecasting and importance models;
- project database and indexes.

K_Research_Critic:

- Task and Workflow models;
- CriticProfile;
- research-specific Claim and Source contracts;
- review and approval lifecycle.

K-Trader:

- market models;
- VSA/trap evidence;
- trading risk, scoring and execution semantics;
- market storage.

VoiceBridge:

- media retrieval;
- speech/transcription/translation runtime;
- media-specific state and storage.

### Candidates for Future Shared Extraction

Only after demonstrated multi-project use:

- provenance envelope minimum fields;
- generic source metadata envelope;
- provider error/retry envelope;
- telemetry and request logging primitives;
- common identifier/versioning conventions where semantics truly match;
- CI/documentation templates;
- generic connector interfaces, not provider-specific or domain-specific implementations.

## Storage Boundary

Current decision for M5 readiness:

- no shared runtime database;
- no implicit mixed storage;
- no direct write access to another project's canonical store;
- each project remains Source of Truth for its own domain data;
- cross-project data exchange must use a versioned contract, export or API;
- cross-project access is read-only by default unless an approved contract explicitly grants writes;
- failures in one project must not corrupt another project's canonical state.

A future global provenance, entity identity or connector service requires a separate validated need and architecture decision.

## Extraction Rule

A candidate may be extracted to shared infrastructure only when all conditions hold:

1. at least two projects consume materially the same capability;
2. semantics are compatible, not merely similarly named;
3. a versioned public contract exists;
4. compatibility tests exist for all consumers;
5. ownership and Source of Truth are explicit;
6. failure isolation and rollback are defined;
7. migration does not require silent access to another project's storage.

## Result

Shared Infrastructure Architecture Review: COMPLETE.
Recommended model: HYBRID.

M5 may proceed with project-local implementation after the readiness gate is closed.

Cross-project component extraction, shared runtime storage, and silent mixed-resource consumption remain prohibited until a specific architecture decision is approved.
