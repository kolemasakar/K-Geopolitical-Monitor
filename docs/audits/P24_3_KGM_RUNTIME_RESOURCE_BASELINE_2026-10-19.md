# P24.3 KGM real VM resource and unattended unit audit — 2026-10-19

**Read-only measurement; no systemd/unit/runtime changes.** Sources: GitHub Actions owner SSH run [39243681720](https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/39243681720) and independent `kgmops` Remote Desktop Commander read-only `systemctl show`/`systemctl cat`/`df`.

## Runtime
- `kgm-monitor.service`: `active/running`, `enabled`, `User=kgm`, `Group=kgm`, `PID=906`, `NRestarts=0`.
- `Restart=on-failure`, `RestartSec=10`, `OOMPolicy=stop`.
- `MemoryCurrent=16867328` bytes (~16.1 MiB); `MemoryPeak=17129472` bytes (~16.34 MiB); `TasksCurrent=1`.
- `MemoryMax=infinity`, `CPUQuotaPerSecUSec=infinity`, `TasksMax=6327`. **No explicit RAM/CPU limits.**
- Disk `/dev/sda1`: 46212176 KiB total, 37312092 KiB available (~80.74% free), 20% occupied; filesystem ext4.
- `CPUUsageNSec=14816233000` cumulative (not a point-in-time CPU utilization rate).

## Unit hardening already present
`NoNewPrivileges=true`, `PrivateTmp=true`, `PrivateDevices=true`, `ProtectSystem=strict`, `ProtectHome=true`, kernel restrictions, empty capability sets, `UMask=0077`, `ReadWritePaths=/opt/k-geopolitical-monitor/data`.

## Qualifiers
- Single-point RAM is **not enough to prescribe a safe `MemoryMax`**; measure across scheduled ingest, larger source batches, retention and recovery scenarios first.
- Resource limit installation is intentionally deferred; changing unit settings may alter a running unit or require reload and is a separate reviewed operation.
- Loaded Python release still `NOT_ATTESTED`; disk checkout SHA is not proof.
- No journal-error census was obtained by owner SSH workflow; previous probe noted `NOT_ATTESTED_WITHOUT_ADMIN`.
- Production cleanup remains HOLD, unrelated to progression of resource/observability controls.
- Preserve `FREE_ONLY / NO_SEND / Production NO-GO`.

## Next gates
1. Add bounded read-only collection of `MemoryCurrent`, `MemoryPeak`, cumulative CPU, cgroup `memory.events` and service restart events, with small outputs and no private logs or DB records.
2. Design conservative resource protections from observed peak envelope and system-wide headroom. Review and authorize separate unit drop-in before application; avoid unattended production restart.
3. Define retention/resource observability alert thresholds with disk reserve >=10% and evidence of stability over real workload.
4. Complete loaded-source provenance, rollback and consumer NO_SEND gates before production admission.
