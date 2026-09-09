# Project Checkpoint — Phase 18 Activation A4 Fresh Exact-Head Launch Evidence Validated

Date: 2026-09-09
Project: K-Geopolitical Monitor
Gate: `PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY`
Status: `VALIDATED / ACTIVATION_READY_NOT_ACTIVATED`
Frozen launch candidate: `44761d58fd0e0421131cda5059bc955c35bafb6f`
Strategic state sync: `4.34` unchanged

## Gate Result

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = PASS`

`A4_TECHNICAL_EVIDENCE = PASS`

`A4_COST_STATUS = NO_CHARGE_VERIFIED`

`A4_ACTIVATION_STATE = ACTIVATION_READY_NOT_ACTIVATED`

## Technical Evidence

Accepted frozen-candidate proof:

- exact x64 regression: PASS;
- exact native ARM64/aarch64 regression: PASS;
- dependency integrity: PASS;
- bootstrap/unattended/systemd contracts: PASS;
- deterministic shadow reconciliation: PASS;
- retry/idempotency/outbox persistence: PASS;
- tenant isolation: PASS;
- logical recovery: PASS;
- owner-local rollback: PASS;
- live Railway non-canonical controls: PASS;
- automatic promotion/cutover: disabled.

Primary A4 run: `34383486940`.

PR #58 merged A4 evidence/harness at canonical SHA:

`74e2aeb103ced874a3dd47a0600bf31536802090`

Post-merge exact-main evidence included:

- CI run `34384871798`, job `102578501178`: `1164 passed in 113.94s`;
- frozen x64: `1164 passed in 95.73s`;
- frozen native ARM64/aarch64: `1164 passed in 92.00s`;
- A3 shadow/live-canary: PASS;
- A2.3 recovery/owner-local rollback: PASS.

## Cost Evidence

Direct owner-provided Railway Billing/Plans UI screenshots show:

- active plan: `Trial Workspace` / `Trial Plan`;
- `$5` free resource usage;
- no payment method on file;
- no billing history found;
- Hobby is not active and is offered only via `Unlock Hobby plan`;
- approximately `29 days or $4.98 left` at the observation time;
- deployment shutdown when trial credits run out.

Evidence record:

`docs/evidence/PHASE_18_A4_RAILWAY_TRIAL_NO_CHARGE_EVIDENCE_2026-09-09.md`

The automated Railway integration remains unable to observe account billing state directly. That limitation is retained as `A4_AUTOMATED_COST_STATUS = NOT_OBSERVABLE`; it no longer blocks overall A4 because direct account-level evidence satisfies the external cost-verification condition.

## Time-Bounded Validity

The no-charge determination is point-in-time and must be revalidated before any later A5 activation decision if the trial expires, credits are exhausted, the plan changes, a payment method is added, or paid resources are proposed.

## Preserved Boundaries

- owner-local runtime remains canonical;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `CANONICAL_CUTOVER_AUTHORIZED = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- Railway staged changes remain unaccepted;
- strategic machine state remains `4.34`;
- A5 remains a separate explicit owner decision.

## Current Roadmap Position

`A4 = VALIDATED`

`ACTIVATION_READY / NOT_ACTIVATED`

`A5 = DEFERRED / NOT_AUTHORIZED`
