# Phase 18 A4 — Railway Trial No-Charge Evidence

Date: 2026-09-09
Project: K-Geopolitical Monitor
Evidence class: `OWNER_PROVIDED_ACCOUNT_UI / POINT_IN_TIME`
Purpose: close the A4 cost-verification condition under the binding beta no-paid-resource policy and preserve the observed Trial Workspace operating boundary.

## Observed Railway UI

The owner supplied screenshots from Railway `Settings -> Billing` and `Settings -> Plans` for the workspace used by the KGM disposable preflight candidate.

Visible account-level facts:

- `Active Plan`: **Trial Workspace**;
- `Plans` states **You're on the Trial Plan**;
- the Trial Plan includes **$5 of free resource usage**;
- the Trial Plan shows **2 vCPU / 0.5 GB RAM per service**;
- **code and database deployments** are included;
- **community support** is included;
- the UI states deployments are shut down when trial credits run out;
- `Payment Method`: **No payment method on file**;
- `Billing History`: **No billing history found**;
- Hobby is not shown as the active plan and is offered separately via **Unlock Hobby plan**;
- Pro is not shown as the active plan and is offered separately as a paid plan;
- the paid-plan comparison shows Hobby at **$5 minimum usage** and Pro at **$20 minimum usage**;
- the account header shows approximately **29 days or $4.98 left** at the time of observation.

## Determination

For the point-in-time A4 validation on 2026-09-09:

`A4_COST_STATUS = NO_CHARGE_VERIFIED`

The automated provider integration cannot observe the account billing/trial state directly, so the machine-side status remains:

`A4_AUTOMATED_COST_STATUS = NOT_OBSERVABLE`

`A4_OVERALL_COST_STATUS = DETERMINED_OUTSIDE_AUTOMATION`

This satisfies the beta requirement that A0-A4 validation use free/no-charge disposable infrastructure only.

## Observed Trial Boundary

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

The capacity and account values above are screenshot-derived observations of the active Trial Plan on 2026-09-09. They are not a permanent provider entitlement and must be rechecked if Railway changes the trial terms.

## Project Spend Guard

This evidence does **not** authorize:

- a Hobby subscription;
- a Pro subscription;
- adding a payment method;
- purchasing credits;
- any other paid Railway resource;
- automatic conversion from trial to a paid project state;
- shared-runtime activation or canonical cutover.

Binding project tokens:

```text
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
RAILWAY_PAID_UPGRADE_AUTHORIZED = NO
RAILWAY_PAYMENT_METHOD_ADD_AUTHORIZED = NO
RAILWAY_CREDIT_PURCHASE_AUTHORIZED = NO
RAILWAY_POST_TRIAL_SPEND_AUTHORIZED = NO
A4_COST_REVERIFY_BEFORE_A5 = REQUIRED
```

If a future proof requires paid capacity, it must remain blocked or be redesigned to use an approved no-charge path. Trial exhaustion or expiry is a stop condition for the disposable Railway candidate, not permission to upgrade.

## Time-Bounded Validity

This is a point-in-time trial-state observation, not a permanent provider-cost entitlement.

The no-charge classification is valid only while the observed Trial Workspace remains active and has free trial capacity. The provider UI explicitly indicates the trial can end on time expiry or earlier if credits are exhausted.

Transient snapshot observed on 2026-09-09:

- approximately `29 days` remaining;
- approximately `USD 4.98` credit remaining.

These two values must not be treated as current after the observation date without a fresh Railway account check.

Therefore, before any future A5 activation decision, cost status must be revalidated if any of the following is true:

- the trial period has expired or approaches expiry;
- the remaining trial credit is exhausted or materially changed;
- Railway changes the active plan or trial limits;
- a payment method is added or proposed;
- a paid subscription or credit purchase is proposed;
- provider pricing or account status changes.

## Preserved Strategic Boundary

`PHASE_18_SHARED_RUNTIME_LAUNCH_EVIDENCE_READY = PASS`

`ACTIVATION_READY / NOT_ACTIVATED`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`CANONICAL_CUTOVER_AUTHORIZED = NO`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`OWNER_LOCAL_RUNTIME = CANONICAL`

Strategic machine state remains sync `4.34` and is intentionally not modified by this evidence record.

Consolidated project/trial checkpoint:

`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_READY_RAILWAY_TRIAL_BOUNDARY.md`
