# P24.3 Resource limits, retention and alert policy — DRAFT / NOT APPLIED

Evidence: live systemd read-only sample 2026-10-19, MemoryCurrent=16,867,328 B, MemoryPeak=17,129,472 B, MemoryMax=infinity, CPUQuota=infinity, TasksCurrent=1, NRestarts=0; 5,901 MiB physical RAM, 5,169 MiB available, 2,047 MiB swap free; disk 20% used, ~36 GB free; `nproc=1`. This is a snapshot, not peak workload qualification.

## Why unlimited now
Current root-owned `kgm-monitor.service` has general sandbox protections but no MemoryMax/CPUQuota directives. This is an incomplete P24.3 resource gate, not evidence of immediate saturation.

## Review-only candidate
```ini
[Service]
MemoryHigh=256M
MemoryMax=512M
CPUQuota=50%
TasksMax=64
```
This is **not approved or deployed**. Need native ARM64 replay of heaviest existing collection/recovery workload and empirical high-water memory/CPU usage, timeout and retry impacts; include OOM and CPU throttling thresholds before adoption. Do not apply through `systemctl set-property` or a drop-in until a separate owner-reviewed change plan includes monitoring, rollback and service-impact analysis.

## Observability
- New code: `ops/p24_observability/kgm_readonly_metrics.py`, sanitized JSON (systemd current/peak RAM, CPU cumulative nanoseconds, tasks/restarts, cgroup memory.events where readable, filesystem free percentage). No application log bodies, SQLite rows, outbound send or public network.
- `ALERT` on failed service or disk free <10%; trend alerts on restart delta, OOM kill >0, sustained memory pressure and CPU throttling require baseline and correctly implemented scheduler; no false assurance from static CPUUsageNSec.
- Collection schedule NOT enabled. For FREE_ONLY, prefer existing local KGM management timer at a bounded interval over using paid/minute-metered GitHub-hosted workflows, only after owner reviewed installation and privilege scope.
- Retain aggregate numeric metrics ~7 days after storage estimate; cap file size and atomic replacement; never log credentials, report contents or private records.

## Retention and safety
- Preserve accepted P24.2-A snapshot/manifest/report as **HOLD** evidence until separately approved executor and rollback.
- Retention applies only to future explicitly identified temp files, with fixed allowlists, size limits, >=10% disk free guard, and no wildcard or recursive removal of production data.
- No live cleanup, deletion, service restart, unit limit, timer installation, source activation, new provider, K-Trader/KRC resource use, or consumer send.

## Acceptance gates
1. Unit and CI for collector, read-only run from KGM with expected schema and accurate failure behavior.
2. Multi-cycle real workload sampling of CPU/RAM high-water; quantify quota impact.
3. Independent security review of retention and monitoring writes before installing timer.
4. Explicit owner change approval + rollback proof before systemd resource limit or timer activation.
Status FREE_ONLY / NO_SEND / PRODUCTION NO-GO.
