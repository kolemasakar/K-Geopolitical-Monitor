# EXTERNAL_INTEGRATIONS

Version: 0.3
Status: REVIEW_REQUIRED

## Purpose

Define rules for external services, cross-project resources and integrations.

## Integration Categories

- public data sources
- external APIs
- authentication services
- AI services
- storage services
- monitoring services
- cross-project repositories and shared infrastructure resources

## Required Integration Record

Each integration requires:

- purpose
- owner
- provider or source
- data exchanged
- data classification
- authentication mode
- security considerations
- Source of Truth
- fallback strategy
- failure isolation rule
- operational impact
- approval status

## Cross-Project Rule

Repositories, databases, graphs, caches, indexes, datasets and services owned by another project are external integrations by default.

ADR_M5_SHARED_INFRASTRUCTURE.md is APPROVED and establishes HYBRID architecture with PROJECT_LOCAL_ONLY runtime storage for the current implementation line.

Current cross-project rules:

- no shared runtime database;
- no implicit mixed storage;
- no direct write access to another project's canonical store;
- cross-project exchange requires a versioned contract, export or API;
- cross-project reads are external integrations unless explicitly promoted by a later architecture decision;
- failures in one project must not corrupt another project's canonical state.

Any future shared runtime or cross-project write capability requires a new explicit architecture approval.

## Controlled Pilot Boundary

M6 controlled pilot monitoring is validated using deterministic project-local source fixtures.

This validates the integration boundary without approving a production external provider.

A live public-source pilot must create an integration record before activation and must define provider, data contract, provenance fields, failure behavior and Source of Truth.

## Current State

Production external integrations: NONE_APPROVED
Controlled project-local pilot: VALIDATED
Cross-project runtime sharing: BLOCKED_BY_APPROVED_PROJECT_LOCAL_ONLY_BOUNDARY
Baseline integration boundaries: DOCUMENTED
Approval status: REVIEW_REQUIRED_FOR_PRODUCTION_INTEGRATIONS
