# Project Checkpoint — Phase 18 Activation A4 Fresh Exact-Head Launch Evidence

Date: 2026-09-09
Project: K-Geopolitical Monitor
Target gate: `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`
Status: `IN_PROGRESS / TECHNICAL_PASS / BLOCKED_COST_VERIFICATION_REQUIRED`
Frozen launch candidate: `44761d58fd0e0421131cda5059bc955c35bafb6f`
Strategic state sync: `4.34` unchanged

## Current Determination

A4 technical launch-readiness evidence is complete and PASS on the frozen launch-candidate SHA. Formal A4 gate closure is blocked because the current Railway account-specific no-charge/waiver status cannot be observed through the available read-only integration.

This checkpoint intentionally does **not** mark `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY` as satisfied.

## Accepted Frozen-SHA Evidence

A4 workflow run `34383486940`:

- frozen x64 job `102573817917`: SUCCESS, `1164 passed in 289.96s`;
- frozen native ARM64 job `102573817916`: SUCCESS, `aarch64`, `1164 passed in 103.70s`;
- ARM64 bootstrap/unattended/systemd contracts: PASS;
- frozen shadow reconciliation job `102573817854`: SUCCESS;
- frozen recovery job `102573817601`: SUCCESS;
- live candidate controls job `102573817880`: SUCCESS;
- readiness-gate job `102575682072`: SUCCESS as fail-closed state composition.

Full PR-head regression run `34383486586`, job `102573816190`:

- Ubuntu 24.04.5;
- Python 3.11.16 x64;
- `1164 passed in 93.74s`;
- SUCCESS.

## Recovery / Rollback Evidence

Frozen recovery proof established:

- PostgreSQL 16.15 client tooling;
- logical dump/restore: PASS;
- restored RLS contract: PASS;
- deterministic source/restored evidence: PASS;
- ephemeral cleanup: PASS;
- owner-local unattended one-tick startup: PASS;
- owner-local SQLite integrity: PASS.

Owner-local remains the canonical rollback path because no shared-runtime cutover exists.

## Shadow / Canary Evidence

Frozen A3 proof established:

- exact deterministic reconciliation: PASS;
- retry/idempotency: PASS;
- outbox persistence: PASS;
- tenant isolation: PASS;
- read-only shadow observation: PASS;
- deliberate mismatch classes: `ROW_COUNT`, `TABLE_CONTENT`, `SEMANTIC_PROJECTION`;
- mismatch count `3` against budget `2`: fail-closed PASS;
- automatic promotion: false;
- shared-runtime activation authorized: false.

The live Railway canary also remained PASS without mutating Railway.

## Cost Gate

Read-only provider inspection established:

- effective Railway plan tier: `HOBBY`;
- included usage credit: `$5`;
- subscription-fee/waiver/trial/no-charge status for this account: `NOT_OBSERVABLE`;
- current integration cannot prove an active fee waiver.

Accordingly:

```text
A4_TECHNICAL_EVIDENCE=PASS
A4_COST_STATUS=NOT_OBSERVABLE
A4_GATE=BLOCKED_COST_VERIFICATION_REQUIRED
A4_ACTIVATION_STATE=NOT_READY_COST_STATUS_UNVERIFIED
```

The beta rule `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED` prevents treating an ordinary Hobby plan as acceptable unless no-charge status is directly established.

## Harness Correction

Initial A4 run `34383326462`, frozen-recovery job `102573277195`, was interrupted by a transient third-party Google Chrome APT repository `Hash Sum mismatch` before recovery execution.

Only the A4 disposable-runner harness was hardened. Candidate/runtime code and frozen SHA were not changed. The final recovery job then passed.

## Preserved Boundaries

- owner-local canonical authority: unchanged;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `CANONICAL_CUTOVER_AUTHORIZED = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- no paid resource was authorized;
- no Railway staged change was accepted;
- no Railway redeploy was performed;
- strategic machine state remains `4.34`.

## Required Evidence to Unblock

A4 may be reconsidered only after direct account-level evidence establishes that the currently used Railway resources are no-charge for the owner account under the beta policy.

Until then:

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = NOT_SATISFIED`
