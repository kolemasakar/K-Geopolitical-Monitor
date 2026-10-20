# P24.3 kernel resource enforcement observation — 2026-10-19

Scope: read-only /sys/fs/cgroup and systemd inspection via approved KGM kgmops remote access. No deployment or service restart.

## Confirmed
- Active KGM service PID 906; NRestarts=0; MemoryCurrent=16867328 B; MemoryPeak=17129472 B.
- Kernel cgroup v2 `cpu.max = 100000 100000`: quota of one full CPU.
- Kernel `memory.high = 536870912` (512 MiB), `memory.max = 1073741824` (1 GiB).
- Kernel `cpu.stat`: `usage_usec=14931200`, `nr_periods=31`, `nr_throttled=0`, `throttled_usec=0`. This is current accumulated data, not a workload saturation test.
- Observability one-shot last success: service ExecMainStartTimestamp 2026-10-19 11:45:42 UTC, Exit 0.
- Timer active; timer `LastTriggerUSec=2026-10-19 11:35:35 UTC`; separate service execution at 11:45:42 UTC **does not establish that the timer triggered the latter**. `list-timers` showed next 12:00:59 UTC; track at least two independently confirmed timer triggers before claiming recurring cadence acceptance.

## Decisions
RESOURCE_CGROUP_LIMITS=PASS; NO_CPU_THROTTLING_OBSERVED_AT_SAMPLE=PASS; FULL_LOAD_QUALIFICATION=PENDING; TIMER_RECURRENCE=PARTIAL; LOADED_CODE_ATTESTATION=PENDING.

Do not activate KGM consumer delivery or source changes. Preserve cleanup HOLD, FREE_ONLY, NO_SEND, production research GO/NO-GO gate.
