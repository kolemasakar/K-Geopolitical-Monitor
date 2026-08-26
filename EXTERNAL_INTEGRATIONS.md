# EXTERNAL_INTEGRATIONS

Version: 0.2
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

They may become shared infrastructure only after an approved architecture decision defines:

- shared ownership;
- canonical contracts;
- read/write boundaries;
- versioning;
- compatibility policy;
- failure isolation;
- migration and rollback rules.

No implicit mixed storage or silent cross-project mutation is permitted.

## Current State

No production external integration is approved yet.
Cross-project resource sharing: NOT_APPROVED_PENDING_SHARED_INFRASTRUCTURE_REVIEW
Baseline integration boundaries: DOCUMENTED
Approval status: REVIEW_REQUIRED
