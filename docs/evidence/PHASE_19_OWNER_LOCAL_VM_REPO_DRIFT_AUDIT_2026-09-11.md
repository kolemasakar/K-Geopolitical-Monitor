# Phase 19 Owner-Local VM ↔ Repository Drift Audit

Date: 2026-09-11
Status: `READ_ONLY_AUDIT_COMPLETE`
Scope: owner-local KGM runtime `kgm-e4-owner-pilot` versus canonical GitHub `main`

## 1. Purpose

This audit was performed during P19 real-soak Attempt 2 without deployment, restart, package changes, database access, baseline changes, cadence changes, or modification of the active remote-control trust boundary.

## 2. Observed runtime state

Fresh exact-main health control after the P19 Attempt 2 canonical re-anchor reported:

```text
TARGET = kgm-e4-owner-pilot
TAILSCALE_IP = 100.102.136.23
SERVICE_BEFORE = active
SERVICE_AFTER = active
RUNTIME_DB_READ_BY_KGMOPS = denied
ARBITRARY_ROOT_ESCALATION = denied
RESTART = skipped
ANSIBLE = ok=10 changed=0 unreachable=0 failed=0 skipped=1
DEPLOYED_REPOSITORY_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
CONTROL_REPOSITORY_SHA = b4c0f6b2e5d5772654842ebb3a22e7c2a87dfb4f
```

The health operation was therefore state-preserving and did not mutate the host.

## 3. Git ancestry result

GitHub compare from deployed SHA `b31b2136b5fe982d0b63b0135479b1549041906c` to canonical `main` SHA `b4c0f6b2e5d5772654842ebb3a22e7c2a87dfb4f` reports:

```text
RELATION = main ahead of deployed SHA
AHEAD_BY = 516 commits
BEHIND_BY = 0
MERGE_BASE = deployed SHA
```

The deployed SHA is an ancestor of current `main`; this is not a divergent-history or split-brain condition.

## 4. Drift classification

The delta is **material**, not documentation-only. The compare includes later runtime/source-code, migration, operational-control, source-network, semantic-verification, forecast, delivery, shared-runtime-preflight and P19 files in addition to documentation and CI/workflow changes.

Examples in the later canonical tree include:

- `src/kgeopolitical_monitor/operational_stability.py`;
- `src/kgeopolitical_monitor/source_portfolio.py`;
- Phase 13 semantic verification/provenance modules;
- Phase 15 forecast calibration modules;
- Phase 16/17 delivery/publication modules;
- Phase 18 shared-runtime/preflight modules;
- migrations `022` through `032`;
- P19 operational stability and soak logic.

Therefore:

```text
OWNER_LOCAL_HOST_REACHABILITY = PASS
OWNER_LOCAL_SERVICE_HEALTH = PASS
OWNER_LOCAL_SECURITY_BOUNDARY = PASS
P19_SOAK_CONTROL_CHAIN = PASS
DEPLOYED_SHA_ANCESTOR_OF_MAIN = YES
DEPLOYED_RUNTIME_EQUALS_CURRENT_MAIN = NO
RUNTIME_CODE_DRIFT = MATERIAL
```

## 5. Interpretation for P19

The current soak proves sustained health and bounded operability of the **actually deployed owner-local runtime**. It must not be misrepresented as proof that current canonical `main` is deployed on the VM.

The active Attempt 2 baseline remains valid for the observed deployed runtime and is not reset by this read-only audit.

However, before final P19 closure, the project must make an explicit scope decision:

### Option A — close P19 against the observed deployed runtime

Only acceptable if P19's gate is explicitly defined as sustained stability of the current beta runtime and the substantial repository/deployment drift is recorded as a known deployment-convergence item for a subsequent controlled release gate.

### Option B — require current-main deployment equivalence for P19 closure

If P19 is intended to validate the latest canonical application code in live owner-local operation, a controlled deployment of a selected canonical release candidate is required and the elapsed soak would need a new baseline after deployment.

No option is selected by this audit. A deployment is specifically **not authorized or performed** here.

## 6. Current fail-closed classification

Until the closure scope is explicitly selected:

```text
P19_RUNTIME_HEALTH = PASS
P19_RUNTIME_REPO_DRIFT_AUDIT = COMPLETE
P19_DEPLOYED_RUNTIME_EQUIVALENCE = NOT_EVIDENCED
P19_FINAL_CLOSURE_DRIFT_DECISION = REQUIRED
```

This does not invalidate Attempt 2 continuity evidence already being collected, but it prevents accidental conflation of host-health evidence with deployment-equivalence evidence.

## 7. Preserved boundaries

```text
OWNER_LOCAL_RUNTIME = CANONICAL
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
A5 = DEFERRED / NOT AUTHORIZED
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_AUTHORIZED
STRATEGIC_MACHINE_STATE = 4.34 / INTENTIONALLY_FROZEN
```
