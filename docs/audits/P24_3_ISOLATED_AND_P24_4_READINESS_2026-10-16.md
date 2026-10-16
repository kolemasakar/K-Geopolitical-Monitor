# P24.3 isolated acceptance and P24.4 readiness audit — 2026-10-16

Status: IMPLEMENTATION_VALIDATION_PENDING / P24_4_PRODUCTION_NO_GO.
Owner request: execute steps 1–6, FREE_ONLY / NO_SEND; no production activation authorized.
Base: a15fa89edfd851a42fe5289b9321770c5386b2d8.

## 1. Administrative diagnostic gate
Fresh existing-rights probe at 2026-10-16T13:48:04Z: kgm-monitor.service active, PID 208487, deployed checkout b31b2136b5fe982d0b63b0135479b1549041906c. Process cwd/exe inaccessible. Administrative execution is unavailable, not silently substituted with an elevated path. No new sudo/group/polkit rights installed. P24.2-A stays PARTIAL. Even an administrator's current disk SHA cannot retrospectively prove all loaded Python code matches it.

## 2. Retention working policy and isolated execution
Working test policy (NOT a production deletion authorization):
| Type | Test TTL | Protection |
| --- | --- | --- |
| raw | 30 days | explicit protected references retained |
| observation | 90 days | explicit protected references retained |
| artifact | 7 days | explicit protected references retained |
| trace | 14 days | explicit protected references retained |
| ledger, replay_required, evidence | indefinite | no TTL deletion |

retention_rehearsal_p243 accepts validated in-memory records only. It cannot accept a production root. Internal TemporaryDirectory holds disposable copies, executes expiration, restores original bytes and checks exact equality. IDs cannot traverse paths, duplicates/unknown kinds/unresolved supplied references/future timestamps are rejected. Default 100 records/1 MiB, absolute ceiling 1000 records/8 MiB. Input memory is caller-owned; limits prevent materializing oversized fixture sets, not allocation before the API call.
Source record references must be supplied completely by the caller. No claim is made that production reference discovery, DB retention, transaction rollback or live replay retention floors are implemented. The existing dry-run planner retains its own keep-last policy and is not auto-wired to this rehearsal.

## 3. Resource controls
resource_probe_p243 uses real POSIX rlimits in disposable child processes: address space 96 MiB, file size 1 KiB, descriptors 32, CPU 1 second; parent timeout reaps the child. These are test limits, NOT deployment settings.
Proposed resource admission defaults: queue depth 100, queue bytes 1 MiB, disk reserve 1 GiB, RSS 256 MiB, retries 3. Thresholds are working offline defaults requiring operational calibration.
Fresh host metadata: 5903 MiB total RAM, 5059 MiB available, zero swap in use; filesystem 47,321,268,224 bytes total and 35,058,089,984 available. Snapshot only, not a capacity guarantee.
Active systemd settings and OS quotas were not changed. Cgroup enforcement of the KGM service and real queue integration remain production-readiness work.

## 4. Closed-schema observability
resource_observation_p243 reports numeric counters, enumerated admission reasons and aggregate source-state counts. Empty/UNKNOWN/degraded source sets never produce HEALTHY/admit-work. Queue, disk, memory and retry breaches block admission. No titles, raw logs, identities, environment, cookies, keys or free-text error messages accepted/output.
Caller-supplied counters are validated observations, not independent runtime measurements. No active collector, remote alert, listener or send enabled.

## 5. Validation
Focused native ARM64: 24 PASS in 1.25s. Full exact-head native ARM64, CI and review required before offline acceptance. Final evidence appended after actual completion.
Code scope is isolated retention/resource/observability qualification. P24.3 production readiness stays OPEN even if these tests pass.

## 6. P24.4 strategic audit / deployment and rollback gate
Decision: NO_GO_FOR_PRODUCTION / OWNER_DECISION_NOT_REQUESTED_YET.
| Gate | Evidence / gap |
| --- | --- |
| Research S5 | accepted offline with limitations |
| P24.2 recovery | accepted offline; runtime inventory partial |
| P24.3 | isolated working implementations; full acceptance pending, production data adapters/OS integration unverified |
| Deployed SHA drift | unresolved; startup attestation prepared but inactive |
| Ledger migration | synthetic rehearsal passed; live writer quiescence/reference completeness/backup restore unproven |
| Durability | SIGKILL/fsync error tests; physical power-loss guarantee unproven |
| External consumers | authentication/enrollment not accepted; NO_SEND |
| Legacy P23.4 / broad P24.1 | not closed by this work |

Concrete controlled sequence before a deployment request:
1. An authorized administrator runs the fixed metadata probe under the narrow approved mechanism; record process links, unit identity and checkout SHA without secrets. Record unknown loaded state explicitly.
2. Pin candidate merge SHA and current prior SHA b31b2136b5fe982d0b63b0135479b1549041906c. Inventory actual unit/config/dependencies and data paths. Identify which state can be restored without losing subsequent writes.
3. Create a checksum-bound backup under an owner-approved accessible destination; restore it to isolated storage, run DB integrity, ledger record/digest/reference checks and candidate/prior-release smoke tests with NO_SEND. No destination/path is fabricated as already available.
4. Prepare the exact unit/release switch and reverse switch against the real backup/paths, including dependencies. If immutable-release layout or data compatibility is not proven, STOP; do not copy research main over the active checkout.
5. Present the exact candidate, commands, backup manifest, restored test result and remaining risk for the separate owner go/no-go. No restart or data migration before that decision.
6. On a separately authorized change, quiesce writers, capture final backup, perform the reviewed switch and opt-in startup observation. Abort on integrity mismatch, unknown release, exceeded resource bounds, unexpected source/send or failed health checks.
7. Roll back using the tested prior release/unit/environment and the rehearsed compatible data restore procedure. Verify integrity, replay continuity, source state and NO_SEND before resuming. A rollback that discards unbacked writes is prohibited.

This is an executable-deployment preparation checklist, not a deploy-ready command package: actual privileged inspection, backup location and restore evidence are missing. No new production permission is inferred from the audit.
