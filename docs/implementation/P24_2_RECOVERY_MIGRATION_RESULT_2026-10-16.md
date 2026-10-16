# P24.2 isolated reliability/recovery implementation — 2026-10-16

Status: IMPLEMENTED / ACCEPTANCE_PENDING. FREE_ONLY / NO_SEND.
Base: 45e08fa150b48436c5c004d6a2ec37cf74ada02f. Native ARM64 worktree: /tmp/kgm-p242-work.
Authorization: owner requested P24.2-A through E; production activation remains excluded.

## A — fresh runtime inventory

Evidence: docs/evidence/P24_2_A_RUNTIME_MANIFEST_2026-10-16.json.
Service active/running, PID 208487, started Oct 1; checkout b31b2136b5fe982d0b63b0135479b1549041906c. Candidate base differs.
Package metadata: project 0.1.0, FastAPI 0.141.1, psycopg NOT_FOUND. This does not by itself prove a running-service failure.
Process cwd/executable inspection returned exit 1; loaded Python code identity and effective source selection remain NOT_ATTESTED. No secrets/config values were read. Existing untracked egg-info is recorded.
A is PARTIAL: read-only accessible inventory complete; exact process provenance/source selection require an authorized narrow diagnostic surface before production admission.

## B — bounded recovery harness

bounded_recovery_p242.run explicitly invokes accepted recover_durable; no daemon, timers, network or send.
Nonblocking invocation lock returns BUSY, max 3 immediate IO retries, validated item bound, policy denial propagates without retry, report errors fail closed. Time budget checked before/between/after calls.
Budget is cooperative, NOT hard cancellation of blocked filesystem IO or the existing inner recovery lock. Snapshot scan remains O(total inbox). No unconditional unattended-readiness claim.
Existing independent-process restart, cursor and SIGKILL tests are reused.

## C — migration and rollback rehearsal

ledger_migration_rehearsal_p242.rehearse opens an explicit snapshot read-only and requires an empty private workspace.
8 MiB snapshot cap, no-follow regular single-link source checks, canonical v2 record validation, exact record/byte/digest preservation, fsync and rollback check in disposable child directory.
No live cutover API. Legacy writer quiescence is NOT proven. No generation-artifact digest verification beyond ledger record validation; production migration must add source/generation attestation.
SIGKILL test proves original snapshot stays intact, abandoned workspace is refused, fresh workspace restart passes. Operators inspect abandoned rehearsal directories; no automatic deletion of arbitrary existing data.

## D — failure qualification and deployment/rollback runbook

Tests inject EIO/ENOSPC at file and directory fsync, failed replacement, and interrupted rehearsal.
File-fsync failure preserves old ledger. Directory-fsync failure can leave the new valid ledger visible while append reports error: reconcile/replay before retry; no acknowledgement or power-loss durability claim.
Idempotent retry produces one sequence per batch after the tested failures. Physical power loss and hostile filesystem races are unproven.

Proposed deployment sequence (NOT EXECUTED):
1. Obtain narrowly scoped process/package/config/source manifest and compare it to an exact accepted candidate. Stop if identity is unknown.
2. Record previous release SHA, dependency lock/environment, unit/config metadata and owner-approved backup plus checksum; prove restore on disposable data. Never copy secrets into Git.
3. Rehearse candidate and previous release in isolation with NO_SEND, inspect integrity/counts/digests and source-health behavior.
4. Present exact candidate, restoration commands and residual risks for separate owner go/no-go. Only then may a separately authorized operator quiesce writers, snapshot and switch release.
5. Abort on integrity/count mismatch, unexpected send, scope violation or exhausted retries. Preserve evidence and restore the approved previous release/config/data according to the rehearsed procedure; verify integrity and health before resumption.

No deploy-ready command is asserted while actual source selection, dependencies and rollback storage are unverified.

## E — acceptance

Focused and full-suite results, exact commit, environment and CI are to be recorded after completion. Code hashes in runtime manifest bind native validation to these files.
Documentation-only follow-up does not alter tested code; any code edit requires fresh relevant validation.
Phase 23/P24.1 acceptance remains unchanged. P24.3 resource/retention/observability and P24.4 owner production decision remain separate.
