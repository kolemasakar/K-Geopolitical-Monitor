# P24.3 observability recurrence and CI installation trigger audit — 2026-10-19

## Read-only production facts
- KGM active, PID=906, NRestarts=0, MemoryCurrent=17117184 bytes, MemoryPeak=17129472 bytes.
- cpu.stat sample usage_usec=14942675, nr_periods=39, nr_throttled=0, throttled_usec=0.
- kgm-observability.service last invocation 2026-10-19 11:48:57 UTC returned 0.
- Timer active; LastTriggerUSec still 2026-10-19 11:35:35 UTC; next as reported 12:04:13 UTC. Multiple service invocations are NOT proof of successive timer fires.

## CI finding and correction
- Existing owner install workflow originally included a pull_request trigger scoped to its workflow file and was observed to run repeatedly on PR updates; every run includes `systemctl start kgm-observability.service`, potentially resetting OnUnitActiveSec and shifting the timer schedule.
- Disabled the pull_request trigger on this production-install workflow at commit b4bd524, leaving **workflow_dispatch ONLY**. This prevents further PR-driven installation runs. Do not trigger it for routine checks; use the separately read-only workflow.
- Repository-wide CI on head 7004afca SUCCESS, plus specialized read-only tests SUCCESS; a new CI run after b4bd524 should be checked before merge.
- No deletion, KGM restart or external send performed by this audit. Current systemd services and caps remain as configured.

## Remaining
Observe two timer-origin triggers where LastTriggerUSec advances naturally, then document intervals and service outcomes. Verify journal/retention/cgroup evidence without untrusted log publication. Test actual workload peaks before declaring limits fully qualified. Loaded code and integration gates unchanged. FREE_ONLY / NO_SEND / production research NO-GO / cleanup HOLD.
