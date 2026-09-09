# Project Checkpoint — Phase 18 Activation Ready / Railway Trial Boundary

Date: 2026-09-09
Project: K-Geopolitical Monitor
Evidence scope: `PROJECT_STATE + OWNER_PROVIDED_RAILWAY_ACCOUNT_UI`
A4 closure anchor: `78afacfc0dd8af96606645ed7bece966134a61ac`
Current main base at checkpoint update: `ca6e7e4403c2ae67839b983b436b5b34f62fe034`
Strategic state sync: `4.34` intentionally unchanged

## Current Project Position

```text
P18.0–P18.9 = VALIDATED
A0 = COMPLETE
A1 = VALIDATED
A2 = VALIDATED
A3 = VALIDATED
A4 = VALIDATED
PROJECT_POSITION = PHASE_18_A4_VALIDATED_ACTIVATION_READY
ACTIVATION_STATE = ACTIVATION_READY / NOT_ACTIVATED
A5 = DEFERRED / NOT AUTHORIZED
```

A4 closure was merged through PR #60. The A4 closure anchor is:

`78afacfc0dd8af96606645ed7bece966134a61ac`

Accepted post-merge evidence on that closure anchor included:

- canonical CI: `1164 passed in 175.34s`;
- A4 frozen x64 regression: `1164 passed in 131.98s`;
- A4 native ARM64/aarch64 regression: `1164 passed in 161.43s`;
- ARM64 bootstrap: PASS;
- unattended smoke: PASS;
- systemd contract: PASS;
- shadow reconciliation: PASS;
- logical recovery and owner-local rollback: PASS;
- live Railway controls: PASS;
- A4 readiness gate: SUCCESS.

A4 gate state:

```text
PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = PASS
A4_TECHNICAL_EVIDENCE = PASS
A4_COST_STATUS = NO_CHARGE_VERIFIED
A4_AUTOMATED_COST_STATUS = NOT_OBSERVABLE
A4_OVERALL_COST_STATUS = DETERMINED_OUTSIDE_AUTOMATION
```

The automated integration cannot observe Railway account billing state directly. The overall A4 cost result therefore relies on direct owner-provided account UI evidence and is explicitly point-in-time.

## Preserved Strategic Invariants

```text
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
PRODUCTION_LIVE = NOT_OPERATIONAL
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
OWNER_LOCAL_RUNTIME = CANONICAL
CANONICAL_STORAGE = PROJECT_LOCAL_ONLY
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT AUTHORIZED
STRATEGIC_MACHINE_STATE_SYNC = 4.34 / INTENTIONALLY_FROZEN
```

A4 readiness does not authorize A5, shared-runtime activation, canonical data movement, a Railway paid plan, or post-trial spending.

`docs/state/CURRENT_PROJECT_STATE.json` is intentionally not changed by this checkpoint because the strategic machine-state synchronization gate is separate from A0–A4 readiness evidence.

## Railway Trial Workspace — Observed Account State

Owner-provided Railway Billing/Plans screenshots on 2026-09-09 show:

```text
RAILWAY_ACCOUNT_PLAN_OBSERVED = TRIAL_WORKSPACE / TRIAL_PLAN
RAILWAY_FREE_RESOURCE_USAGE_INCLUDED = USD 5
RAILWAY_TRIAL_SERVICE_LIMIT_OBSERVED = 2 vCPU / 0.5 GB RAM per service
RAILWAY_CODE_DEPLOYMENTS = INCLUDED
RAILWAY_DATABASE_DEPLOYMENTS = INCLUDED
RAILWAY_SUPPORT_OBSERVED = COMMUNITY_SUPPORT
RAILWAY_PAYMENT_METHOD_OBSERVED = NONE
RAILWAY_BILLING_HISTORY_OBSERVED = NONE
RAILWAY_HOBBY_PLAN = NOT_ACTIVE
RAILWAY_PRO_PLAN = NOT_ACTIVE
```

The UI separately offers paid plans rather than showing them as active:

- Hobby: `$5` minimum usage / paid plan offer;
- Pro: `$20` minimum usage / paid plan offer.

These paid-plan offers are informational only and are not approved project resources.

## Binding Trial / Cost Boundary

The following rules are durable KGM project constraints while beta remains under the approved no-paid-resource policy:

```text
RAILWAY_PAID_UPGRADE_AUTHORIZED = NO
RAILWAY_PAYMENT_METHOD_ADD_AUTHORIZED = NO
RAILWAY_CREDIT_PURCHASE_AUTHORIZED = NO
RAILWAY_POST_TRIAL_SPEND_AUTHORIZED = NO
RAILWAY_PAID_RESOURCE_AUTOPROMOTION = DISABLED / NOT AUTHORIZED
A4_COST_REVERIFY_BEFORE_A5 = REQUIRED
```

If a validation step requires payment, a paid plan, purchased credits, or another billable resource, that step must remain blocked or be redesigned to use an approved no-charge proof. It must not silently upgrade Railway or create spend.

Trial exhaustion or expiry is a stop condition for the disposable Railway validation candidate, not authorization to convert the project to a paid plan.

## Point-in-Time Trial Snapshot

Observed in the Railway UI on 2026-09-09:

- approximately `29 days` remaining;
- approximately `USD 4.98` credit remaining.

These values are transient observations, not durable limits or current-balance guarantees. They must not be reused as current account state after the observation date without re-checking Railway.

## Revalidation Triggers

Cost/account state must be reverified before any A5 decision and whenever any of the following occurs:

- trial period expires or approaches expiry;
- trial credits are exhausted or materially reduced;
- Railway changes the active account plan or trial terms;
- a payment method appears or is proposed;
- a paid plan, purchased credits, persistent paid service, or other billable resource is proposed;
- provider pricing/capability changes affect the no-charge boundary.

A5 remains a separate explicit owner activation/cutover decision even if the cost state is later reverified.

## Parallel Operations Note

The current main base at this documentation update already includes PR #61 removing the parked KGM SentinelX after the accepted Tailscale + Ansible replacement-control-plane audit. That parallel operations change does not alter the Phase 18 shared-runtime activation state or the Railway Trial cost boundary recorded here.

## Related Records

- `docs/evidence/PHASE_18_A4_RAILWAY_TRIAL_NO_CHARGE_EVIDENCE_2026-09-09.md`
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A4_LAUNCH_EVIDENCE_VALIDATED.md`
- `docs/implementation/PHASE_18_ACTIVATION_A4_LAUNCH_EVIDENCE_RESULT.md`
- `docs/implementation/PHASE_18_ACTIVATION_A2_A5_APPROVED_PLAN.md`
