# Phase 19 — Real Soak Continuity Failure and Remediation

Date: 2026-09-11
Status: `ATTEMPT_1_FAILED_CONTINUITY / REMEDIATION_IN_PROGRESS`

## Finding after the owner pause

The first owner-local real-soak attempt did **not** satisfy the evidence-continuity gate.

Canonical audit evidence:

- audit run: `34565336933`
- audit job: `103156191413`
- canonical repository SHA evaluated: `9ac388a905b57fd8fe737e1c0439e49bf606fe85`
- original baseline: `2026-09-10T00:19:31Z`
- completed workflow-dispatch controls after baseline: `8`
- failed controls after baseline: `0`
- qualifying health observations: `8`
- latest qualifying observation: `2026-09-11T04:55:10Z`
- maximum observed evidence gap: `9.280277777777778h`
- maximum allowed gap: `7h`
- audit result: `FAIL_CONTINUITY`
- 24h milestone: `FAIL_CONTINUITY`
- preserved audit artifact: `10185788371`
- artifact ZIP SHA256: `0fb067868dc066a68d8e62490d74bab113e0c8ec488b365c41792b5bb808df17`

Therefore:

```text
P19_REAL_SOAK_ATTEMPT_1 = FAILED_CONTINUITY / NOT_EVIDENCED
P19_REAL_24H_SOAK = NOT_VALIDATED
PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED = NO
```

The elapsed wall-clock duration is not sufficient to override this failure.

## Host/runtime distinction

The continuity failure is an evidence-chain failure; it does not establish a KGM host outage.

The latest qualifying control before this record was:

- control run: `34563957732`
- job: `103152139880`
- observation: `2026-09-11T04:55:10Z`
- Tailscale connectivity: PASS
- target: `kgm-e4-owner-pilot` / `100.102.136.23`
- `kgm-monitor.service`: `active` before and after
- runtime DB read as `kgmops`: denied
- arbitrary root escalation: denied
- restart: skipped
- Ansible recap: `ok=10 changed=0 unreachable=0 failed=0 skipped=1`

All eight controls counted by the failing audit completed successfully. The failed gate means that observation timing left one or more intervals longer than the required seven-hour evidence bound.

## Remediation rule

The seven-hour continuity criterion is retained. It is **not** widened or waived after the failure.

The target observation cadence changes from six hours to three hours:

```text
health dispatcher = 27 */3 * * * UTC
dead-man audit     = 47 */3 * * * UTC
maximum gap        = 7h
```

This creates design margin for one missed nominal three-hour cycle while retaining the original evidence requirement.

The Tailscale trust boundary remains unchanged:

```text
scheduled dispatcher
  -> workflow_dispatch(operation=health)
  -> existing tailscale-kgm-control.yml
  -> GitHub OIDC
  -> Tailscale
  -> kgmops / bounded Ansible
  -> kgm-e4-owner-pilot
```

No new Tailscale workflow identity is introduced.

## Canonical baseline source

The active real-soak baseline is moved from duplicated workflow literals to:

`ops/p19/real_soak_baseline.txt`

During this remediation PR the file intentionally still contains the failed Attempt 1 baseline. This preserves fail-closed behavior until a fresh post-remediation canonical health observation is obtained.

The audit collector is changed so qualifying evidence is selected using the health observation step completion timestamp. This allows a future baseline to be anchored precisely to a verified observation rather than to the earlier workflow creation time.

## Re-anchor procedure

A new P19 real-soak attempt may begin only after all of the following:

1. cadence/baseline remediation is merged to canonical `main`;
2. exact-main CI and P19 contract checks pass;
3. a fresh `workflow_dispatch(operation=health)` control on the remediated canonical revision succeeds;
4. the exact verified observation timestamp is recorded as the new canonical baseline;
5. the new baseline is merged and a read-only audit confirms `PASS / IN_PROGRESS` with no continuity failure.

The previous 24h elapsed interval is never retroactively converted to PASS.

## Binding project boundaries

```text
OWNER_LOCAL_RUNTIME = CANONICAL
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
PRODUCTION_LIVE = NOT_OPERATIONAL
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
A5 = DEFERRED / NOT AUTHORIZED
STRATEGIC_MACHINE_STATE = 4.34 / INTENTIONALLY_FROZEN
P20 = NOT_STARTED
```
