# S5.4 read-only operational audit — 2026-10-16

Status: **PARTIAL / PRODUCTION_GATE_OPEN**. This audit is a verified snapshot, not a deployment authorization.

## Repository and approved research scope
- PR #215 owner-approved S5 research-only roadmap, GitHub CI SUCCESS, merged `8870bcb4855e4c1493c27e6d4241ecce247e9950`.
- PR #216 owner approval synchronized to `ROADMAP.md`, `CURRENT_HANDOFF.md`, `CURRENT_PROJECT_STATE.json`; CI SUCCESS, merged canonical main `9e0d32e2c0dbd93d0fc034a66cf2bc00feff4d30`.
- Independent S5.1/S5.2/S5.3 draft implementation PRs #217/#218/#219, pending exact-head CI/full native ARM64 gate at time of this audit.
- S3/S4 research-only already accepted with limitations. NO_SEND retained.

## Read-only native ARM64 runtime evidence
Host: `kgm-e4-owner-pilot` (`aarch64`).
- `systemctl is-active kgm-monitor.service`: **active**.
- `ActiveState=active`, `SubState=running`, `ExecMainPID=208487`.
- `WorkingDirectory=/opt/k-geopolitical-monitor`.
- `ExecStart`: `/opt/k-geopolitical-monitor/.venv/bin/python -m kgeopolitical_monitor.unattended_runner --project-root /opt/k-geopolitical-monitor --poll-seconds 60`.
- Runtime `/opt/k-geopolitical-monitor` Git HEAD: `b31b2136b5fe982d0b63b0135479b1549041906c`.
- Runtime repo status showed an untracked `src/k_geopolitical_monitor.egg-info/`.
- Validation mirror `/tmp/kgm-pr163-validation-AWDJxqb2/repo` HEAD: `f135014e2962907c76ea14bf3b10ddc7c288046c`; it is not the deployment.
- Git initially refused unsafe ownership for reading `/opt`; the audit used an invocation-local `git -c safe.directory=/opt/k-geopolitical-monitor` flag, not a persistent permission change.

## Material drift assessment
**CONFIRMED CODE DRIFT** between the live service checkout and S5-approved research canonical main. A running service does not prove research-only components were deployed or would work with the current runtime. No code synchronization or service restart was attempted.

## Open gates and limits
1. S5.1 must prove crash/failpoint/restart and distinguish pre-replace vs post-replace ambiguity. Power-loss durability and remote exactly-once remain unproven.
2. S5.2 can compare only synthetic local ledgers; no ledger migration, rollback or production writes authorized.
3. S5.3 must be explicit-deny and NO_SEND. A passing offline grant is not live consumer enrollment.
4. S5.4 needs independent exact-head CI/ARM64 results, cross-PR compatibility, stronger runtime source-health/permission review, and final docs sync.
5. Owner decision is required before any production deployment, source activation, remote listener/export, or K-Sentinel/K-Trader connection.

Infrastructure policy: **FREE_ONLY**, no paid providers, no HP-OMEN, no KRC/K-Trader shared infrastructure.

Gate: `P24_1_S5_4_RUNTIME_DRIFT_CONFIRMED_PRODUCTION_OPEN`.
