# P24.4 busy offline runtime and forward-data rollback preparation — 2026-10-19

Decision: **BOUNDED_OFFLINE_PASS_WITH_LIMITATIONS / PRODUCTION_NO_GO**.
Owner authorized the next step: busy isolated runtime qualification and preparation of rollback that preserves new writes. FREE_ONLY / NO_SEND / CLEANUP HOLD. No production switch, restart, restore, deletion, permission change or consumer/source activation is authorized or performed.

Baseline main: `9c97b22f1397d3f0c6039b406d909f2759bba2c1` (PR #236).
Implementation: `src/kgeopolitical_monitor/busy_qualification_p244.py`.
Exact candidate/test SHA, validation and aggregate report: `docs/evidence/P24_4_BUSY_FORWARD_ROLLBACK_2026-10-19.json`.

## Busy workload actually exercised

The pinned October 17 SQLite backup (704512 bytes, SHA256 `4c5c27a1716c706753b8ccda2abeae59982b3e6d5cad8b1eddce154c1bffa8f7`) is read without mutation. All DB changes occur inside an internally created temporary directory. Original owner watches are disabled **only in this disposable copy**; 20 explicitly synthetic watches and one interrupted-run fixture are added.

The actual candidate service builder, parsers, collector, analysis processor and health recorder execute four controlled timestamp rounds. No wall-clock one-minute wait is implied by the controlled timestamps.

| Round | Fixture behavior | Executions | Failed runs | Results |
| --- | --- | ---: | ---: | ---: |
| 0 | Both adapter fixtures usable | 20 | 0 | 20 |
| 1 | GDELT fixture fails; RSS fixture usable | 20 | 0 | 20 |
| 2 | Both fixtures fail | 20 | 20 | 0 |
| 3 | Both fixtures usable again | 20 | 0 | 20 |

Total: 80 executions, 160 in-memory fixture HTTP calls, 60 deliberately injected adapter failures. No fixture delegates to a network transport. A socket audit hook blocks network socket operations; zero socket attempts were observed. Synthetic fixture titles/URLs are not real source evidence and never leave the disposable DB as factual findings.

Every round reconstructs the supervisor over persisted state. A second tick at the same timestamp executes no due watch. One abandoned RUNNING fixture is recovered at the first startup only. Final round persisted retry count is 1 after the prior failed round. This is supervisor reconstruction and controlled interrupted-run state, not a new process-kill or power-loss test.

Resource admission measures due count, serialized watch metadata, free disk and Linux peak RSS before each round; post-tick observation measures remaining due work, peak RSS and actual runtime retry count. Unknown/fixture source state never admits live work. An explicit offline-only path proceeds when hard resource bounds pass. Child-only limits: address space 256 MiB, per-file 16 MiB, 64 descriptors, CPU 30 seconds; outer wall timeout 90 seconds. This is a bounded functional workload, not sustained saturation or a production soak.

## New writes and prior-release compatibility

The busy workload changes 40 tables relative to the original snapshot. After candidate calls return, sqlite3.backup() captures **current committed forward state**, rather than the old baseline. Integrity and FK checks pass. No actual production writer is stopped; quiescence here is the sequential disposable workload returning with no active candidate operation.

A separate clean checkout is pinned to `b31b2136b5fe982d0b63b0135479b1549041906c`. HEAD and tracked/untracked worktree status are checked. It is the historical disk release, not an attestation of code loaded by the active service. Another disposable copy of the forward checkpoint is opened by that release in a separate interpreter, with a cleared credential environment, denied network and bytecode writes disabled. The interpreter/dependency environment is the qualification venv, not an attested production dependency bundle. Actual old service construction and watch listing succeed (23 watches in this captured snapshot plus fixtures). All table-row inventories remain identical before and after legacy initialization/read. Candidate state independently remains identical to the forward checkpoint.

This establishes **prior-code initialization/read compatibility** with these committed candidate changes. It does not establish old-writer semantics, every source/consumer contract, performance, migration reversibility or safe production resumption.

## Rollback gate

`rollback_gate` is a metadata decision function; it performs no switch or restore. It requires explicit quiescence, fresh-current-checkpoint and prior-read compatibility evidence. Missing evidence yields `STOP_KEEP_FORWARD_DB`; satisfied simulated gates yield `CODE_ONLY_KEEP_FORWARD_DB`. Both decisions set:
- baseline_restore_allowed = false;
- production_execution_authorized = false;
- writer_resumption_validated = false.

An incompatible old read attempt is isolated on a sibling copy; it cannot replace or modify the candidate DB or forward checkpoint. A failed compatibility result selects STOP. Final temporary workspace removal discards only the qualification's disposable copies; no claim is made that a production rollback checkpoint was created or retained.

The production preparation procedure is in `docs/implementation/P24_4_FORWARD_DATA_ROLLBACK_PREPARATION_2026-10-19.md`. It is conditional and not a live execution package.

## Remaining gates

Production remains NO-GO: writer-resumption compatibility with forward schema/data; complete dependency/config/unit release package; prospective startup provenance; a fresh cutover backup and actual writer quiescence; preservation of writes committed after any rollback checkpoint; busy production-like duration/volume and saturation; retention reference completeness; live ledger/durability; source/consumer authorization. P23.4 and broader P24.1 remain unchanged. Cleanup remains HOLD independently of these results.


Final qualification: code/test SHA `d43af16b82f6749f7f20405fc8e72070ea9016a3`; full native ARM64 **1693 PASS / 453.86s / exit 0**; GitHub CI #3602 **1693 PASS / 121.61s / SUCCESS**; focused new tests **6 PASS / 4.02s**, state/roadmap invariants **10 PASS**. Real-snapshot busy run: 80 synthetic executions, prior initialization/read PASS with all forward rows preserved, peak qualification RSS 56254464 bytes. Original backup hash/size unchanged; production service remains active. No new automated review is asserted. These results do not authorize production execution or validate old-writer resumption.
