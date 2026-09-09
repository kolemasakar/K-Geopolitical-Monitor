# Phase 18 Activation A4 — Fresh Exact-Head Launch Evidence Result

Date: 2026-09-09
Project: K-Geopolitical Monitor
Target gate: `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`
Status: `VALIDATED / ACTIVATION_READY_NOT_ACTIVATED`
Frozen launch candidate: `44761d58fd0e0421131cda5059bc955c35bafb6f`
Strategic state sync: `4.34` unchanged

## Final Determination

A4 is formally validated.

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = PASS`

`A4_TECHNICAL_EVIDENCE = PASS`

`A4_COST_STATUS = NO_CHARGE_VERIFIED`

`A4_ACTIVATION_STATE = ACTIVATION_READY_NOT_ACTIVATED`

This does **not** activate shared runtime, authorize canonical cutover, authorize paid resources, create migration `033`, or change strategic machine state `4.34`.

## Frozen Technical Evidence

Frozen candidate: `44761d58fd0e0421131cda5059bc955c35bafb6f`.

Accepted A4 evidence includes:

- exact frozen-SHA x64 regression: PASS;
- exact frozen-SHA native ARM64/aarch64 regression: PASS;
- dependency integrity: PASS;
- ARM64 bootstrap/unattended/systemd contracts: PASS;
- A3 deterministic shadow reconciliation: PASS;
- A2.3 logical recovery and owner-local rollback: PASS;
- live Railway non-canonical controls: PASS;
- automatic promotion/cutover: disabled.

Primary accepted A4 workflow run `34383486940`:

- frozen x64 job `102573817917`: `1164 passed in 289.96s`;
- frozen ARM64 job `102573817916`: `aarch64`, `1164 passed in 103.70s`;
- frozen shadow reconciliation job `102573817854`: SUCCESS;
- frozen recovery job `102573817601`: SUCCESS;
- live candidate controls job `102573817880`: SUCCESS;
- readiness composer job `102575682072`: SUCCESS.

PR-head regression run `34383486586`, job `102573816190`: `1164 passed in 93.74s`.

PR #58 then merged the A4 harness and blocked-state evidence into canonical `main` at `74e2aeb103ced874a3dd47a0600bf31536802090`.

Post-merge validation on that canonical merge confirmed:

- exact-main CI run `34384871798`, job `102578501178`: `1164 passed in 113.94s`;
- A4 frozen x64: `1164 passed in 95.73s`;
- A4 frozen native ARM64/aarch64: `1164 passed in 92.00s`;
- ARM64 bootstrap/unattended/systemd: PASS;
- A3 shadow/live-canary: PASS;
- A2.3 recovery/owner-local rollback: PASS.

## Cost Evidence Closure

The automated Railway integration could not observe account-specific subscription/waiver/trial state and therefore correctly remained fail-closed at `NOT_OBSERVABLE`.

The owner subsequently supplied direct Railway account UI evidence from `Settings -> Billing` and `Settings -> Plans`.

Observed account-level facts:

- active plan: `Trial Workspace` / `Trial Plan`;
- included free resource usage: `$5`;
- no payment method on file;
- no billing history found;
- Hobby is offered as a separate `Unlock Hobby plan` action and is not the active plan;
- UI showed approximately `29 days or $4.98 left` at observation time;
- Railway states deployments are shut down when trial credits run out.

Evidence record:

`docs/evidence/PHASE_18_A4_RAILWAY_TRIAL_NO_CHARGE_EVIDENCE_2026-09-09.md`

Therefore, for the current A4 point-in-time validation:

`A4_COST_STATUS = NO_CHARGE_VERIFIED`

The earlier integration-only value `NOT_OBSERVABLE` remains historically correct as an **automated-observation limitation**, but it is no longer an unresolved overall A4 blocker because direct owner account evidence now satisfies the external cost-verification condition.

## Time-Bounded Cost Validity

The no-charge classification is not permanent. It is valid only while the observed Trial Workspace remains active and free trial capacity remains available.

Before any future A5 activation decision, cost status must be revalidated if the trial expires, credits are exhausted, the active plan changes, a payment method is added, paid resources are proposed, or Railway pricing/account status changes.

This prevents a point-in-time trial proof from silently becoming a later paid-resource authorization.

## Provider / Topology Snapshot

The disposable Railway candidate remains non-canonical:

- project: `kgm-shared-runtime-preflight`;
- canonical candidate service: `kgm-preflight-api-v3`;
- deployed source remains the prior A1 implementation anchor;
- PostgreSQL remains private/non-public;
- no provider mutation was required for A4 closure;
- no payment, upgrade, credit purchase, redeploy, or staged-change acceptance was performed by this closure.

## Explicit Boundaries

- owner-local runtime remains canonical and independently operable;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `CANONICAL_CUTOVER_AUTHORIZED = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- strategic machine state remains `4.34`;
- A5 remains a separate explicit owner decision and is **not authorized by A4 validation**.

## Gate Closure

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = PASS`

Current operational state:

`ACTIVATION_READY / NOT_ACTIVATED`
