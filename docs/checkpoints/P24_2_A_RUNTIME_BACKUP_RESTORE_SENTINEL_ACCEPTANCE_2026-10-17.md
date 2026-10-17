# P24.2-A — Runtime metadata, consistent backup, isolated restore validation

Date: 2026-10-17  
Status: **SENTINEL VALIDATION PASS / KGM ACCEPTANCE PENDING**

## Scope

P24.2-A established a bounded administrative path for runtime metadata inspection and backup/restore validation on `kgm-e4-owner-pilot` without broadening `kgmops` privileges, without switching the SentinelX slot, and without deploying or restarting the KGM application.

Constraints preserved:

- FREE_ONLY / NO_SEND;
- no broad sudo for `kgmops`;
- `kgmops` not added to group `kgm`;
- no general production-data write access;
- no deployment, live migration, consumer connection, or production restore;
- no production data upload to GitHub.

## Runtime observation

Service:

```text
kgm-monitor.service = active/running
MainPID = 906
User/Group = kgm:kgm
WorkingDirectory = /opt/k-geopolitical-monitor
ExecMainStartTimestamp = Fri 2026-10-16 21:12:30 UTC
```

Process:

```text
cwd = /opt/k-geopolitical-monitor
exe = /usr/bin/python3.12
```

Current checkout on disk:

```text
b31b2136b5fe982d0b63b0135479b1549041906c
```

Worktree:

```text
?? src/k_geopolitical_monitor.egg-info/
```

Important limitation:

```text
loaded_python_release = NOT_ATTESTABLE_RETROSPECTIVELY
```

The checkout SHA is disk state only and MUST NOT be treated as evidence of the Python release already loaded by the running process.

Runtime report:

```text
/var/lib/kgm-p24-export/runtime-report.json
```

The report excludes environment values, raw logs, and process memory.

## Canonical data store

Observed canonical SQLite database:

```text
/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db
```

## Consistent backup

Backup was created through Python `sqlite3.backup()` from a read-only source connection. A normal `cp` of the open database was not used.

Backup:

```text
/var/lib/kgm-p24-export/backup/runtime.db
```

Result:

```text
size_bytes = 704512
sha256 = 4c5c27a1716c706753b8ccda2abeae59982b3e6d5cad8b1eddce154c1bffa8f7
integrity_check = ok
ordinary_cp_used = false
```

Manifest:

```text
/var/lib/kgm-p24-export/backup/manifest.json
```

## Isolated restore validation

Restore target:

```text
/var/lib/kgm-p24-validation/restore-check/kgeopolitical_monitor.db
```

Validation:

```text
integrity_check = ok
size_bytes = 704512
sha256 = 4c5c27a1716c706753b8ccda2abeae59982b3e6d5cad8b1eddce154c1bffa8f7
production_target_touched = false
```

Schema migration history was present and matched for migrations `001` through `021`.

## Bounded access model

Installed fixed helpers:

```text
/usr/local/libexec/kgm-p24-runtime-report
/usr/local/libexec/kgm-p24-backup
/usr/local/libexec/kgm-p24-cleanup
```

Systemd units:

```text
kgm-p24-report.service
kgm-p24-backup.service
kgm-p24-cleanup.service
```

`kgmops` has read-only access to:

```text
/var/lib/kgm-p24-export/runtime-report.json
/var/lib/kgm-p24-export/backup/runtime.db
/var/lib/kgm-p24-export/backup/manifest.json
```

Observed:

```text
READ_OK
WRITE_DENIED
```

The isolated validation area remains root-only:

```text
/var/lib/kgm-p24-validation
VALIDATION_READ_DENIED for kgmops
```

## Owner/admin recovery path

Existing GitHub Actions secrets were confirmed present:

```text
E4_HOST
E4_SSH_PRIVATE_KEY
E4_SSH_KNOWN_HOSTS
```

The owner/admin path is:

```text
GitHub Actions -> ubuntu@kgm-e4-owner-pilot -> sudo -n
```

A bounded workflow was added:

```text
.github/workflows/p24-narrow-admin-install.yml
```

The successful run used main commit:

```text
b1aeb2e404184a35398f212f7659d6e1e5d4f0af
```

The workflow self-stages a fixed package, validates syntax and SHA256, installs only the fixed helpers, verifies `kgm-monitor.service` remains active, and removes only its temporary staging directory.

## Safety result

```text
P24.2-A_DIAGNOSTIC_ACCESS = PASS
P24.2-A_RUNTIME_REPORT = PASS
P24.2-A_CONSISTENT_BACKUP = PASS
P24.2-A_ISOLATED_RESTORE = PASS
PRODUCTION_DB_RESTORE = NO
DEPLOYMENT = NO
LIVE_MIGRATION = NO
CONSUMER_CONNECTION = NO
GITHUB_UPLOAD_OF_PRODUCTION_DATA = NO
SENTINELX_SLOT = UNCHANGED
KGMOPS_GENERAL_SUDO = UNCHANGED
PRODUCTION_SERVICE = ACTIVE
```

## Cleanup status

Cleanup has **not** been executed. Validation artifacts remain available for KGM acceptance.

Deletion order recorded in the manifest:

1. isolated restore DB;
2. backup `runtime.db`;
3. `manifest.json`;
4. `runtime-report.json`;
5. empty validation directory;
6. empty backup directory.

Cleanup must be executed only after KGM acceptance through the fixed `kgm-p24-cleanup.service`.

## Next gate

KGM should:

1. accept or reject P24.2-A evidence;
2. use the runtime report and manifest as the evidence package for the next P24.2 step;
3. explicitly authorize cleanup after acceptance;
4. preserve the limitation that the disk checkout SHA is not runtime loaded-code attestation.
