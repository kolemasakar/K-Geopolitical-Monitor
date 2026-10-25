# O1 scoped read-only diagnostics gate — 2026-10-25

Decision: **O1_PARTIAL / PRIVILEGED_OBSERVABILITY_BLOCKED / NO_PRODUCTION_CHANGE**.

## Fresh verification
- GitHub PR #252 passed CI #3717 and merged to canonical main at `80504f5da30caf07c7fd4d5cf7dacc7e21496748`.
- Remote Desktop Commander endpoint: `kgm-e4-owner-pilot`, user `kgmops`. `whoami` and `groups` returned only `kgmops`.
- The inspection account cannot read protected `/opt/k-geopolitical-monitor/data`, `/proc/125277/exe`, or system service journal; such denial is preserved as **BLOCKED**, not a healthy-result claim.
- Inspectable `/usr/local/bin` had no matching `kgm|sentinel|inspect|audit|read` helper names; `/home/kgmops/.local/bin` includes only `kgm-rdc-watchdog.sh`. These directory checks cannot prove absence of all possible administrative mechanisms.
- `kgm-monitor.service`: `ActiveState=active`, `MainPID=125277`, `NRestarts=0`, `Result=success`.
- Disk Git HEAD remains `b31b2136b5fe982d0b63b0135479b1549041906c`. Neither service process loaded-code SHA nor semantic ingest success is proven.

## Proposed narrow administrator-operated observability mechanism (NOT INSTALLED)
1. Administrator reviews a root-owned, non-writable-to-kgmops, fixed-function diagnostic helper; no user-supplied command, arbitrary file path, shell, or dynamic SQL.
2. Output is limited to redacted aggregate service journal counts/time range, bounded most recent successful/failed cycle timestamps, read-only database integrity and forward-state counters, and import-module provenance if safely attestable. No tokens, passwords, source item text, raw log lines or raw database export.
3. Data access requires existing least-privilege permissions, no direct general sudo/shell, no remount, restart, migration, cancellation, deployment, backup restore, cache cleanup or writer resume.
4. Admin performs a dry read-only policy/side-effect review; owner separately authorizes the exact helper before any server installation or sudoers changes.
5. Independent reviewer compares snapshot with checkout Git SHA and service start time; no claim that disk SHA equals in-memory imported code without direct evidence.

## Required O1 evidence
- Scoped unit log summary with explicit permissions and window.
- Successful/failed unattended cycle timestamps, source health/freshness samples, and operational clock references.
- SQLite read-only integrity check and forward-state summary only if safely snapshot-consistent (avoid unintended WAL writes/lock disruption).
- Process/module loaded-code provenance or explicit `UNKNOWN`.
- Decision `PASS / PASS_WITH_KNOWN_LIMITATIONS / BLOCKED` for O1 independently of S5 offline PASS.

**Policy:** FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO. No privileged facility was installed; only documentation is proposed.
