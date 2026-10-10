# KGM bounded recovery index design — pre-implementation gate

Date: 2026-10-07. Scope: owner-only offline canonical research workflow. This design does not activate production, providers, K-Trader, HP-OMEN or public ingress.

## Problem

Canonical `recovery_snapshot` sorts and validates every `inbox/*.json` request on every recovery pass. `max_items` bounds processing only, not filesystem reads. The durable cursor fixes fairness but not O(total inbox) scan cost.

## Required properties

1. Request JSON remains the source of truth. An index is rebuildable metadata, never authority for lifecycle state.
2. No request may disappear from recovery merely because an index update crashed.
3. Index corruption or request/index disagreement fails closed or triggers an explicit bounded rebuild path; never silently marks work complete.
4. Terminal transition and index removal cannot form an unsafe transaction. A stale index entry is acceptable because canonical request validation can prove terminal state; a missing pending entry is not acceptable.
5. Existing owner-only flock/fsync/atomic-replace primitives remain the durability baseline.
6. Historical no-lookahead/result integrity rules are unaffected.

## Proposed v1

Use an append-only pending journal plus compact checkpoint, generation-numbered and digest-bound. Admission writes canonical request first, then journal ADD. State transitions that remain pending need no journal change. Successful terminal/expiry writes canonical state first, then journal REMOVE. Therefore crashes can create stale ADD entries but cannot make a request terminal before canonical state says so.

Because admission can crash after request write but before ADD, indexed recovery alone is insufficient. Add a durable high-water generation to admission and reconcile a bounded tail of request generations; periodic full audit/rebuild remains mandatory until a single atomic database is adopted. **Do not implement indexed-only recovery before this missing-ADD problem is solved and tested.**

## Benchmark gate

Before implementation, measure canonical recovery on synthetic durable records at 100, 1,000, 5,000 and 10,000 pending items, at least three runs each, recording wall time and peak process RSS where available. Benchmark must run only on the authorized isolated KGM host and use disposable directories. No production corpus.

Acceptance for indexed work is evidence-driven: retain O(N) implementation if measured scale is operationally adequate; otherwise implement journal/checkpoint only after crash invariants above have executable tests.

## Current dependency

The terminal-success gate was implemented on branch in commits `3d20a4aa7ee212cf4e78cbc20fd4b8acd4ae236e` through `71604c6733437010a16bcb6d8eb5c31ab5a2499d`, but exact-SHA isolated validation is pending because the authorized KGM validation host is currently offline. Do not use HP-OMEN or unrelated project hosts as substitutes.
