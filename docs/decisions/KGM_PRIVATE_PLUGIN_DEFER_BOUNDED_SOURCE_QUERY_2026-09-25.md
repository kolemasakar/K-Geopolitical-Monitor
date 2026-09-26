# KGM decision: defer bounded degraded-source query until public release

Date: 2026-09-25
Status: OWNER_APPROVED / DEFERRED
Scope: K-Geopolitical Monitor private owner-only Plugin v0.1.

## Decision
The owner is currently the sole user. Do **not** implement the proposed `degraded_sources_limited()` / upstream SQL limit optimization in the current private owner-only stage. Retain the existing 20-item response projection in `kgm_get_status` and the existing `BackendStateReader.degraded_sources()` behavior. This is a conscious acceptance of a **performance/scalability risk**, not a declaration that the underlying query is bounded.

## Mandatory public-release gate
Before transitioning the KGM Plugin/API to any public or multi-user release:
1. Implement a dedicated bounded upstream degraded-source query with stable ordering and explicit truncation / has-more semantics (e.g. fetch limit+1).
2. Review SQL query plan, intermediate result costs, appropriate indexes, and representative load/concurrency tests. LIMIT on the final result alone may not bound upstream work.
3. Preserve existing consumer compatibility; do not silently change the legacy `degraded_sources()` method.
4. Validate authentication, rate limiting, secret-safe error handling and data exposure separately.
5. Record test evidence and approve the gate **before** public enablement.

## Private-stage safeguards
Keep private owner-only access, a 20-item output cap, no public ingress, and no paid services. Do not claim that the private-stage query is load-bounded. Revisit early if measurable latency, memory, or DB contention emerges, even while single-user.

This decision supersedes the earlier proposal to immediately address the unbounded upstream read. It does not defer other independent security and correctness requirements.
