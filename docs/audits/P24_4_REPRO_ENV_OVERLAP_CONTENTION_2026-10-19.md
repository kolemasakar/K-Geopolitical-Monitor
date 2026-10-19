# Reproducible ARM qualification environment, overlap and contention — 2026-10-19

Decision: **BOUNDED_OFFLINE_PASS_WITH_LIMITATIONS / PRODUCTION_NO_GO**.
Owner authorized steps 1+2: isolated reproducible candidate environment and overlapping-item/concurrent-writer qualification. Baseline main: 10e80c373519cd83681db25aec40fcf663e6b2cd. Exact code/test SHA, aggregate results, wheel identities/hashes and final validation: `docs/evidence/P24_4_REPRO_ENV_OVERLAP_CONTENTION_2026-10-19.json`.

## Complete isolated environment

Created a private ARM64 qualification bundle at `/home/kgmops/kgm-qualification-bundles/p244-20261019-arm64`. It retains 25 downloaded wheels (14507627 bytes), a generated manifest and requirements.lock. Repository lock: `constraints/candidate-linux-aarch64-py312.lock`. Every package is pinned to an exact version and wheel SHA256, including all transitive runtime/test dependencies and pip. `psycopg` and `psycopg-binary` are included at 3.3.6. The helper `wheel_lock_p244` reads a bounded wheelhouse, validates identities and rejects duplicate distribution versions, aliases/non-wheels and excessive files/bytes; it performs no download or installation.

A new venv was created from Python 3.12.3 on Linux aarch64. Installation used only this wheelhouse, `--no-index --require-hashes --force-reinstall`; installed distribution/version mapping exactly equals the manifest; pip check PASS. In a disposable wheelhouse copy a wheel was deliberately altered: pip failed specifically with its hash-mismatch diagnostic. That negative result is not inferred merely from a nonzero exit.

The lock freezes the actual independently qualified ARM environment (for example fastapi 0.147.0, psycopg 3.3.6), rather than silently claiming it equals the older focused x64 CI constraints. Both satisfy the repository's declared ranges; x64 CI remains its own test matrix. This lock is specifically Linux ARM64/CPython 3.12; it is not a cross-platform lock or a byte-for-byte whole-OS image.

Project code and migrations remain a separate pinned Git source-tree input. No project wheel or immutable deployment/release switch is claimed. Full regression runs through PYTHONPATH from the exact code checkout using the rebuilt environment. Source checkout, Python/OS ABI and retained wheel bytes are required to reproduce the qualification; the environment install itself requires no network.

Production service venv was not installed into or modified. The earlier missing-psycopg gap is resolved for the **isolated candidate environment only**. It remains absent in the unchanged service environment; future candidate deployment must switch to the reviewed separate environment, not mutate it as an incidental fix.

## Overlapping items

On a private copy of the accepted real snapshot, 20 candidate watches run four fixture rounds (80 executions). A sibling forward checkpoint is then processed by the clean pinned b31b213 prior source with its actual configured service-venv interpreter. `--overlap` reuses the candidate's item URLs/titles, exercising repeated stable raw-item identities instead of a disjoint namespace.

Prior writer: 80 executions, 60 successful and 20 injected failures, recovery/cadence/retry PASS. Raw item count **5 → 5**; no duplicate raw rows. Forward rows retained under the previously documented policy: fixture-only watch enable changes and three monotonic current-health timestamps; all other committed rows/values protected. Candidate DB and forward checkpoint remain unchanged during prior sibling writes. This covers repeated identical fixture items, not arbitrary changed-content updates under the same identity, every future schema or live source behavior.

## Process concurrency and SQLite contention

All cases use another owned sibling copy; the live service and original exports are not targets.

1. Candidate process acquires its canonical `default_runtime_lease_path(project_root)`. Prior-release process resolves its own canonical lease path for the same project and is denied before its DB write. DB byte hash remains unchanged by that denied contender.
2. Only the disposable holder is killed and reaped. A new prior-release process acquires the released OS lease despite the persistent lock file and commits its probe row.
3. Two disposable processes deliberately bypass the supervisor lease for a database fault case. Candidate holds BEGIN IMMEDIATE with an uncommitted row; prior connection receives exact SQLITE_BUSY under a test-only 100ms busy timeout, rolls back and waits. Uncommitted rows are not visible. Candidate commits; prior retries and commits. Final probe rows are exactly first/resumed/second (3), with integrity/FK checks PASS.

This validates single-supervisor exclusion plus a narrowly controlled SQLite contention/retry case. It does not authorize simultaneous operational supervisors or change the production 5000ms database profile. Child handshake/finish waits are bounded; only owned child processes are terminated and reaped. Socket operations remain denied throughout offline runtime qualification.

## Reproduction

With the exact source checkout, CPython 3.12.3/compatible ARM64 ABI and the retained wheelhouse:

```bash
python3 -m venv /tmp/kgm-qualification-rebuild
/tmp/kgm-qualification-rebuild/bin/python -m pip install \
  --no-index --require-hashes --force-reinstall \
  --find-links /home/kgmops/kgm-qualification-bundles/p244-20261019-arm64/wheelhouse \
  -r constraints/candidate-linux-aarch64-py312.lock
/tmp/kgm-qualification-rebuild/bin/python -m pip check
PYTHONPATH=src /tmp/kgm-qualification-rebuild/bin/python -m pytest -q
```

These commands create an isolated environment; they are not production deployment commands. Hashes prove the selected wheel bytes match the recorded lock, not independent publisher trust. No secret values, production SQLite or raw report/manifest is stored in GitHub.

## Remaining gates

Immutable candidate/prior release packaging and configuration-reference handoff; a reviewed exact switch/reverse-switch package; fresh live writer quiescence and consistent checkpoint; prospective loaded-code provenance; larger-duration/saturation and changed-content scenarios as required by the final acceptance matrix; production retention reference completeness, live ledger/durability and consumer authorization. Phase 23 P23.4 and broader P24.1 remain open. FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO.


Final acceptance on code/test SHA `b693416128a983fdc10ee825b44f0345460a1fa7`: rebuilt hash-locked ARM64 venv full regression **1708 PASS / 462.09s / exit 0**; GitHub CI #3626 **1708 PASS / 119.73s / SUCCESS**. New final overlap/contention/lock tests: **4 PASS / 7.57s**; supporting focused group before final assertions: 21 PASS / 17.89s; state/roadmap invariants 10 PASS. Direct fastapi/uvicorn/psycopg imports and bundled libpq load PASS. Real-snapshot overlap raw count 5→5 and all committed forward rows retained under the controlled policy; canonical cross-release lease and SQLite contention PASS. Source snapshot and actual service-venv metadata hashes unchanged, service active. No new automated review asserted. Isolated environment acceptance does not install dependencies into production or authorize restart, migration, restore, cleanup, concurrent supervisors or writer resumption.
