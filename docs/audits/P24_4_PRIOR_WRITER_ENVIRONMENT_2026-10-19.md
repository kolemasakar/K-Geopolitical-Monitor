# Prior writer and service environment qualification — 2026-10-19

Status: **BOUNDED_PRIOR_WRITER_PASS_WITH_LIMITATIONS / PRODUCTION_NO_GO**.
Baseline main: e587a201344e2281e7c83a100961e8cca4cab6b9. Owner asked to continue after busy-runtime/read-only rollback preparation. This scope adds isolated old-writer behavior and secret-safe environment/configuration inventory. No production writer, package, unit, restart, restore, cleanup or permission was changed.

Evidence: `docs/evidence/P24_4_PRIOR_WRITER_2026-10-19.json`. Implementation extends the explicit prior-checkout gate with `--prior-writer` and `--prior-python`. Snapshot remains checksum-pinned and private-copy-only.

## Actual old writer qualification

First create 80 synthetic candidate cycles on the accepted real snapshot copy, capturing committed forward state. On a sibling copy run the clean pinned source b31b2136b5fe982d0b63b0135479b1549041906c with `/opt/k-geopolitical-monitor/.venv/bin/python`, Python 3.12.3. The old-source PYTHONPATH precedes installed project metadata; no production project root is passed to the old builder. Credentials are not inherited, bytecode writes are disabled and socket operations are denied. Referencing the installed interpreter/site-packages does not mutate the production release or DB.

The old writer executes four rounds, 20 watches each: usable fixtures, one failed fixture, both failed fixtures, usable fixtures again. Results: 80 executions, 60 successful/20 deliberately failed, one abandoned run recovered, final retry count 1, and no duplicate same-timestamp executions after supervisor reconstruction. Candidate DB and forward checkpoint remain unchanged while the prior writer uses its sibling copy.

Fixture source URLs/titles have a separate namespace for prior writes. This proves a bounded append workload with disjoint new items, not all overlapping-item updates, concurrent writers, sustained load, external side effects or universal old-version compatibility. Both the candidate-created new records and the original real-snapshot rows are checked for retention after old writes.

## Explicit preservation policy

Every pre-existing table and row must remain present with the same values, allowing additional rows. Two narrowly controlled exceptions apply only inside the disposable sibling:
- existing watch `enabled` flags may be cleared to isolate owner/candidate watches from synthetic prior watches;
- three fields in singleton `owner_runtime_health` may advance monotonically: last_supervisor_tick_at, last_completed_tick_at, last_successful_execution_at. A prior nonnull timestamp cannot become null; singleton identity and all other health fields must be retained for this workload.

The initial strict comparison correctly stopped on those three current-health timestamps. They describe the latest service state and advance under any later tick. The accepted forward checkpoint retains their earlier values. No business-row loss, arbitrary update allowance or broad health-table exclusion was introduced. Tests reject deleted/overwritten committed rows, removed watches, backward/null health timestamps and changed instrumentation version. An unexpected schema/row mutation fails closed.

Old-writer fixture compatibility is now separately true. `rollback_gate.writer_resumption_validated` remains false for production: fixtures and observed environment metadata do not provide owner authorization, a fresh live checkpoint, complete overlap/concurrency semantics or a reviewed release switch.

## Actual service configuration inventory

Read-only systemd inspection: active/running, MainPID 906, NRestarts 0; kgm:kgm; working directory /opt/k-geopolitical-monitor. Unit `/etc/systemd/system/kgm-monitor.service`; drop-in `/etc/systemd/system/kgm-monitor.service.d/90-p24-resource-limits.conf`. Their hashes and sizes are in sanitized evidence. ExecStart selects `/opt/k-geopolitical-monitor/.venv/bin/python -m kgeopolitical_monitor.unattended_runner`, with project-root/poll-seconds flag names. No EnvironmentFiles references were returned. Environment values and raw command argument values were not exported. This does not establish absence of every possible secret/configuration input.

Configured limits remain MemoryHigh 512 MiB, MemoryMax 1 GiB, one CPU, TasksMax 128. The configured venv interpreter resolves to the system Python executable seen in the earlier process report; that does not attest the loaded Python source release.

System-Python package NOT_FOUND observations are superseded for **service dependency inventory** by inspection of its actual venv. The service venv reports 24 installed distribution records and passes pip check. The project appears twice in installed metadata; this is recorded without claiming corruption or automatic remediation. Hashing package names/versions is metadata inventory, not a source/wheel integrity lock or retrospective loaded-code proof.

## Candidate dependency gap

Compare the candidate pyproject runtime requirements with actual service-venv metadata:

| Dependency | Candidate requires | Service venv | Result |
| --- | --- | --- | --- |
| Python | >=3.10 | 3.12.3 | Satisfied |
| fastapi | >=0.116,<1 | 0.141.1 | Satisfied |
| uvicorn | >=0.35,<1 | 0.52.4 | Satisfied |
| psycopg | >=3.3,<4 | absent | Open candidate-package gap |

The old SQLite writer working and pip check passing do not satisfy the newer candidate dependency declaration. No package was installed into the live venv. Build/reproduce a separate candidate environment with its complete declared dependencies and reviewed hashes before any future production decision; preserve the prior service environment unchanged for rollback.

## Remaining decision

Production NO-GO remains: overlapping-item and concurrent-state compatibility, reproducible candidate/prior release/dependency bundles, complete secret-reference configuration handoff, immutable switch/reverse-switch package, fresh quiesced live checkpoint, prospective startup provenance, live ledger/durability, retention reference discovery and consumer authorization. FREE_ONLY / NO_SEND / CLEANUP HOLD. Prior S5/P24 acceptances and Phase 23 strategic position remain intact.


Final validation: code/test SHA `c06d0cb95651394b650203731faae81ee8433c40`; native ARM64 **1704 PASS / 462.06s / exit 0**; GitHub CI #3609 **1704 PASS / 131.72s / SUCCESS**; focused writer/preservation tests **17 PASS / 7.31s**, state/roadmap invariants **10 PASS**. Actual pinned prior writer runs 80 synthetic disjoint-item cycles using the service venv; committed forward rows retained with the documented controlled exceptions. Unit, drop-in and installed-package metadata hashes unchanged after checks; original snapshot unchanged; service active. No new automated review asserted. Candidate psycopg dependency, overlap/concurrency and actual production writer resumption remain open. FREE_ONLY / NO_SEND / CLEANUP HOLD / Production NO-GO.
