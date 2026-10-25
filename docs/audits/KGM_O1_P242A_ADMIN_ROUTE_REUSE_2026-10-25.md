# KGM O1 — established P24.2-A admin route and safe live-probe decision (2026-10-25)

## Ground truth

The prior Oct17 P24.2-A administrator acceptance is recorded in `docs/checkpoints/P24_2_A_RUNTIME_BACKUP_RESTORE_SENTINEL_ACCEPTANCE_2026-10-17.md`. Privileged path is GitHub Actions with pinned SSH access to `ubuntu@kgm-e4-owner-pilot`, then bounded `sudo -n`; workflow `.github/workflows/p24-narrow-admin-install.yml`. OCI Run Command instead runs as `ocarun`, member of `adm`, with no sudo or access to the protected database.

Direct read-only host inventory on Oct25 verified:
- `/usr/local/libexec/kgm-p24-runtime-report`, `kgm-p24-backup`, and `kgm-p24-cleanup` exist, root-owned executable;
- `kgm-p24-report.service` and `kgm-p24-backup.service` are installed/loaded but inactive one-shot units;
- Runtime report writes via `os.replace` to the Oct17 `/var/lib/kgm-p24-export/runtime-report.json`;
- Backup script refuses to run while `/var/lib/kgm-p24-export/backup` exists; it is NOT a reusable fresh snapshot command without separately reviewed output isolation;
- Cleanup script is prohibited by CLEANUP_HOLD.

Thus neither existing P24.2-A helper should be re-run for O1. Do not modify/deploy the original service or overwrite any historical acceptance artifacts.

## Proposed next authorized execution

Review and install **a distinct, fixed, one-shot, summary-only read-only probe** via the previously approved admin channel; do not grant `ocarun` or `kgmops` more permissions.

Required controls:
1. Pin code, command arguments and exact host; verify workflow and hashes before dispatch. Reject arbitrary shell/user command injection.
2. No raw DB upload, journal payload, process environment or secrets. Output only DB integrity verdict, bounded schema/table counts, migration count, and well-defined worker-cycle aggregates with column/table provenance. Do not mistake catalog timestamps for cycles.
3. Open canonical DB using SQLite `mode=ro` and `PRAGMA query_only=ON`. Explicitly capture SQLite errors, busy timeouts and WAL caveats; never report PASS on a skipped check. If using SQLite online backup for snapshot consistency, write to a distinct secure temporary location only, with fixed noncollision path, retention/cleanup separately approved.
4. Cross-check timestamp range, service PID/start, source freshness, latest successful and failed cycle totals, and actual process-code provenance independently. Disk HEAD alone is not a loaded-code attestation.
5. Keep Oct17 exports untouched; production service, permissions and configuration unchanged; FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.

Current O1 gate: PARTIAL. Validated historical backup integrity and systemd journal access do NOT validate current worker-cycle health, current SQLite integrity, current source freshness or loaded-code identity.

## GitHub evidence

PR #255 merged after CI SUCCESS; merge commit `e2a4d62be577f31daad7d566bae7f4254915f490`. The present change is documentation-only, not a live probe or administrative invocation.
