# P24.2-B–E and P24.3 execution handoff — 2026-10-19

## Decision
P24.2-A accepted as **PASS_WITH_LOADED_CODE_LIMITATION** for bounded backup/restore/diagnostic evidence. Cleanup stays **HOLD** and is removed from the critical path. PR #233 is separate and draft; do not merge or run deletion to unblock reliability work.

## Already qualified offline (historical)
P24.2-B–D isolated mechanisms and P24.2-E offline acceptance already reported on 2026-10-16: 1642 native ARM64 tests PASS, 1642 CI PASS; caveats remain. Do not relabel these as production unattended operation. P24.3 production retention/resource/observability integration remains outstanding.

## Current automation
`.github/workflows/p24-reliability-readonly-baseline.yml` checks existing owner SSH credentials, live service activity, systemd resource-limit metadata, filesystem capacity and enabled state without modifying the host. It prints no application source or raw database content. A passing probe does not attest the loaded Python release, current data integrity, comprehensive log health or scheduler autonomy. Does not enable cron/timer or alter services.

## Next implementation sequence
1. Record read-only baseline from CI; separately validate whether `MemoryMax`/`CPUQuota` are unbounded on the live unit and quantify disk reserve; no assumption of enforcement without measurement.
2. P24.2-B: review existing offline scheduler recovery evidence and missing cases, specifically duplicate writer prevention, timeout, retry exhaustion, restart replay. Add offline tests only for actual gaps.
3. P24.2-C/D: preserve isolated migration and rollback evidence; production migrations and new runtime releases require an explicit rollback and owner gate. No live writes.
4. P24.2-E: exact-head CI and sanitized result; reconcile evidence to the candidate commit, not runtime loaded code.
5. P24.3: design retention policy across report/backup/temporary storage, resource limits, service journal/cgroup inspection, and bounded periodic checks. Start with read-only diagnostics; only propose production timers and limits after safe review and owner approval.
6. P24.4: fresh loaded-code provenance/actual source selection from new instrumented start after separate planned deployment; independent production decision; NO_SEND consumer connection remains disabled.

## Invariants
FREE_ONLY; no shared K-Trader/KRC resources; no service restart, production checkout mutation, source activation, external delivery, live migration, deletion, or paid service. CI jobs may read existing service metadata only. Keep P23.4 owner gate and strategic Phase 23 position unchanged.
