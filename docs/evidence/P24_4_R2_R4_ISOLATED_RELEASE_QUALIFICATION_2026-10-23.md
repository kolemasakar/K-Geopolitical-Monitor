# P24.4 R2-R4 — 2026-10-23 bounded offline qualification

Decision: **ISOLATED_BUILD_AND_SWITCH_PASS_WITH_LIMITATIONS / PRODUCTION_NO_GO**.

## Exact scope and source

- Repository: `kolemasakar/K-Geopolitical-Monitor`; PR #241 source/test code at `39251230eab8bd838ff08bc342b4e8c5f48a31fe`. Subsequent PR #241 commits are docs only.
- Baseline old checkout: `b31b2136b5fe982d0b63b0135479b1549041906c`.
- Host: `kgm-e4-owner-pilot` (Linux `aarch64`, Python 3.12.3). All tests used `/tmp` disposable private sibling databases, NOT service database. NO_SEND enforced for active-watch subprocess by denying socket and urllib connections before importing the runner.
- Dependency wheel bundle: `/home/kgmops/kgm-qualification-bundles/p244-20261019-arm64`, original read-only 25-wheel lock, total 14,507,627 bytes.

## R2 — old writer with active watch (bounded)

On a disposable candidate-initialized schema (75 tables, 32 migrations), inserted one enabled synthetic watch and one historical COMPLETED monitoring run. Executed pinned historical writer once with outbound access forcibly denied. Result: subprocess exit 0, one execution reported source failure `OFFLINE_DENIED`, watch retained, historic COMPLETED record retained, monitoring_runs count 2, PRAGMA integrity_check `ok`. This is a **network-failure watch-path compatibility smoke**, not successful source-ingestion/replay, multi-watch stress or full live writer admission.

## R3 — offline isolated release build

Built at `/tmp/kgm-p244-release-39251230`, NOT in production release directories. Inputs copied from the pinned code commit: `src`, `migrations`, `pyproject.toml`. New CPython3.12 venv built using `python3 -m venv --copies`, then hash-enforced offline pip install with `--no-index --find-links <retained-wheelhouse>/wheelhouse --require-hashes -r requirements.lock`. Exit 0; `pip check` exit 0. Generated `manifest.json` (mode `ISOLATED_OFFLINE_ONLY`, production_approved=false) with:
- Source SHA: `39251230eab8bd838ff08bc342b4e8c5f48a31fe`.
- Source tree SHA256: `0597080f6a478c3340cfa47b21f6f500594e1b4723c3cf2d7cbf6d1eaabaff3a` (349 source files).
- Migrations tree SHA256: `df75d87f824ddc656a968a986cfe732c67f3da660eda7d1c7c02862e3fe03d5f` (32 migration files).
- requirements.lock SHA256: `9e58c0a81205bdc3b8630e4920884c386906995c1d77bfbe239707692e5e8617`.
- 25 matched wheels; platform linux-aarch64; Python 3.12.3.
- Hash algorithm for both trees: for each sorted regular file recursively, pair its POSIX relative path with the file's SHA256 hex; JSON-encode the ordered list with separators `(',',':')`, UTF-8; take SHA256 of resulting bytes.

A `/tmp` qualification artifact is not a persistent, write-protected, fully deployment-attested or signed immutable application release. An exact release needs authoritative assembly scripts, package verification under target service hardening, installed-package digest, source/config provenance, and operational owner gate.

## R4 — executable-source switch/reverse-switch simulation

Using the newly built isolated venv, one disposable `project_root` and its sole DB/lease:
1. Candidate source `/tmp/kgm-p244-release-39251230/source` `--once` exit 0.
2. Inserted one enabled offline synthetic watch, one historical COMPLETED run and one `forward_preserve_probe` row.
3. Invoked pinned prior source `/tmp/kgm-p244-pr241-prior` with blocked network; one failed source collection path executed without uncaught failure.
4. Invoked candidate source again with same root; exit 0.
5. Confirmed source modules and migrations resolve strictly under the selected source tree; 32 migrations, two monitoring_runs, preserved marker; `integrity_check=ok`, `foreign_key_check=0`. Result `ISOLATED_SWITCH_REVERSE_SMOKE_PASS`.

This is **not** a test of systemd actual unit override, Privileged production switch, live-DB quiescence, power loss, or full in-flight replay. Actual service remains untouched.

## Existing full-regression evidence from PR #241

- 13 targeted ARM64 tests PASS / 6.09s / exit 0.
- Full 1710 ARM64 tests PASS / 462.35s / exit 0 on code SHA `39251230...`.
- GitHub CI #39898785179, #39900347544 and #39900880897 all `completed/success` for code/then documentation checkpoints. These do NOT automatically attest a future new code SHA.

## Remaining release and merge acceptance gates

- Full differential old/new writer tests with multiple active watches, actual meaningful insert/update/delete, same-ID changed content, retry/recovery, saturation, concurrent ownership, crash/kill and data invariants.
- Reproducible persistent artifact automation including full release provenance and exact final source SHA with no moving refs or unverified placeholders.
- Systemd sandbox mirror/restart suppression, one-writer quiescence, consistent fresh sqlite3 backup + independently verified restore on disposable copy, cutover and reverse-cutover test.
- Formal code review and branch/main state decision after test coverage, then a separate owner production authorization.

**Do not promote** this note to production permission or an assertion of the above open tests. Keep `FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO`.
