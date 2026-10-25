# O1 runtime attestation checkpoint — 2026-10-25

## Decision
**O1_PARTIAL / LOADED_CODE_UNKNOWN / OPERATIONAL_HEALTH_UNVERIFIED / PRODUCTION_NO_GO**.

This is a read-only inspection of `kgm-e4-owner-pilot` via authorized Remote Desktop Commander. Do not infer service health from a running process. No deployment, restart, migration, writer action, data modification, external delivery, cleanup or secrets inspection occurred.

## Reproducible observations
- Host: `kgm-e4-owner-pilot`; ARM64 `aarch64` (earlier observed).
- Service: `kgm-monitor.service`, `ActiveState=active`, `SubState=running`, `Result=success`, `NRestarts=0`; `MainPID=125277`.
- Service start `2026-10-24 06:39:45 UTC`; `ExecStart=/opt/k-geopolitical-monitor/.venv/bin/python -m kgeopolitical_monitor.unattended_runner --project-root /opt/k-geopolitical-monitor --poll-seconds 60`.
- Visible process inventory showed one corresponding runner PID 125277, owned by `kgm`. Process count observed through accessible ps is not proof that no short-lived competing writers exist.
- Checkout on disk: `b31b2136b5fe982d0b63b0135479b1549041906c`. Accepted S5 research main after PR #251: `972abc729265ff4c5841f45438d698783669404a`.
- Untracked `src/k_geopolitical_monitor.egg-info/`; left untouched. `unattended_runner.py` root-owned mode 644, last stat mtime 2026-09-01 08:26 UTC; mtime is not provenance attestation.
- `systemctl cat`: `User=kgm`, `UMask=0077`, `ProtectSystem=strict`, `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectHome=true`, `PrivateDevices=true`, `CapabilityBoundingSet=` empty, `ReadWritePaths=/opt/k-geopolitical-monitor/data`, `Restart=on-failure`.
- Resource drop-in: `MemoryHigh=512M`, `MemoryMax=1G`, `CPUQuota=100%`, `TasksMax=128`.
- Persistent `data` path owner `kgm:kgm`, permission mode 750, inaccessible to inspection account. No DB/forward-state content inspected.
- `/proc/125277/exe`, `cwd`, `root` symlink targets: permission denied. No loaded-module/hash attestation.
- Unprivileged `journalctl -u kgm-monitor.service`: access restriction; `-- No entries --` is NOT evidence of zero errors or successful cycles. Attempt to run a broader privileged inspection through remote policy was denied.

## Evidence matrix
| Requirement | Observed | Gate |
|---|---|---|
| unit active, process running | yes, timestamped read-only systemd/ps | PASS narrowly |
| service hardening settings | systemd unit and drop-in inspected | PASS settings only |
| checkout SHA | b31b2136... | PASS disk-only |
| actual imported/loaded code SHA | access restricted; cannot safely infer from disk | UNKNOWN |
| writer quiescence/lease correctness | process listing not sufficient | UNKNOWN |
| journal failure rate/last successful cycle | journal access restricted | BLOCKED |
| source freshness/provenance | not measured in this O1 run | NOT_OBSERVED |
| persistent forward-state integrity | data access restricted | BLOCKED |
| release/production go | no authorization | NO_GO |

## Next permitted work
1. Establish a bounded **read-only** privileged audit facility for `kgm` service logs and state summaries, with redaction and no token/raw secret disclosure; owner controls privileges.
2. Provide an explicit read-only loader/package provenance attestation method (process start vs checkout history; interpreter path; import locations) without service restart or code execution inside the live process.
3. Verify last N completed unattended cycles and persistence invariants from read-only summarized evidence, then compare with source freshness/provenance. Distinguish observational metadata from factual verification.
4. Record findings and make separate owner decision about O1 gate; do not assume qualification of O2–O5 or production.

Policy: **FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO**. This checkpoint is not a production approval.
