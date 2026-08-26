# EXTERNAL_INTEGRATIONS

Version: 0.4
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

## Approved Controlled-Pilot External Integrations

### Consilium Press Releases RSS

Status: APPROVED_FOR_CONTROLLED_PILOT
Class: Official sources
Mode: public read-only RSS; no authentication
Record: docs/integrations/CONSILIUM_RSS_CONTROLLED_PILOT.md
Live smoke: PASS

### GDELT DOC 2.0 API

Status: APPROVED_FOR_CONTROLLED_PILOT
Class: Structured data
Mode: public read-only HTTPS API; no authentication
Record: docs/integrations/GDELT_DOC2_CONTROLLED_PILOT.md
Live smoke: PASS

GDELT is used for discovery/index metadata only and is not treated as independent verification of linked publisher claims.

## Failure Boundary

- external-source failures fail closed at the affected adapter;
- source failures are recorded in collection audit state;
- one source failure must not block another source adapter;
- deterministic CI does not depend on live network availability;
- live network verification is isolated in a manual smoke workflow.

## Current State

Controlled-pilot external integrations approved: 2
Controlled live-source acquisition: VALIDATED
Production/global external integrations: NONE_APPROVED
Cross-project runtime sharing: BLOCKED_BY_APPROVED_PROJECT_LOCAL_ONLY_BOUNDARY
Approval status: REVIEW_REQUIRED_FOR_PRODUCTION_INTEGRATIONS
