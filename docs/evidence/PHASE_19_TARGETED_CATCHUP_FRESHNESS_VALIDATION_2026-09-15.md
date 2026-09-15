# Phase 19 Targeted Catch-up and Freshness Validation — 2026-09-15

Status: `EXECUTED / NOT_PASSED / REMEDIATION_REQUIRED`
Contract: `docs/implementation/PHASE_19_REBASELINED_ACCEPTANCE_CONTRACT.md`
Canonical base: `a3ba31bcb3519908f6fa02d37a77a931c418d9d7`
Deployed owner-local candidate: `b31b2136b5fe982d0b63b0135479b1549041906c`
Target host: `kgm-e4-owner-pilot`

## Scope and change boundary

This was a bounded validation only. It performed no deployment, service restart, canonical runtime database mutation, scheduler/cadence change, Tailscale trust change, shared-runtime activation, paid-resource authorization, or migration creation.

The owner-local service was observed `active (running)` and the deployed repository SHA remained exactly `b31b2136b5fe982d0b63b0135479b1549041906c`.

## Selected documented gap

The existing Attempt 2 audit artifact records the largest qualifying scheduler/evidence gap as:

```text
PRE_GAP_OBSERVATION_UTC  = 2026-09-11T23:24:56Z
POST_GAP_OBSERVATION_UTC = 2026-09-12T07:45:10Z
GAP_SECONDS              = 30014
GAP_HOURS                = 8.337222222222222
```

This proves gap detection. It does not by itself prove a canonical application-data collection gap, because the GitHub health-observation scheduler and the continuously running owner-local collector are separate mechanisms.

## Exact deployed-code gap replay

The exact deployed code was exercised against an isolated temporary project-local database, using the documented 30,014-second gap duration and the runtime's configured live adapters. The production database was not touched.

At `2026-09-15T08:47:05Z`:

```text
DUE_AFTER_GAP = True
TICK_EXECUTION_COUNT = 1
EXECUTION_STATUS = COMPLETED
EXECUTION_ERROR = null
```

The live collection result was:

```text
COLLECTION_STATUS = PARTIAL
ITEM_COUNT = 0
SOURCE_SUCCESS_COUNT = 1
SOURCE_FAILURE_COUNT = 1

consilium-press-releases = SUCCESS / 0 matching items
gdelt-doc-2              = FAILED / "GDELT response does not contain an articles list"
```

A direct diagnostic call immediately afterward returned `{}` from GDELT, and repeated bounded diagnostic queries then returned HTTP `429`. This is retained as source-availability evidence, not treated as evidence that no geopolitical event occurred.

The deployed GDELT adapter is configured with a rolling `timespan=24h`. The selected 8.337-hour interval is therefore within the adapter's nominal historical retrieval window, but live catch-up could not be demonstrated because the source did not provide usable article data during this validation.

## Freshness interpretation

Existing P12.5 semantics remain authoritative:

- a successful Consilium acquisition with zero bounded watch matches leaves content freshness `UNKNOWN`; collection time must not be promoted into content freshness;
- a failed/unavailable source cannot be promoted into a freshness PASS;
- source operational failure does not imply event absence.

Therefore current post-gap data freshness cannot be claimed as PASS from this run.

## Temporal-gap representation audit

The active unattended/live path was inspected in the deployed candidate:

```text
unattended_runner.py
unattended_service.py
operational_monitoring.py
live_operational_cycle.py
live_sources.py
```

Observed behavior:

- overdue watches become due and execute once when the supervisor is running;
- source collection attempts and failures are persisted;
- raw-item ingestion uses stable IDs and `ON CONFLICT ... DO NOTHING` semantics;
- GDELT uses a rolling 24-hour query window;
- the live/unattended path does not persist the scheduler/application gap interval that triggered recovery;
- the live/unattended path does not mark items as `recovered`, `current`, or associated with a specific missed interval;
- the live/unattended path does not automatically create a temporal coverage limitation for the portion of a gap that a source cannot backfill.

General coverage-reporting machinery exists elsewhere in the codebase, but no integration from the deployed live/unattended path to that machinery was found for this recovery scenario. Therefore a non-recoverable temporal interval would not currently be made explicit by the live path itself.

## Deterministic deployed-candidate validation

Relevant exact-deployed tests were executed directly on `kgm-e4-owner-pilot`:

```text
pytest:
  tests/test_live_operational_cycle.py
  tests/test_live_end_to_end.py
  tests/test_source_collection_attempts.py
  tests/test_unattended_service.py

RESULT = 17 passed, 1 non-functional pytest cache permission warning
```

These tests confirm live-cycle terminal behavior, source-attempt audit, unattended supervisor behavior, and same-collection end-to-end idempotency. They do not substitute for a successful integrated catch-up against a recoverable live source.

## Security/runtime-control evidence

Current direct observation plus reusable P19 evidence supports:

```text
SERVICE_ACTIVE = PASS
DEPLOYED_SHA_STABLE = PASS
RUNTIME_DB_READ_BY_KGMOPS = DENIED
ARBITRARY_ROOT_ESCALATION = DENIED (reused bounded-control evidence)
DEPLOYMENT_DURING_VALIDATION = NO
SERVICE_RESTART_DURING_VALIDATION = NO
```

The production data directory remains intentionally unreadable to `kgmops`. No new read privilege was introduced merely to make the validation pass.

## Required gate fields

```text
P19_GAP_DETECTION = PASS
P19_COLLECTION_RESUME = PARTIAL_EVIDENCE / CANONICAL_SELECTED_GAP_COLLECTION_WATERMARK_NOT_OBSERVED
P19_APPLICATION_LEVEL_CATCH_UP = NOT_PROVEN
P19_UNRECOVERABLE_GAPS_EXPLICIT = FAIL
P19_POST_GAP_DATA_FRESHNESS = NOT_PROVEN
P19_DEDUP_IDEMPOTENCY_AFTER_CATCH_UP = COMPONENT_PASS / INTEGRATED_CATCH_UP_NOT_PROVEN
P19_SECURITY_INVARIANTS = PASS
```

Overall:

```text
P19_TARGETED_CATCH_UP_AND_FRESHNESS_VALIDATION = NOT_PASSED
P19_CLOSURE = NOT_ELIGIBLE
P20_OPERATIONAL_EXECUTION = NOT_STARTED
P19_STRICT_CONTINUITY_GATE = RETIRED / REMAINS_NON_BLOCKING
ATTEMPT_4 = NOT_REQUIRED
MULTIDAY_SOAK = NOT_REQUIRED
```

## Minimal remediation required before re-validation

The next implementation should be narrowly scoped to the rebaselined objective, not to continuity:

1. persist a recovery interval/watermark when a watch resumes after being overdue;
2. allow a source adapter to declare bounded historical-retrieval capability and the interval actually requested/covered;
3. persist/report any uncovered portion as an explicit temporal coverage limitation;
4. propagate recovery/current/missing coverage semantics into downstream analytical/reporting state;
5. retain current stable-ID dedup/provenance behavior;
6. re-run the targeted validation using a recoverable live source when it is operational, with source-specific freshness evaluated fail-closed.

No new multi-day soak is required after this remediation.