# P22.1 — Bounded Owner-Only Operational Pilot — Result

Date: 2026-09-19
Status: `VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION`
Gate: `P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED`
Execution SHA: `ec71242cc3cb8f793a7dcf0b70c884e085db5b26`
Target node: `kgm-e4-owner-pilot`

## Decision

P22.1 is validated for **bounded owner-local operational execution**, with measured collection degradation and no semantic-utility claim.

The authorized one-shot pilot executed successfully on an isolated exact-main checkout on the real ARM64 owner node. It persisted a healthy supervisor tick and a completed monitoring run while preserving source failure visibility, project-local storage and deployed-runtime containment.

## Execution evidence

```text
ARCH = aarch64
PYTHON = 3.12.3
EXACT_MAIN_SHA = ec71242cc3cb8f793a7dcf0b70c884e085db5b26
PILOT_ROOT = /tmp/kgm-p221-owner-pilot-20260919
WATCH_ID = watch-p22-1-bounded-20260919
CHECKED_AT = 2026-09-19T14:28:20.080287+00:00
EXECUTION_COUNT = 1
RUN_STATUS = COMPLETED
RESULT_COUNT = 0
RECOVERED_RUNS = 0
RUNTIME_HEALTH = HEALTHY
DB_INTEGRITY = ok
```

## Source outcome

The live collection was `PARTIAL`:

- `consilium-press-releases`: `SUCCESS`, 0 matching items;
- `gdelt-doc-2`: `FAILED`, HTTP 429;
- total persisted collection items: 0;
- source successes: 1;
- source failures: 1.

The GDELT degradation is preserved as operational evidence rather than hidden or converted into a successful source state.

## Owner workspace observation

Post-run owner workspace remained read-only:

```text
owner_execution_enabled = false
active_watch_count = 1
finding_count = 0
alert_count = 0
degraded_source_count = 1
limitations =
  DEGRADED_SOURCES_PRESENT
  NO_PERSISTED_COVERAGE_ASSESSMENT
```

The persistent owner-operation switch was **not** enabled. The P22.1 authorization applied only to the bounded one-shot session.

## Semantic / intelligence-utility limitation

Because the collection produced zero items:

- live analysis runs: 0;
- live analysis claims: 0;
- operational findings: 0;
- persisted coverage snapshots: 0;
- canonical P13 semantic decisions from this pilot: 0;
- verification-yield impact: `NOT_OBSERVED`;
- contradiction-workload impact: `NOT_OBSERVED`;
- forecast-input impact: `NOT_OBSERVED`.

P22.1 therefore validates operational boundedness and fail-closed observability, **not** semantic quality or factual-verification improvement.

P13.5/P13.6 remain the sole canonical factual-verification authority.

## Deployed runtime containment

The historical deployed runtime was inspected but not mutated:

```text
DEPLOYED_SHA_BEFORE = b31b2136b5fe982d0b63b0135479b1549041906c
DEPLOYED_SHA_AFTER  = b31b2136b5fe982d0b63b0135479b1549041906c
SERVICE_BEFORE = active
SERVICE_AFTER  = active
SERVICE_ENABLED = enabled
SERVICE_RESTART = false
DEPLOYED_DATA_READ_BY_KGMOPS = false
```

The pilot ran only under the isolated project-local root. No production/live cutover occurred.

## Preserved gates

```text
WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED
PERSISTENT_OWNER_OPERATION = NOT_ACTIVATED
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
PUBLIC_INGRESS = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
PLUGIN_PUBLICATION = NOT_ACTIVATED
```

## Final state

```text
P22_1_STATE = VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION
P22_1_GATE = P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED
P22_2_STATE = VALIDATED_WITH_ONBOARDING_BLOCKERS
P22_3_STATE = BLOCKED_ON_OWNER_GATE
NEXT_GATE = P22_3_WAVE_B_ONBOARDING_OWNER_DECISION_REQUIRED
```
