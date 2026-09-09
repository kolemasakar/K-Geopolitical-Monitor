# Phase 18 A4 — Railway Trial No-Charge Evidence

Date: 2026-09-09
Project: K-Geopolitical Monitor
Evidence class: `OWNER_PROVIDED_ACCOUNT_UI / POINT_IN_TIME`
Purpose: close the A4 cost-verification condition under the binding beta no-paid-resource policy.

## Observed Railway UI

The owner supplied screenshots from Railway `Settings -> Billing` and `Settings -> Plans` for the workspace used by the KGM disposable preflight candidate.

Visible account-level facts:

- `Active Plan`: **Trial Workspace**;
- the Trial Workspace includes a **$5 credit balance**;
- the UI states deployments are shut down when credits run out;
- `Payment Method`: **No payment method on file**;
- `Billing History`: **No billing history found**;
- Hobby is not shown as the active plan; the UI instead offers **Unlock Hobby plan**;
- `Plans` states **You're on the Trial Plan**;
- the Trial Plan states **Includes $5 of free resource usage**;
- the account header shows approximately **29 days or $4.98 left** at the time of observation.

## Determination

For the point-in-time A4 validation on 2026-09-09:

`A4_COST_STATUS = NO_CHARGE_VERIFIED`

This satisfies the beta requirement that A0-A4 validation use free/no-charge disposable infrastructure only.

This evidence does **not** authorize:

- a Hobby subscription;
- adding a payment method;
- purchasing credits;
- any other paid Railway resource;
- shared-runtime activation or canonical cutover.

## Time-Bounded Validity

This is a point-in-time trial-state observation, not a permanent provider-cost entitlement.

The no-charge classification is valid only while the observed Trial Workspace remains active and has free trial capacity. The provider UI explicitly indicates the trial can end on time expiry or earlier if credits are exhausted.

Therefore, before any future A5 activation decision, cost status must be revalidated if any of the following is true:

- the trial period has expired;
- the remaining trial credit is exhausted or materially changed;
- Railway changes the active plan;
- a payment method is added;
- a paid subscription or credit purchase is proposed;
- provider pricing or account status changes.

## Preserved Strategic Boundary

`BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`CANONICAL_CUTOVER_AUTHORIZED = NO`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`
