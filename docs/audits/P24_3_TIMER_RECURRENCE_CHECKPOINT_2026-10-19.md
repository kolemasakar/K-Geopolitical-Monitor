# P24.3 timer recurrence checkpoint — 2026-10-19

Read-only independent KGM host inspection at 2026-10-19 11:53:31 UTC:
- Service `kgm-monitor.service`: active, MainPID=906, NRestarts=0, MemoryCurrent=16867328 B, MemoryPeak=17129472 B.
- CPU cgroup `nr_periods=43`, `nr_throttled=0`, `throttled_usec=0`.
- `kgm-observability.timer` active, `LastTriggerUSec=2026-10-19 11:35:35 UTC`.
- Observability oneshot last success at 11:48:57 UTC. This service execution **cannot** be attributed to the timer, since timer LastTrigger did not advance.
- Special CI checks on head 3b4f2d46 PASS; full CI was still in progress when checked.

New review-only script `ops/p24_observability/kgm_timer_readonly_gate.py` makes timer freshness/last service success explicit and fails closed on stale trigger. It **does not** attest two distinct natural firings by itself and has no start/restart/schedule mutation operation.

Acceptance still PENDING until two naturally occurring LastTrigger transitions have been observed, preferably over 30–45 minutes without reinstall workflow dispatch. A completed scheduled service exit is different from a manual oneshot execution. No background work is promised or started here.

NO_SEND / FREE_ONLY / production research NO-GO / P24.2-A cleanup HOLD.
