# KGM exchange P2/P3 offline acceptance checkpoint

Date: 2026-09-28. Issue #162, draft PR #163, Sentinel PR #26, K-Trader PR #87.

At exact code SHA `3d6b66f2cad1662f3a59c4682b42a06d162bf664`, an isolated KGM-host checkout ran six synthetic test modules: contract, legacy artifact, generation, replay, ledger and failure injection. Result: **42 passed in 0.36s; exit 0**. This does not demonstrate real source output or operational channel readiness.

Implemented offline candidates:
- Atomic generation-directory publisher and strict completion marker/manifest/digest reader. Legacy two-file writer remains in draft branch and is NOT production-ready.
- Pure bounded replay selection with explicit cursor expiry, gap, reorder and duplicate checks.
- `exchange_ledger_v1.py` prototype: flock-protected append-only JSONL, fsync, digest-bound idempotent append of already published generations, bounded replay. Assumes private dedicated POSIX filesystem and trusted single publisher.
- Synthetic failure injection: rename failure leaves no published generation, absent generation rejected, duplicate attempt preserves original.

**Unresolved material safety issues:** interrupted JSONL append may leave a truncated final line; concurrent reader lacks shared ledger lock; current ledger replay does not implement pruning/retention and must not claim durable crash recovery. No real power-loss or hostile-filesystem tests, no approved exporter read identity or data release policy, no real source/forecast measurement, no private transport credentials or receiver E2E. Keep all new modules isolated and unused by production until these gates are resolved. Private Plugin PR #161 remains paused; strategic Phase 23 unchanged.
