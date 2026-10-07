# KGM Real Source Execution owner-pilot gate audit — 2026-10-07

## Decision

**KGM_REAL_SOURCE_EXECUTION_READY_FOR_OWNER_PILOT = PASS_WITH_RESTRICTIONS**

This gate authorizes only the next isolated owner-pilot step: implementing and testing explicitly approved public/free source adapters. It does **not** authorize production activation, unattended live-source operation, Sentinel transport, K-Trader integration, paid providers, or release of real-corpus results.

## Verified basis

Exact isolated SHA: `4242ea011e72b9addccbee4cf9eabe2dea718cf4`.

- Source Adapter Contract v1 validates typed source identity, correlation, provenance and explicit source status.
- Historical requests enforce publication and availability cutoff; look-ahead fails closed.
- Duplicate/corrupt observations fail closed.
- Deterministic worker connects ACCEPTED → PROCESSING → normalized evidence → immutable typed COMPLETE/PARTIAL result.
- Adapter crash and invalid observation leave PROCESSING recoverable.
- Retry after adapter crash completes without duplicate terminal state.
- Terminal replay is rejected before invoking an adapter; immutable artifact remains authoritative.
- Targeted source/worker/restart/completion suite: 23/23 PASS.
- Selected exchange/research regression: 161/161 PASS.

Previous exact SHA `46db415f7650c58b1753f456404241f32ed7e300` passed GitHub CI run 2411.

## Restrictions for next step

1. First real adapters must be public, free, read-only and explicitly bounded.
2. No credentials or paid fallback.
3. Owner-pilot only; no daemon/unattended scheduling.
4. Preserve raw provenance metadata needed by the typed observation contract.
5. Each adapter gets deterministic fixtures plus live read-only acceptance tests before expansion.
6. A live-source failure must map to explicit PARTIAL/UNAVAILABLE behavior; it must never create false COMPLETE.
7. K-Trader and Sentinel remain excluded until separately authorized.

This gate does not declare `KGM_INDEPENDENT_RESEARCH_READY`.
