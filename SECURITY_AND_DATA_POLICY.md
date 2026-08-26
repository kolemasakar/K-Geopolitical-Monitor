# SECURITY_AND_DATA_POLICY

Version: 0.2
Status: REVIEW_REQUIRED

## Purpose

Define security and data governance principles for K-Geopolitical Monitor.

## Principles

- Data provenance must be preserved.
- Access must follow least privilege.
- Sensitive user-provided information requires explicit handling rules.
- External data usage must respect applicable restrictions.
- Auditability is required for important analytical outputs.
- Operational claims must be supported by reproducible evidence.

## Data Categories

- public information
- user-provided information
- derived analytical data
- operational metadata

## M5 Baseline Boundaries

- Public-source monitoring is the default data mode for the current baseline.
- Secrets, tokens and credentials must not be stored in repository files.
- External credentials must be supplied through environment or platform secret storage.
- Provenance must retain enough information to identify the originating source and collection context.
- Derived conclusions must remain distinguishable from source evidence.
- Cross-project repositories, stores, indexes, graphs, caches or datasets must not be consumed implicitly.
- Any cross-project resource is treated as an external integration until a Shared Infrastructure architecture decision explicitly defines it as shared infrastructure.
- Shared resources require an explicit owner, Source of Truth, data contract, access mode, failure boundary and lifecycle rule.
- One project must not silently mutate another project's canonical data.

## M5 Readiness Rule

M5 operational implementation must not be marked ready until security and data boundaries are reviewed together with the Shared Infrastructure Architecture Review.

## Current State

Baseline boundaries: DOCUMENTED
Approval status: REVIEW_REQUIRED
Detailed production security architecture: NOT_DEFINED
