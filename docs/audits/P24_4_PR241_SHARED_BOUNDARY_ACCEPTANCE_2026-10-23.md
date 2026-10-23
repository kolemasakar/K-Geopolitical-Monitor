# P24.4 / PR #241 — independent qualification and acceptance review
Date: 2026-10-23. Decision: **BOUNDED_OFFLINE_PASS_WITH_LIMITATIONS / PRODUCTION_NO_GO / KEEP_PR_DRAFT**.

## Reviewed sources

- `tests/test_release_shared_boundary_p244.py` committed at `646314dab6c8ceee79b966b0a71487f382c71dfe`.
- Shared source/root layout design `docs/implementation/P24_4_SHARED_RUNTIME_BOUNDARY_ISOLATED_2026-10-23.md`.
- P24.4-R1 manifest and reviewed switch/reverse-switch contract `docs/implementation/P24_4_R1_RELEASE_MANIFEST_SWITCH_REVERSE_SWITCH_2026-10-23.md`.
- Existing runtime storage, lease, runner, database, migrations and historical qualification evidence on canonical `main`.
- Production unit/drop-in paths only; active production service and data were never modified.

## New measured qualification

- Tested source/test SHA `39251230eab8bd838ff08bc342b4e8c5f48a31fe` (subsequent commits are documentation only).
- Independent `kgm-e4-owner-pilot`, Linux aarch64 / Python 3.12.3, cloned isolated checkout at `/tmp/kgm-p244-pr241-review`.
- Isolated rebuilt environment `/home/kgmops/kgm-qualification-bundles/p244-20261019-arm64/env-rebuilt`, unchanged. Exact 25/25 wheel SHA-256 matching lock and manifest previously reconfirmed, bytes 14507627.
- Targeted suite `tests/test_release_shared_boundary_p244.py tests/test_runtime_lease.py tests/test_runtime_storage.py tests/test_unattended_runner.py`: **13 PASS / 6.09 s / exit 0**.
- Full independent native ARM64 suite: **1710 PASS / 462.35 s / exit 0**.
- GitHub PR #241 CI run `39898785179`: `completed/success` on `39251230e...`.
- GitHub PR #241 CI run `39900347544`: `completed/success` on documentation head `fcf37ed8b18a6991669eb76201eff8c662e00180`.
- Actual pinned historical `b31b2136b5fe982d0b63b0135479b1549041906c` checked out under `/tmp/kgm-p244-pr241-prior`. Manual disposable forward-schema smoke with temporary project root: candidate → pinned prior → candidate, empty-watch `--once` all exit 0; 32 schema_migrations remain 32; extra forward fixture record retained; `PRAGMA integrity_check=ok`, `foreign_key_check=0`. Run used isolated rebuilt Python environment, not production service venv.
- All new tests and smoke use disposable local DBs, not active production DB. No monitoring-source activation, external delivery, live migration, service restart or production writer action.

## Scope limits and review findings

1. The two release-copy test fixtures use **identical current source code**. They validate source-directory isolation and persistent single DB/lease only. They do not simulate real old-vs-new release source differences; separate manual pinned-history empty-watch smoke is recorded above.
2. Prior writer read/startup compatibility on a forward-schema test DB is established for the smoke scope, but full semantics with active watches, changed-content same-ID, saturation, write replay, forward-state preservation and fault/power-loss failure remain unresolved. The previously accepted 80-cycle historical data has limited fixture scope and cannot be promoted to live resumption proof.
3. Manifest is an **unissued JSON contract with placeholders**; source and migration tree, effective unit, interpreter/module import hashes still require future exact artifact assembly and verification. Startup provenance implementation is an observation, not complete loaded-release attestation.
4. No real immutable application release directory, final reviewed systemd switch commands, production snapshot, checkpoint restore, real-layout reverse-switch or owner cutover approval exists.
5. Active `kgm-monitor.service` has `Restart=on-failure` with persistent project-root DB/lease. Stop/restart quiescence and full file access/policy must be independently proven before any future live switch.
6. The latest checkin for this acceptance note will be documentation only. CI success on prior head must not be misrepresented as automatically validating this new docs-only SHA.

## Formal acceptance

- **ACCEPT (bounded)**: proposed shared runtime-root architecture; isolated common lease/DB test; 13 targeted ARM64 PASS; 1710 full native ARM64 PASS; pinned prior empty-watch forward-schema smoke PASS; P24.4-R1 manifest and safety-constrained switch/reverse-switch review document.
- **DO NOT ACCEPT (release/production)**: assembled immutable artifact, actual production switch or reverse-switch, historical prior-writer resumed writes, complete prospective loaded-source attestation, current quiesced production checkpoint, owner production authorization.
- **PR #241 remains Draft and unmerged** pending further full-scope old-writer compatibility, deployable artifact qualification, owner code-merge decision and any later separate production gate.
- Owner baseline strategic state remains `PHASE_23_P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED`; this qualification does not advance broad P24.1, or admit P23.4.
- Safety invariant `FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO` remains binding.
