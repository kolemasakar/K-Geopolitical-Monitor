# P24.4-R1 — Owner-review release manifest and switch/reverse-switch procedure
Date: 2026-10-23. Status: DESIGN_ONLY / PRODUCTION_NO_GO.
Scope: disposable test copies and reviewed instructions, not a deployment authorization.

## Source and evidence anchors

- Canonical repository: `kolemasakar/K-Geopolitical-Monitor`, `main` checkpoint `413bb7e415202a5764d28057c754b8ef2a2539d4`.
- Prior disk checkout: `b31b2136b5fe982d0b63b0135479b1549041906c`; loaded-code provenance cannot be retrospectively inferred from its Git SHA.
- Last full qualified candidate *before this PR*: `b693416128a983fdc10ee825b44f0345460a1fa7`, native ARM64 1708 PASS. This is a historical evidence scope, not this PR's regression outcome.
- First PR #241 source/test SHA: `39251230eab8bd838ff08bc342b4e8c5f48a31fe`.
- Attached existing wheelhouse: `/home/kgmops/kgm-qualification-bundles/p244-20261019-arm64`. 25/25 SHA-256 hashes correspond to `constraints/candidate-linux-aarch64-py312.lock`, total 14,507,627 bytes; Python 3.12.3 Linux aarch64. This is a dependency bundle, **not** an application release artifact.
- 2026-10-23 isolated read/write-free KGM source-switch smoke: same disposable project root, PR #241 candidate → pinned prior `b31b2136` → candidate. All three empty-watch supervisor ticks exit 0; migrations 32 before/after; preserved one probe row, integrity OK and FK violations 0. This is bounded schema/startup compatibility, not full prior-writer resumption.
- Production source path: `/opt/k-geopolitical-monitor`; service `kgm-monitor.service`; Python `/opt/k-geopolitical-monitor/.venv/bin/python`; `--project-root /opt/k-geopolitical-monitor`; DB `/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db`; lock `/opt/k-geopolitical-monitor/data/.kgm-monitor.lock`.
- Service unit references: `/etc/systemd/system/kgm-monitor.service` and `/etc/systemd/system/kgm-monitor.service.d/90-p24-resource-limits.conf`; running service venv unchanged. No raw environment values or secrets are captured.

## Proposed manifest v1 (contract only, not issued)

```json
{
  "format": "KGM_IMMUTABLE_RELEASE_V1",
  "release_id": "<qualified-full-source-sha>",
  "source": {
    "repo": "kolemasakar/K-Geopolitical-Monitor",
    "git_sha": "<qualified-full-source-sha>",
    "source_tree_sha256": "<computed-after-assembly>",
    "migrations_tree_sha256": "<computed-after-assembly>"
  },
  "environment": {
    "platform": "linux-aarch64",
    "python": "3.12.3",
    "requirements_lock_sha256": "9e58c0a81205bdc3b8630e4920884c386906995c1d77bfbe239707692e5e8617",
    "wheelhouse_count": 25,
    "wheelhouse_total_bytes": 14507627,
    "wheelhouse_manifest_sha256": "<measured-after-release-assembly>",
    "installed_packages_sha256": "<measured-after-release-assembly>"
  },
  "config_refs": {
    "unit_path": "/etc/systemd/system/kgm-monitor.service",
    "unit_sha256": "<fresh-pre-cutover-hash>",
    "drop_in_path": "/etc/systemd/system/kgm-monitor.service.d/90-p24-resource-limits.conf",
    "drop_in_sha256": "<fresh-pre-cutover-hash>",
    "persistent_project_root": "/opt/k-geopolitical-monitor",
    "sqlite_path": "/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db",
    "lease_path": "/opt/k-geopolitical-monitor/data/.kgm-monitor.lock"
  },
  "acceptance": {
    "full_arm64_regression": "<pending-exact-release>",
    "old_writer_forward_compatibility": "<pending-full-scope>",
    "owner_production_approval": false
  }
}
```

A placeholder renders the manifest **INVALID FOR DEPLOYMENT**. The exact source, migrations, interpreter, dependency and config file hashes must be measured and agreed for one immutable assembled release. Do not assume `main` equals a tested release or infer loaded-source identity from disk Git HEAD.

## Proposed immutable layout (not created)

```text
/opt/kgm-releases/<release-sha>/source/{src,migrations,pyproject.toml}
/opt/kgm-releases/<release-sha>/.venv/
/opt/kgm-releases/<release-sha>/manifest.json
/var/lib/kgm-release-state/{checkpoints,attestations}/
/opt/k-geopolitical-monitor/data/{kgeopolitical_monitor.db,.kgm-monitor.lock}
```

The service's `WorkingDirectory` and `--project-root` **must remain** `/opt/k-geopolitical-monitor` unless tested shared-root logic replaces this contract. The executable must be the exact pinned release interpreter, and source import location must be pinned to the release's `source/src`, not inherited from old service `.venv` or ambient `PYTHONPATH`. Since default migrations derive from source module `__file__`, verify module imports and the migration tree at startup. The prior writer must resolve exactly the same canonical lock inode/path and DB file; never run both writers in parallel.

## Proposed switch steps — execution prohibited

1. PREPARE: after an exact immutable source + venv build, verify checksums, ownership, read-only source permissions, installed distribution mapping, static service unit and effective drop-ins, and runtime import/migration provenance. Validate artifact under exact systemd hardening and single-writer rules using private disposable DB only.
2. OWNER GATE: separate owner authorization must identify immutable full SHA, manifest, approved systemd modifications, incident response and writer-resumption conditions. No implied approval from PR or CI.
3. QUIESCE: under that future authorization disable replacement supervisor attempts, stop all owned writers, verify the canonical OS lease is free, and verify no unmatched writer handles the DB. If not provable STOP.
4. PRESERVE: create a **fresh current** SQLite `sqlite3.backup()` checkpoint in a protected location, never `cp` an open DB; independently restore the checkpoint into a disposable DB, verify integrity/FK, migrations, row/state inventory and fresh checksum. Protect checkpoint under CLEANUP HOLD.
5. SWITCH: use reviewed unit/drop-in to select pinned release interpreter and source path; preserve `WorkingDirectory` and `--project-root`. Do not mutate the in-use checkout as a pseudo switch. Maintain `NO_SEND`; capture prospective loaded-code/module-path attestation on startup.
6. VALIDATE: assert single lease holder, right DB inode/path, source and migrations from release, configured limits and prohibited sends, and exact committed-row preservation; health/integrity/recovery and no unhandled forward-state differences.
7. RESUME WRITES ONLY IF APPROVED: additional separate full forward-compatibility evidence and owner gate; otherwise keep stopped. No consumers or new sources activated.

## Reverse-switch — CODE_ONLY_KEEP_FORWARD_DB

On failed startup, evidence mismatch or health/forward-state fault: STOP the candidate before any other writer. Retain current committed forward DB, logs/checkpoints and NO_SEND guard. Return code/config/dependencies only to an **independently qualified** pinned prior release under reviewed unit changes and verified single lease; then attest imports, migrations, DB integrity, foreign keys, retained records and compatibility before authorizing writes.

If old writer is not fully forward-compatible, fail closed and keep all writers paused for repair-forward. **Never** restore the 2026-10-17 historical snapshot, a stale checkpoint, or a partial append-only replay over post-cutover writes. No tested full replay journal exists.

## Explicit STOP gates

- Any unknown SHA, unsigned/unverified artifact evidence, dirty content or missing wheel/hash.
- Unexpected import or migration path, missing `psycopg`, incompatible service sandbox permissions, unexpected writes/source/consumer sends.
- Parallel/unaccounted writer, different DB/lease path, missing fresh quiesced checkpoint, integrity/FK mismatch, lost or overwritten forward rows.
- Unqualified old-writer behavior, missing loaded-code attestation, failed runtime health, unknown SQLite schema.
- No owner production approval, or inability to demonstrate cleanup/rollback without data loss.

## Owner review

This document is a reviewable plan and **not** an execution script; it intentionally does not assign unverified privileged commands, switch symlinks, modify the unit, take current production checkpoints, run live migrations, or restart KGM. No release artifact assembled or activated. `FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO`.
