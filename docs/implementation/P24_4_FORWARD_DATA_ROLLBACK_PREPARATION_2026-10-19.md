# Forward-data-preserving rollback preparation — 2026-10-19

Status: **PREPARED_WITH_OPEN_GATES / NOT_AUTHORIZED_FOR_PRODUCTION_EXECUTION**.
FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO.

## Fixed known scope

- Host: kgm-e4-owner-pilot; unit: kgm-monitor.service; production working directory: /opt/k-geopolitical-monitor.
- Canonical production DB path: /opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db.
- Prior disk release: b31b2136b5fe982d0b63b0135479b1549041906c, separately tested initialization/read against a forward-schema disposable copy. It is not a retrospectively attested loaded release.
- Qualified historical snapshot: October 17; it is NOT a current rollback target after new writes.
- Candidate SHA and results are in docs/evidence/P24_4_BUSY_FORWARD_ROLLBACK_2026-10-19.json. A future deployment must pin its own exact reviewed merge/release SHA; do not silently substitute moving main.
- No production rollback directory, immutable release layout, final privileged command set, service switch or write-resumption permission has been accepted. Do not invent those as available.

## Selected data strategy

Prefer rollback of code/config/dependencies **while retaining the current committed forward DB**. Candidate migrations are additive for the tested snapshot, and prior initialization/read passed, but old writer behavior must be qualified before this becomes a deployable strategy. Capture a fresh current checkpoint after writer quiescence before any future authorized code switch.

Never restore the October 17 snapshot over a DB that has subsequently accepted writes. A frozen pre-cutover or pre-rollback checkpoint is also stale once further writes resume. The tested gate never permits baseline restore.

If prior writers are incompatible with forward data, STOP: retain current code/data in a controlled NO_SEND/paused state according to a separately approved incident procedure, retain the fresh current checkpoint, and repair forward. A data downgrade or replay path requires a separately tested complete change journal covering inserts, updates and deletes, foreign keys, provenance and all new tables. No complete journal exists in this implementation; partial table export or append-only replay is not an acceptable substitute.

## Required sequence before a future owner decision

1. Inventory the exact current unit/drop-ins, interpreter/dependencies, configuration references and permissions through narrow secret-safe diagnostics. Bind candidate and prior bundles to immutable artifacts. Keep configuration/secret VALUES out of GitHub. Test prior writers against the forward-schema copy, including retry, recovery, duplicate suppression and all retained new-state classes. Stop on any loss or semantic incompatibility.
2. Present a concrete switch/reverse-switch package for the actual release layout, with reviewed commands, exact SHAs, dependency/config references, storage locations and permission boundaries. The current in-place checkout is not an immutable release switch mechanism. Do not run git checkout over the active process and call that loaded-code proof.
3. Obtain a separate owner production decision covering the exact switch and any required controlled pause/restart. This qualification does not provide that decision.
4. Under that separate authorization, stop/quiesce every writer and verify no replacement writer is active. Capture a fresh sqlite3.backup() checkpoint of **current** committed state in an approved protected location; record manifest/checksum and verify isolated restore plus latest committed-state inventory. If writers cannot be proven quiescent, STOP without replacing code/data.
5. Re-evaluate prior compatibility on this latest checkpoint. Use CODE_ONLY_KEEP_FORWARD_DB only with the previously accepted writer compatibility, current evidence, and owner-approved switch. Keep the forward DB; do not copy an old baseline over it. Record actual service startup provenance and preserve NO_SEND throughout.
6. Before resuming writes, validate integrity/FKs, latest committed-state preservation, migration set, retry/replay continuity, resource health and expected source/consumer policy. Until old-writer semantics and a fresh checkpoint are accepted, writer_resumption_validated remains false and work stays stopped under the approved incident procedure.
7. If the switch/read/health check fails, STOP with forward DB and checkpoint retained. Do not retry a destructive restore. Any additional restore or replay needs a complete, tested no-loss procedure and a separate owner decision. Subsequent checkpoint cleanup remains independently on HOLD.

## Abort criteria

Unknown/moving release or dirty prior bundle; non-attested configuration; active/unaccounted writer; stale or mismatched checkpoint; integrity/FK failure; changed/lost committed rows; old-writer incompatibility; unrecognized new schema/state; missed replay history; unexpected source/send; exceeded resource bounds; failed startup/health/provenance. None authorizes fallback to the old snapshot.

## What has actually been tested

On an isolated snapshot copy: 80 synthetic candidate cycles, success/partial/total-failure/recovery, persisted cadence after supervisor reconstruction, interrupted-run recovery, current-state consistent checkpoint, prior b31b213 initialization/read on a sibling copy, and exact row-inventory preservation. Production was not stopped, switched, restored or written by this work. The remaining production steps above are requirements, not claimed executions.


Final qualification: code/test SHA `d43af16b82f6749f7f20405fc8e72070ea9016a3`; full native ARM64 **1693 PASS / 453.86s / exit 0**; GitHub CI #3602 **1693 PASS / 121.61s / SUCCESS**; focused new tests **6 PASS / 4.02s**, state/roadmap invariants **10 PASS**. Real-snapshot busy run: 80 synthetic executions, prior initialization/read PASS with all forward rows preserved, peak qualification RSS 56254464 bytes. Original backup hash/size unchanged; production service remains active. No new automated review is asserted. These results do not authorize production execution or validate old-writer resumption.


## Prior writer and actual service environment — 2026-10-19

Owner-authorized continuation: pinned b31b213 prior writer executed 80 synthetic disjoint-item cycles on a sibling forward-DB copy using the actual service venv Python (60 success, 20 expected failures, recovery/retry/cadence PASS). Committed rows retained under an explicit policy: fixture-only watch enable changes and three monotonic current-health timestamps; other overwritten/deleted rows rejected. Production writer resumption remains unvalidated. Actual ExecStart selects `/opt/k-geopolitical-monitor/.venv/bin/python`; system-Python NOT_FOUND is not service package evidence. Actual venv pip check PASS, but candidate pyproject requires missing psycopg>=3.3,<4. No installation or production mutation. Sanitized unit/drop-in/package metadata, exact validation and limitations: `docs/evidence/P24_4_PRIOR_WRITER_2026-10-19.json`; audit: `docs/audits/P24_4_PRIOR_WRITER_ENVIRONMENT_2026-10-19.md`. FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO; Phase 23 position unchanged. State synchronization v4.70.


Final validation: code/test SHA `c06d0cb95651394b650203731faae81ee8433c40`; native ARM64 **1704 PASS / 462.06s / exit 0**; GitHub CI #3609 **1704 PASS / 131.72s / SUCCESS**; focused writer/preservation tests **17 PASS / 7.31s**, state/roadmap invariants **10 PASS**. Actual pinned prior writer runs 80 synthetic disjoint-item cycles using the service venv; committed forward rows retained with the documented controlled exceptions. Unit, drop-in and installed-package metadata hashes unchanged after checks; original snapshot unchanged; service active. No new automated review asserted. Candidate psycopg dependency, overlap/concurrency and actual production writer resumption remain open. FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO.
