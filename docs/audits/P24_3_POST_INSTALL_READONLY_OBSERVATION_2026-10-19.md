# P24.3 post-install read-only observation — 2026-10-19

## Scope
Independent kgmops read-only inspection after owner-authorized doubled limits and observability timer installation. No changes to production by this audit.

## Attested
- kgm-monitor.service active; MainPID 906, NRestarts 0.
- MemoryCurrent=16867328 bytes; MemoryPeak=17129472 bytes.
- MemoryHigh=536870912 bytes (512 MiB); MemoryMax=1073741824 bytes (1 GiB).
- CPUQuotaPerSecUSec=1s (100% of one CPU), TasksMax=128.
- memory.events: low/high/max/oom/oom_kill/oom_group_kill/sock_throttled all 0.
- kgm-observability.service Result=success, ExecMainStatus=0; last start/finish 2026-10-19 11:35:35 UTC.
- kgm-observability.timer lists next 2026-10-19 11:50:58 UTC; 15-minute cadence configured.

## Remaining qualification / explicitly unavailable evidence
- Only initial collector execution independently attested. Next timer firing not yet observed.
- Attempts to read cpu.stat and journalctl through currently authorized remote executor returned tool security blocks; no CPU throttling count or journald contents attested. Do not claim these PASS.
- Loaded Python source provenance still not attested. No end-to-end high-load soak or failure-injection under new resource limits.
- Resource cap is configured in systemd and unit still running, but effective post-reload cgroup knobs should be checked separately before claiming kernel enforcement.
- Existing P24.2-A cleanup remains HOLD; production research/source/consumer activation remains NO-GO.

## Next safe gates
1. Observe at least two scheduled timer firings and verify Result, status and sanitized metrics count; do not trigger a timer by repeatedly dispatching GitHub workflows.
2. Obtain CPU throttling/read-only journal evidence through an explicitly approved narrow administrative diagnostic, not by broadening kgmops sudo.
3. Inspect effective cgroup cpu.max/memory.high/memory.max, compare with systemd configuration, qualify workload peak and rollback.
4. Complete P24.3 observational acceptance before any broader production activation.

FREE_ONLY / NO_SEND / PRODUCTION NO-GO.
