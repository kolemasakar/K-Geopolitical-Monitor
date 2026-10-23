# P24.4 shared runtime boundary — isolated qualification

Status: DESIGN + TESTS SUBMITTED / PRODUCTION NO-GO.

## Verified source facts

- `RuntimeStoragePolicy(project_root)` resolves data to `<project_root>/data`.
- `default_runtime_lease_path(project_root)` resolves to `<project_root>/data/.kgm-monitor.lock`.
- `unattended_runner` accepts `--project-root`, obtains lease before constructing the service, and uses that same root for `OperationalMonitoringRuntime`.
- `database._default_migrations_dir()` derives migrations from the source module's physical file location, **not** from `project_root`.
- The 2026-10-22 unit points at `/opt/k-geopolitical-monitor/.venv/bin/python`, with working directory and `--project-root` `/opt/k-geopolitical-monitor`.
- The owner-managed production DB is `/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db`.
- Previous accepted candidate qualification: `b693416128a983fdc10ee825b44f0345460a1fa7`, 1708 ARM64 tests PASS, not a production admission.

## Minimal code/data separation — proposal

Keep `--project-root=/opt/k-geopolitical-monitor` for both old and new code. A candidate service **could**, after separately authorized release acceptance, use an interpreter at `/opt/kgm-releases/<qualified-sha>/.venv/bin/python` with source imports explicitly pinned to `/opt/kgm-releases/<qualified-sha>/source/src`. The working directory remains the persistent runtime root. Do not edit the existing unit or its data directory in this qualification.

A separate immutable source directory contains `src/`, `migrations/`, verified application metadata, and a locked release-specific environment. Validate module `__file__` and migration source path at startup; an import fallback to old source is a STOP. Evaluate systemd `ProtectHome`, `ProtectSystem=strict`, `ReadWritePaths`, permissions and `PYTHONPATH` under the exact proposed unit before deployment. Never embed configuration or secret values in the release manifest.

The release's code and dependency bytes are pinned; the persistent data and lease are intentionally outside the immutable source. No symlink flip or live release switch is implemented by this PR.

## Targeted isolated tests

`tests/test_release_shared_boundary_p244.py` copies current source and migrations into two disposable release directories. With the same temporary `--project-root`, it validates:
1. old → new → old `--once` runner executions preserve a forward fixture row in one DB, plus SQLite integrity and foreign-key checks;
2. lock held by the parent rejects both release invocations before DB initialization, and the next invocation succeeds after release.

The two copies are the **same current code**, not an independently qualified historical old writer or a production switch. They test path isolation, not complete forward-schema compatibility, write replay, power-loss durability or loaded-code attestation. They execute only on a temporary DB with no configured watches (no live network requests).

## Remaining release gates

1. Targeted tests and full CI, then independent native ARM64 regression on exact branch SHA.
2. Exact historical old-writer → forward-schema interoperability on disposable sibling DB with complete preservation comparison.
3. Source/import/migration startup attestation and evaluated immutable manifest.
4. Reviewed exact systemd switch and reverse-switch actions; service remains unmodified.
5. Fresh quiesced backup + restore qualification and owner production approval.
6. Never downgrade the live DB; code-only rollback must retain current forward data, else STOP.

`FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO`. No production write, restart, migration, snapshot cleanup or consumer activation is authorized.
