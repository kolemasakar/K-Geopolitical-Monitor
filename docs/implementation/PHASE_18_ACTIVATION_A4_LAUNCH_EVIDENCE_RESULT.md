# Phase 18 Activation A4 — Fresh Exact-Head Launch Evidence Result

Date: 2026-09-09
Project: K-Geopolitical Monitor
Target gate: `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`
Status: `TECHNICAL_EVIDENCE_PASS / BLOCKED_COST_VERIFICATION_REQUIRED / NOT_ACTIVATED`
Frozen launch candidate: `44761d58fd0e0421131cda5059bc955c35bafb6f`
Strategic state sync: `4.34` unchanged

## Scope

A4 freezes one exact launch-candidate SHA and revalidates the technical launch-readiness evidence without changing canonical authority, accepting Railway staged changes, authorizing paid resources, or activating shared runtime.

All technical A4 jobs explicitly checkout the frozen candidate SHA rather than the PR merge ref. The A4 workflow itself is control-plane evidence only; it does not redeploy Railway or mutate provider state.

## Accepted Technical Evidence

Final A4 workflow run: `34383486940`.

- frozen x64 job `102573817917`: SUCCESS;
  - Ubuntu 24.04.5;
  - Python 3.11.16 x64;
  - dependency check: PASS;
  - exact frozen SHA assertion: PASS;
  - `1164 passed in 289.96s`.
- frozen native ARM64 job `102573817916`: SUCCESS;
  - Ubuntu 24.04.4 ARM image;
  - architecture: `aarch64`;
  - Python 3.11.16 arm64;
  - dependency check: PASS;
  - exact frozen SHA assertion: PASS;
  - `1164 passed in 103.70s`;
  - bootstrap shell validation: PASS;
  - unattended one-tick smoke: PASS;
  - systemd unit contract: PASS.
- frozen shadow reconciliation job `102573817854`: SUCCESS;
  - PostgreSQL 16.15 disposable service;
  - exact reconciliation: PASS;
  - retry/idempotency: PASS;
  - outbox persistence: PASS;
  - forced tenant isolation: PASS;
  - read-only shadow observation: PASS;
  - deliberate mismatch classes: `ROW_COUNT`, `TABLE_CONTENT`, `SEMANTIC_PROJECTION`;
  - mismatch budget behavior: `3 > 2`, fail-closed PASS;
  - automatic promotion: false;
  - canonical cutover authorized: false.
- frozen recovery job `102573817601`: SUCCESS;
  - PostgreSQL client 16.15;
  - logical `pg_dump -> pg_restore`: PASS;
  - source rows: 3;
  - restored RLS contract: PASS;
  - ephemeral cleanup: PASS;
  - owner-local independent rollback/startup: PASS.
- live candidate controls job `102573817880`: SUCCESS;
  - existing Railway candidate remains observable and non-canonical;
  - credential-free live canary: PASS;
  - no Railway mutation performed.
- readiness gate job `102575682072`: SUCCESS as a fail-closed state composer.

Final PR-head CI run `34383486586`, job `102573816190`:

- Ubuntu 24.04.5;
- Python 3.11.16 x64;
- `1164 passed in 93.74s`;
- SUCCESS.

## Readiness Gate Output

The final readiness job produced:

```text
A4_LAUNCH_CANDIDATE_SHA=44761d58fd0e0421131cda5059bc955c35bafb6f
A4_TECHNICAL_EVIDENCE=PASS
A4_COST_STATUS=NOT_OBSERVABLE
A4_GATE=BLOCKED_COST_VERIFICATION_REQUIRED
A4_ACTIVATION_STATE=NOT_READY_COST_STATUS_UNVERIFIED
PHASE_18_SHARED_RUNTIME_ACTIVE=NO
CANONICAL_CUTOVER_AUTHORIZED=NO
MIGRATION_033=NOT_CREATED_NOT_PREAUTHORIZED
PRODUCTION_LIVE=NOT_OPERATIONAL
```

Therefore the technical A4 evidence is complete, but the target gate `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY` is **not satisfied**.

## Provider / Topology / Cost Snapshot

Read-only Railway inspection observed:

- project: `kgm-shared-runtime-preflight`;
- environment provider-name: `production`, while KGM classification remains disposable non-production preflight;
- canonical candidate service: `kgm-preflight-api-v3`;
- deployed source remains `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- API has the intended Railway service domain;
- PostgreSQL has no public service domain;
- 31 existing staged Railway changes remain untouched;
- effective plan tier: `HOBBY`;
- included usage credit reported: `$5`;
- account-specific subscription-fee / waiver / trial / no-charge status: `NOT_OBSERVABLE` through the available read-only integration.

Railway documentation states that the standard Hobby plan has a monthly subscription fee, while a fee waiver may exist for eligible accounts. Since the current account-specific waiver/no-charge state is not programmatically observable, A4 cannot classify this provider candidate as no-charge under the binding beta policy.

No payment, upgrade, new paid resource, staged-change acceptance, redeploy, or provider mutation was performed to resolve this limitation.

## Harness Correction Record

Initial A4 workflow run `34383326462` had one infrastructure-only harness failure in frozen-recovery job `102573277195` before the recovery proof ran.

Cause: a transient `Hash Sum mismatch` in the GitHub-hosted runner's third-party Google Chrome APT repository during `apt-get update`.

Correction:

- runtime/candidate code was unchanged;
- frozen candidate SHA was unchanged;
- the disposable runner now removes only Google APT list files before the PostgreSQL client refresh and uses APT retries;
- final run `34383486940` then completed the real logical recovery proof successfully.

This was not a KGM candidate failure and is retained as transparent harness history.

## Explicit Boundaries

- owner-local runtime remains canonical and independently operable;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `CANONICAL_CUTOVER_AUTHORIZED = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- Railway staged changes remain untouched;
- strategic machine state remains `4.34`;
- A5 is not opened by technical A4 success.

## Blocking Condition

To satisfy the A4 target gate under the approved beta policy, direct account-level evidence must establish that the currently used Railway resources are no-charge for this account, for example an authoritative Billing/dashboard indication of an active fee waiver or equivalent no-charge state.

Until that evidence exists:

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = NOT_SATISFIED`

`A4_GATE = BLOCKED_COST_VERIFICATION_REQUIRED`
