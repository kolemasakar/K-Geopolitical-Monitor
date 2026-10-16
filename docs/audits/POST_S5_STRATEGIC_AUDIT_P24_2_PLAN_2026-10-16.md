# Post-S5 strategic audit and P24.2 remediation plan — 2026-10-16

Status: DOCUMENTARY_AUDIT_COMPLETE / P24_2_PLAN_PREPARED / PRODUCTION_GATE_OPEN.
Scope: repository evidence review, not fresh runtime inspection or new test execution.
Audit baseline: main 9c9c03f05640441b47b8b58ec59d15f841ca9c01 (PR #227 merged).

## Evidence and findings

- S5 offline acceptance is retained with known limitations. PRs #217, #218, #219, #220 and #223 are recorded accepted; #225–#227 reconcile evidence and state.
- Accepted research code anchor: 9c10d4d2dec331f82db3e4a346bcaef6372df3b3. Recorded integrated ARM64 result: 1615/1615 PASS, 466.86 seconds, exit 0. This audit did not rerun tests. The supplied chat's 457.55 seconds is not corroborated by these repository records.
- Final acceptance report had a stale partial-evidence heading and a stale pending-attestation sentence, contradicting its accepted exit result. Reconciled in this documentation change.
- Historical runtime audit remains immutable as a dated snapshot. Last recorded checkout b31b2136b5fe982d0b63b0135479b1549041906c differs from accepted research code. No fresh service, process-code or source-health attestation was collected here.
- SIGKILL qualification establishes tested process-crash behavior; it cannot establish physical power-loss durability. Read-only compatibility is not a tested migration. Injected test grants are not authenticated network identities.
- Phase 23 P23.4 and broader P24.1 coverage remain open. P24.2 engineering can proceed on the approved parallel validation track; this is not full P24.1 closure.
- Historical status fields and appended checkpoints are not current deployment attestations. Preserve historical evidence and use the latest explicit scoped acceptance.

## Remediation matrix

| Gate | Required work | Acceptance evidence | Execution boundary |
| --- | --- | --- | --- |
| Runtime drift | Inventory unit, checkout, process start, installed package provenance, permissions, config and source selection; compare with candidate | Timestamped read-only manifest, exact candidate SHA, reviewed difference and rollback inventory | No service restart or live checkout modification |
| Ledger migration | Specify deterministic v1-to-v2 conversion, backup, integrity checks, lock/exclusive-writer behavior, interrupted conversion and rollback | Isolated synthetic and authorized sanitized-copy rehearsal; exact record counts, identities, duplicates and checksums; corrupt input fails closed; original unchanged | No live migration |
| Durability | Define acknowledgement/replace/file-fsync/directory-fsync boundary; test EIO, ENOSPC and interrupted recovery in disposable storage | Fault matrix with pre/post-commit outcomes, integrity and replay assertions; physical power-loss assurance remains explicitly unproven absent suitable evidence | Never power-cycle the active host for this test |
| Consumer identity | Specify trusted principal binding, allowlist, scope, revocation, replay and cross-consumer isolation | Offline negative tests for missing/forged/revoked/wrong-scope identity; NO_SEND enforced | No listener, credential enrollment or external delivery |
| Owner admission | Consolidate residual risk and deployment/rollback runbook | Explicit owner go/no-go after technical review | No implicit production permission |

## P24.2 work packages and ordering

1. P24.2-A: establish a fresh read-only runtime/candidate inventory and test-entry manifest; record unavailable access instead of inferring current health.
2. P24.2-B: isolate scheduler/recovery harness with bounded retries, no overlapping writer, deadlines, restart continuity and fail-closed source/error states. Reuse accepted S5 tests; add meaningful missing failure cases.
3. P24.2-C: implement and rehearse ledger conversion/rollback on disposable data, with resource bounds and integrity checks. No production format cutover.
4. P24.2-D: validate storage fault handling and candidate deployment/rollback procedure in isolation; retain unsupported power-loss claims as limitations.
5. P24.2-E: consolidate exact-head CI and independent native ARM64 results, command/environment provenance and evidence hashes; synchronize handoff. P24.3 owns retention/resource/observability follow-up; P24.4 owns final production decision.

External consumer authentication remains a separate integration gate and need not block NO_SEND isolated recovery tests. No K-Sentinel/K-Trader enrollment is included.

## Exit criteria and rollback requirements

Each implementation PR requires exact-head relevant tests and repository-required CI; code acceptance requires full regression and independent native ARM64 evidence under existing project practice. Documentation-only work receives consistency/link/JSON review; it does not manufacture a new 1615-test run.
Before any proposed deployment: pin candidate and previous release, preserve unit/config/dependency manifests and data backup, prove rollback in isolation, define abort conditions (integrity failure, retry exhaustion, unexpected send, scope violation), and require a separate owner decision. If safe rollback cannot be demonstrated, deployment remains blocked.
No calendar milestone or production target date is inferred.

FREE_ONLY / RESEARCH_ONLY / NO_SEND. No source activation, live migration, service restart, persistent scheduler activation, paid/shared infrastructure, HP-OMEN use or public publication.
