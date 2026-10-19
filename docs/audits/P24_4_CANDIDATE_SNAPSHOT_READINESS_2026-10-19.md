# P24.4 candidate snapshot qualification and readiness — 2026-10-19

Decision: **NO_GO_FOR_PRODUCTION**. The owner authorized steps 1–4 (repository/access reconciliation, isolated real-snapshot compatibility, isolated operational integration and refreshed audit). This supersedes the October 19 work hold only for that scope. FREE_ONLY / NO_SEND / CLEANUP HOLD remain mandatory.

## Evidence and access

Baseline main: `056913b0b1656f2c579910321f8611874585cb8a` (PR #235). Candidate code and test SHA, regression results and captured aggregates are recorded in `docs/evidence/P24_4_CANDIDATE_QUALIFICATION_2026-10-19.json`.

The KGM ARM64 device was online; `kgm-monitor.service` was observed active. All three accepted exports remain readable and not writable by kgmops. Backup: 704512 bytes, SHA256 `4c5c27a1716c706753b8ccda2abeae59982b3e6d5cad8b1eddce154c1bffa8f7`; report SHA256 `7d906d7677a11385c687e827ff4abe569d34ef0dfb0de7c32c84ddd11c43f557`; manifest SHA256 `a3d4a3a79d7717f8ef6c965a7976027f5241a600ccd6e82738352087acde5bcd`. These match prior owner acceptance. No raw report, manifest, SQLite or row values were uploaded. This is still the October 17 captured snapshot, not a new cutover backup.

No fresh loaded-code attestation was attempted. Historical runtime disk SHA `b31b2136b5fe982d0b63b0135479b1549041906c` does not identify the Python code loaded by the active process. No old cleanup helper was run; no claim is made that a replacement helper is installed or accepted.

## Actual candidate integration

`candidate_qualification_p244.qualify()` reads bounded, checksum-pinned single-link regular snapshot bytes (no final symlink following), writes a baseline only inside its own private temporary workspace and starts a disposable candidate child. It accepts no production destination. The child runs the actual candidate database initializer and unattended service builder/run_once, with an explicitly denied HTTP transport and a process-local audit hook denying socket operations. Its environment excludes inherited credentials and Python startup settings. This is isolation for trusted project code, not an OS security sandbox for hostile code.

Real snapshot result:
- integrity and foreign key checks passed before migration, after migration, after the tick and after rollback;
- migration records 21 → 32; tables 51 → 75;
- all pre-existing non-migration table rows/counts preserved at the migration boundary;
- second initialization is idempotent;
- actual candidate supervisor tick succeeds with **zero executions** because no watches are due in the snapshot;
- no real-snapshot HTTP/socket attempts occurred. This is not evidence of successful live acquisition or full busy-runtime compatibility;
- rollback replaces only the disposable DB with the baseline, verifying original inventory and byte-exact SHA. It is not an in-place schema downgrade or a production rollback after new writes.

A separate synthetic-watch integration test executes one real candidate cycle and asserts the denied HTTP transport is exercised. Negative tests cover unknown migration, wrong hash, symlink/hardlink, corrupt/oversized SQLite, queue overflow and child timeout/reaping; input bytes remain unchanged. No synthetic result is represented as production-source evidence.

## Retention, limits and observation

The same offline candidate flow measures due-watch count, serialized watch metadata bytes, actual filesystem free bytes and Linux peak RSS. Retry counter zero describes this qualification invocation (no harness retries); it does not measure all historical source retry state. Missing/unknown sources yield DEGRADED and `admit_work=false`. Only an explicitly offline tick may proceed past source uncertainty when hard resource admission gates pass. Hard resource rejection prevents that tick.

OS limits apply to the disposable child: address space 256 MiB, per-file size 16 MiB, 64 descriptors, CPU 30 seconds; parent wall timeout 60 seconds reaps the child. These are test bounds, separate from the existing service cgroup settings observed below. The existing dedicated resource probes additionally exercise limit enforcement and timeout behavior.

Two bounded metadata-only artifacts derive from the actual tick's aggregate output. Retention planner keeps the current artifact and selects the aged copy under the existing 7-day working test TTL. The execution/restore rehearsal consumes those same output bytes in another internally owned disposable directory: expired copy deleted, protected current copy retained, restoration byte-exact. No production DB row, raw item, ledger or original export is deleted. Aging one output copy is a controlled test fixture; production reference discovery and DB/raw retention adapters remain open.


## Independent read-only reconciliation of parallel runtime work

Draft PR #233 contains hardened cleanup preflight/review material; draft PR #234 contains operational metrics/timer/resource work. Neither branch is merged or activated by this qualification PR. Their claims are distinguished from the following direct observation at `2026-10-19T12:26:08.772438+00:00`:
- active/running, MainPID 906, NRestarts 0;
- systemd MemoryHigh 536870912 (512 MiB), MemoryMax 1073741824 (1 GiB), CPUQuotaPerSecUSec 1s, TasksMax 128;
- effective cgroup v2 memory.high/memory.max match; cpu.max is `100000 100000` (one full CPU);
- MemoryCurrent 16867328, MemoryPeak 17129472 bytes at this sample;
- cpu.stat nr_throttled 0, throttled_usec 0; all memory.events counters zero. This is accumulated low-load observation, not proof under saturation;
- observability service Result=success, ExecMainStatus=0, start `2026-10-19 12:20:01 UTC`; timer active and LastTriggerUSec matches that timestamp.

This supersedes the historical unlimited-service observation only for these current measured knobs. No service setting/restart was changed by this work. One directly inspected timer event does not establish repeated cadence or long-term stability; two independently confirmed scheduled firings and sustained-load qualification remain unaccepted here. Loaded-code provenance is still unknown.

## Production gate matrix

| Gate | Current decision |
| --- | --- |
| P24.2-A diagnostic/backup/restore | Accepted with loaded-code limitation; acceptance retained |
| Captured snapshot vs candidate schema | PASS with limitations: 21→32, 51→75, existing rows preserved, idempotent |
| Offline candidate operational composition | PASS with limitations: resource admission, tick, aggregate observation, output-artifact retention and rollback integrated |
| Busy workload/live source behavior | Not established by the empty real-snapshot tick; synthetic denied-network coverage only |
| Loaded release / deployed-candidate drift | Open; existing process cannot be retrospectively attested |
| Release switch / dependency and configuration package | Open; exact live switch/reverse-switch package not accepted |
| Final backup and writer quiescence | Open; fresh consistent cutover backup and preservation of subsequent writes required |
| Production retention and resource controls | Kernel caps independently observed; saturation/peak-load qualification, raw/DB reference discovery and retention policy remain open |
| Ledger migration / physical power loss | Open; SQLite rehearsal does not close live ledger or physical durability gates |
| External consumers | Not authorized; authentication/enrollment gates and NO_SEND remain |
| Cleanup | HOLD, independently of snapshot acceptance and qualification |
| Phase 23 P23.4 / broad P24.1 | Unchanged and not closed by this work |

Next work requires a bounded plan for release/config/dependency inventory and production rollback preserving writes, busy isolated workloads, retention reference completeness and prospective startup provenance. Any production restart, migration, restore, deployment, source/consumer activation or cleanup remains a separate owner decision. This audit does not request or imply that decision.


Final qualification validation on code/test SHA `eb144822f4452851b6c6162e48c32746b5f226b6`: native ARM64 **1687 PASS / 458.22s / exit 0**; CI #3592 **1687 PASS / 171.26s / SUCCESS**. New focused tests: 6 PASS / 5.33s. Current read-only service observation confirms effective 512 MiB memory.high / 1 GiB memory.max / one CPU / TasksMax 128, zero sampled OOM/throttling counters, active observability timer and one matched successful timer event. Repeated cadence and saturation qualification remain open. Source snapshot hash/size unchanged after qualification; service remains active. These findings supersede historical unlimited-resource observations only for the directly checked current knobs. No production changes by this work.
