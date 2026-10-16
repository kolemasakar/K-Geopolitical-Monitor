# P24.3 observability entry — 2026-10-16

Status: ENTRY_OFFLINE_PASS_WITH_KNOWN_LIMITATIONS / NO_SEND.

## P24.2-A diagnostic follow-up
The fixed read-only script scripts/p24_runtime_metadata_probe.py reads only allowlisted systemd properties, checkout SHA and process cwd/exe links. It reads no environment values, credentials, raw logs or process memory. Run under existing rights succeeded on 2026-10-16T13:31:34Z: PID 208487 active, checkout b31b2136b5fe982d0b63b0135479b1549041906c; cwd/exe UNAVAILABLE. No elevated administrative execution was available. P24.2-A remains PARTIAL. The script is prepared for an authorized narrow diagnostic mechanism; no sudo rule or helper installation was performed.

## Prepared startup attestation
Optional --startup-attestation emits one secret-free JSON observation after actual adapter construction. Default is off; active unit is untouched. It records checkout SHA at startup, Python version, actual adapter source IDs and fingerprints of the loaded adapter fetch code objects. A checkout SHA is disk-at-startup evidence, not proof all loaded dependencies match a release; marshal fingerprints are Python-version-specific. This cannot retrospectively attest PID 208487. Do not restart or modify the active service to collect it without separate authorization. Tests use synthetic runtime construction and no provider calls.

## P24.3 entry: guarded retention planning
retention_plan_p243.plan is metadata-only, nonrecursive and capped at 1000 entries by default (maximum 10000); exceeding the cap fails without a partial deletion plan. It only considers artifact-*.json, preserves at least keep_last=1 newest artifact, rejects aliases, and reports retained/eligible byte totals. No deletion API is provided. It does not cover live DB/ledger retention, recursive totals, OS resource enforcement or production health. Dry-run tests prove originals and ledger files remain unchanged.

Focused ARM64 tests: 14 PASS, 3.18s. Exact-head full regression/CI pending before code acceptance. P24.3 broader retention execution/resource controls/observability remains IN_PROGRESS. FREE_ONLY / NO_SEND; no runtime deployment, new source activation, live deletion, credentials, external consumers or paid/shared infrastructure.


## P24.3 entry acceptance — 2026-10-16

PR #230 code `64293ae420b34329c4d8b8531874a036f5922ea7`: native ARM64 **1652 PASS / 457.95s / exit 0**, focused **14 PASS / 3.18s**. GitHub CI #3457 **1652 PASS / 98.32s** and Backup Restore Rollback #34 SUCCESS. Supersedes earlier pending entry wording. Evidence: `docs/evidence/P24_3_ENTRY_ACCEPTANCE_2026-10-16.json`.

P24.2-A remains PARTIAL: fixed probe executed under kgmops, no elevated/admin execution; historical loaded release cannot be retrospectively established. Prepared --startup-attestation is off by default and has not been activated on the service. Loaded-code marshal fingerprints depend on Python version and compile filename/path, and are observations, not reproducible whole-release identity. No full P24.3 closure: live retention/DB cleanup, OS-level resource enforcement and comprehensive production observability remain future work. No deployed code change, restart, deletion, source activation, consumer enrollment or send. FREE_ONLY / NO_SEND preserved.
