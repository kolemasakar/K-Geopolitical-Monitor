# KGM handoff — P24.4 bounded offline acceptance, 2026-10-19

Status: WAITING_FOR_OWNER_TRANSITION_GENERATOR. This is a project checkpoint/handoff; the owner will supply the transition generator separately. Do not invent or execute that generator now.

## Canonical anchors

- Baseline main before this documentation freeze: d0261a0ca4569522c63f834b2cf82484d280ce9f (PR #239 MERGED).
- Exact latest code/test qualification SHA: b693416128a983fdc10ee825b44f0345460a1fa7.
- Exact final PR #239 documentation head: 042365630c024785bc31748d70c51b5ac4c2019c; CI #3630 / run 39262861393 SUCCESS, independently rechecked for this freeze.
- Full native ARM64 on the offline rebuilt environment: 1708 PASS, 462.09s, exit 0; code CI #3626: 1708 PASS, 119.73s.
- The subsequent freeze merge SHA must be obtained from GitHub main; do not mistake the pre-freeze anchor for an immutable current-main promise.
- Strategic position remains PHASE_23_P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED. P23.4 and broader P24.1 remain open; Phase24 acceptance is scoped parallel evidence.

## Accepted bounded offline work

- S5 offline acceptance preserved; no production admission inferred.
- P24.2-A diagnostics, consistent historical SQLite backup and independent restore accepted with loaded-code limitation (PR #232).
- Real-snapshot candidate migration/rollback composition accepted: migrations 21→32, tables 51→75, existing rows preserved, idempotency/integrity/FKs and byte-exact private baseline restore (PR #236). That baseline restore is a test only; never apply it after new production writes.
- Busy candidate flow and forward-data rollback preparation (PR #237): 80 synthetic executions; code-only rollback retains the forward DB; old data restore remains prohibited.
- Pinned b31b213 prior writer tested in the actual service venv against a sibling forward DB (PR #238); conditional preservation policy protects rows, with fixture enable flags and three monotonic current-health timestamps as the only test exceptions.
- Reproducible ARM64/CPython3.12 isolated candidate environment (PR #239): 25 exact-version wheel hashes, offline installation exact match, pip check/direct runtime imports PASS; modified wheel rejected by exact hash-mismatch evidence. The actual service venv is unchanged and still lacks the candidate-declared psycopg dependency; the isolated candidate includes psycopg/psycopg-binary 3.3.6.
- Identical overlapping fixture items retained raw count 5→5 and committed forward rows. Cross-release canonical lease denies a second supervisor before DB write, releases after an owned-holder kill; controlled SQLITE_BUSY rollback/retry retains 3 expected commits. This is not concurrent-supervisor authorization.

Primary latest evidence: docs/evidence/P24_4_REPRO_ENV_OVERLAP_CONTENTION_2026-10-19.json.
Audit/rebuild procedure: docs/audits/P24_4_REPRO_ENV_OVERLAP_CONTENTION_2026-10-19.md.
Rollback preparation: docs/implementation/P24_4_FORWARD_DATA_ROLLBACK_PREPARATION_2026-10-19.md.
Lock: constraints/candidate-linux-aarch64-py312.lock.

## Runtime and data boundaries

Last prior observed host: kgm-e4-owner-pilot; service kgm-monitor.service active/running, PID906, kgm:kgm; /opt/k-geopolitical-monitor; configured Python /opt/k-geopolitical-monitor/.venv/bin/python (3.12.3). These are earlier observations, not a fresh runtime check in this freeze. Disk release b31b2136b5fe982d0b63b0135479b1549041906c does not attest loaded Python source: NOT_ATTESTABLE_RETROSPECTIVELY.

Canonical DB: /opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db. kgmops is not granted direct production-data access. Read-only accepted exports: /var/lib/kgm-p24-export/runtime-report.json, /var/lib/kgm-p24-export/backup/runtime.db, /var/lib/kgm-p24-export/backup/manifest.json. Historical Oct17 backup: 704512 bytes; SHA256 4c5c27a1716c706753b8ccda2abeae59982b3e6d5cad8b1eddce154c1bffa8f7. It is not a fresh cutover backup. Original root validation remains separately protected; no cleanup authorized.

Retained qualification bundle: /home/kgmops/kgm-qualification-bundles/p244-20261019-arm64 (wheelhouse, requirements.lock, manifest.json, env-rebuilt). Exact source Git tree/migrations plus CPython/OS ABI are separate inputs. Do not assume a temporary checkout/venv still exists or repeat expensive tests merely because the chat changes. Recheck artifact existence only when needed; preserve known validation unless code/environment changes justify rerun.

## Open work and constraints

- Prepare immutable source/environment/config-reference release artifacts and the exact switch/reverse-switch procedure. No production command package has yet been accepted.
- Fresh live writer quiescence/checkpoint, prospective startup provenance and separate owner production decision remain required.
- Current overlap coverage is bounded identical synthetic items, not changed-content-under-same-ID, saturation, every schema or unlimited simultaneous writers.
- Production retention/reference completeness, live ledger migration/physical-power durability and external consumer authentication/enrollment remain open.
- Draft PR #233 cleanup preflight and #234 observability/resource branch remain unmerged; do not auto-merge, execute cleanup or treat every claim in them as canonical acceptance. Other open research branches are not automatically part of main.
- FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO. No paid services, service restart/deployment, live DB restore/migration, source/consumer activation, permissions expansion, raw reports/SQLite/secrets to GitHub or cross-project infrastructure/slot changes.

## Resume discipline

1. Wait for the owner's generator in this chat; then apply its actual instructions to the verified checkpoint.
2. In the new chat, reconcile main plus docs/handoff/CURRENT_HANDOFF.md, docs/state/CURRENT_PROJECT_STATE.json and ROADMAP.md with this handoff. Preserve the Phase23 strategic pointer and scoped Phase24 evidence.
3. Continue only the owner's authorized offline scope. Planned release/switch preparation does not grant production execution. No new production consent is created by the chat transition.
