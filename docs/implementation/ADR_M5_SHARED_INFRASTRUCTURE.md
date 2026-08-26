# ADR M5 - Shared Infrastructure Boundary

Status: PROPOSED
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Context

K-Geopolitical Monitor now has implementation baselines through M4 and is preparing M5 Operational Intelligence Platform work.

Related repositories contain conceptually overlapping infrastructure and models, but their domain semantics and runtime ownership differ.

The architecture review evaluated fully independent repositories, immediate extraction to a dedicated shared repository, and a hybrid model.

## Proposed Decision

Adopt a HYBRID architecture.

- Keep project-specific domain models, algorithms and canonical storage in their owning repositories.
- Standardize narrow cross-project contracts before sharing implementations.
- Do not create a dedicated shared runtime repository merely because component names are similar.
- Extract shared infrastructure only after proven multi-project use, stable semantics and compatibility tests.
- Prohibit implicit mixed storage and direct mutation of another project's canonical store.

## Consequences

Positive:

- preserves project autonomy and failure isolation;
- prevents premature coupling;
- allows future reuse where commonality is demonstrated;
- provides a controlled path toward shared provenance, telemetry or connector primitives.

Tradeoffs:

- some temporary duplication may remain;
- future shared extraction requires explicit migration work;
- cross-project contracts must be versioned and tested.

## Approval Boundary

This ADR is PROPOSED, not APPROVED.

The M5 Shared Infrastructure Architecture Review is complete, but cross-project extraction or shared runtime storage requires explicit owner approval of this ADR or a superseding architecture decision.
