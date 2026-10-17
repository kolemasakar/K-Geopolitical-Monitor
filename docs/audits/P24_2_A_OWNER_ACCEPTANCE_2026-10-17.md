# P24.2-A owner acceptance — 2026-10-17

Decision: PASS_WITH_LOADED_CODE_LIMITATION for diagnostic access, runtime-report metadata, consistent backup and isolated restoration of the captured snapshot.
Baseline main: 51cd03de910ebff5d25dd13278889f3f5a1a0fd1.
Evidence: docs/evidence/P24_2_A_OWNER_ACCEPTANCE_2026-10-17.json.
No production DB or raw report/manifest is uploaded to GitHub; only sanitized acceptance metadata and checksums.

## Direct owner checks
- Read runtime-report.json and backup/manifest.json through the narrow export access.
- All three exports readable, not writable by kgmops; root validation copy remains unreadable.
- Backup size 704512 bytes, SHA256 4c5c27a1716c706753b8ccda2abeae59982b3e6d5cad8b1eddce154c1bffa8f7, matches manifest.
- Read-only immutable SQLite inspection: integrity_check ok, foreign_key_check zero violations, 51 tables, 21 migration records exactly matching manifest.
- Independently restored this backup via sqlite3.backup() into an owner-created temporary directory. Integrity, all table row counts and migration records match; restored SHA256 equals backup SHA256.
- Temporary owner restore removed automatically. Original export/admin validation artifacts untouched.
- Root-only administrator restore result is manifest-attested, NOT directly inspected by the owner process.

## Runtime and historical scope
Administrator report timestamp 2026-10-17T00:55:41.800371+00:00; PID 906, active/running, kgm:kgm, cwd /opt/k-geopolitical-monitor, executable /usr/bin/python3.12.
Disk checkout b31b2136b5fe982d0b63b0135479b1549041906c with untracked egg-info remains distinct from research main.
Loaded Python release remains NOT_ATTESTABLE_RETROSPECTIVELY. Effective live source selection is not attested by this report. This acceptance does not infer loaded release identity or source coverage.
The snapshot captured at 2026-10-17T00:55:49.749478+00:00 is verified historical evidence, NOT a fresh pre-cutover backup or evidence of candidate schema/migration compatibility.

## Cleanup disposition
Cleanup HOLD. Acceptance of this snapshot does NOT authorize the existing ops/p24_diag/kgm-p24-cleanup helper. Reviewed baseline helper uses unchecked rm -f and ignores rmdir errors, so it can report PASS without the promised preflight/post-state guarantees. No cleanup was run. After a hardened helper or separately approved verified administrative procedure is reviewed, the only permitted deletion targets/order are:
1. /var/lib/kgm-p24-validation/restore-check/kgeopolitical_monitor.db
2. /var/lib/kgm-p24-export/backup/runtime.db
3. /var/lib/kgm-p24-export/backup/manifest.json
4. /var/lib/kgm-p24-export/runtime-report.json
5. /var/lib/kgm-p24-validation/restore-check
6. /var/lib/kgm-p24-export/backup

Abort on unexpected path/type/content or nonempty directories; no recursive wildcard deletion and no production target. Before any deletion, an authorized administrator must validate ALL targets: exact fixed paths, root-owned nonsymlink regular files with single links, root-owned nonsymlink parent directories, exact directory contents with no extras, report and manifest hashes pinned to the owner evidence and both DB hashes/sizes matching the accepted snapshot. Complete every preflight check before mutation; abort unchanged on any mismatch. Cleanup must propagate unlink/rmdir errors, verify all six targets absent, confirm production service remains active, and emit PASS only after post-state proof. No ignored rmdir errors or recursive wildcard deletion. The existing helper must not be executed for this disposition. Preserve acceptance evidence independently before cleanup; report actual execution separately. Current evidence does not claim deletion.
A new consistent backup and isolated restore proof must be captured before any later authorized cutover.

## Remaining gates
P24.2-A accepted in the bounded diagnostic/backup scope; P24.2 overall retains known limitations.
P24.4 production NO-GO preserved: deployed/candidate drift, startup provenance, candidate-vs-real-data compatibility and rollback, production retention/resource/observability integration, live ledger migration and external consumer authorization remain separate gates.
FREE_ONLY / NO_SEND. No owner-acceptance service restart, production restore, deployment, source activation, consumer connection or rights expansion.
