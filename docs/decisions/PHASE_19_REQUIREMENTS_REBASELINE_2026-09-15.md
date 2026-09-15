# Phase 19 Requirements Rebaseline — Normal Monitoring vs Event Watch

Date: 2026-09-15
Status: `APPROVED / OWNER_REQUIREMENTS_REBASELINE`
Scope: K-Geopolitical Monitor (KGM)

## Owner requirement

Strict runtime/evidence continuity is **not** a baseline requirement of KGM.

The primary project objective is the quality and recoverability of the information-analysis product:

```text
COLLECT
→ VERIFY / CORROBORATE
→ NORMALIZE / DEDUPLICATE
→ SUMMARIZE
→ ANALYZE
→ ASSESS UNCERTAINTY
→ FORECAST
```

A temporary runtime or scheduler gap is acceptable when the system detects the gap, resumes collection, recovers the missed period where source capabilities permit, exposes unrecoverable gaps explicitly, and restores acceptable source/data freshness without silent material loss.

## Operating modes

### NORMAL MONITORING MODE — current project mode

Strict continuity is not a blocking acceptance criterion.

Blocking qualities are:

- required-source collection reliability;
- explicit gap detection;
- recoverability and catch-up where the source permits historical retrieval;
- explicit representation of unrecoverable gaps;
- source/data freshness and completeness visibility;
- provenance, verification/corroboration and deduplication integrity;
- separation of facts, assumptions and analytical judgments;
- uncertainty/confidence disclosure;
- preserved security and runtime-control invariants.

No universal maximum evidence-gap duration is a project-level PASS/FAIL rule in this mode.

### EVENT WATCH MODE — optional future capability

Strict or near-real-time continuity is justified only for a bounded watch where missing or materially delaying an expected event is unacceptable.

An Event Watch must define its own contract, including as applicable:

```text
polling cadence
maximum tolerated gap
alert latency
fallback sources
notification rules
watch start / expiry
```

`EVENT_WATCH_MODE` is **not active** for the current P19/P20 work and is not a prerequisite for normal KGM development.

## P19 supersession rule

This decision supersedes any earlier P19 acceptance language that made the following a global blocking gate:

```text
continuous evidence cadence
<= 7h maximum evidence gap
24h / 72h / 7d uninterrupted soak
```

Those rules remain valid only as historical contracts for the attempts executed under them. They are not deleted or rewritten retroactively.

Historical classification is preserved:

```text
P19_REAL_SOAK_ATTEMPT_1 = FAILED_CONTINUITY / HISTORICAL_EVIDENCE
P19_REAL_SOAK_ATTEMPT_2 = FAILED_CONTINUITY / HISTORICAL_EVIDENCE
P19_REAL_SOAK_ATTEMPT_3 = HISTORICAL_OLD_CONTRACT_EVIDENCE
```

These classifications do **not** imply a demonstrated KGM runtime failure. Existing evidence attributes the observed continuity failures to evidence/scheduler cadence rather than a demonstrated bounded-health or owner-local service failure.

## Rebaselined P19 acceptance

P19 is redefined around operational reliability of the information pipeline rather than uninterrupted evidence cadence.

Blocking P19 closure requirements are now:

```text
P19_RUNTIME_HEALTH = PASS
P19_GAP_DETECTION = PASS
P19_COLLECTION_RESUME = PASS
P19_APPLICATION_LEVEL_CATCH_UP = PASS
P19_UNRECOVERABLE_GAPS_EXPLICIT = PASS
P19_POST_GAP_DATA_FRESHNESS = PASS
P19_SECURITY_INVARIANTS = PASS
```

Already accumulated bounded health, access/control and gap evidence remains usable where it addresses these requirements.

The only remaining targeted validation required before closure is to demonstrate at application/data level that after a known gap the system resumes collection, catches up where source semantics allow, exposes any unrecoverable interval explicitly, and returns to acceptable freshness.

No deliberate multi-day soak is required for that validation.

## Current P19 status

```text
P19_STRICT_CONTINUITY_GATE = RETIRED
ATTEMPT_4 = NOT_REQUIRED
MULTIDAY_SOAK = NOT_REQUIRED
EVENT_WATCH_CAPABILITY = FUTURE_OPTIONAL
APPLICATION_LEVEL_CATCH_UP = NOT_YET_PROVEN
POST_GAP_DATA_FRESHNESS = NOT_YET_PROVEN
P19_CLOSURE = PENDING_TARGETED_CATCH_UP_AND_FRESHNESS_VALIDATION
```

If the targeted validation passes, P19 may be formally closed and project execution may proceed to P20 without any additional strict-continuity soak.

## Change boundary

This requirements decision authorizes no runtime mutation by itself:

```text
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
CONTROL_PLANE_CHANGE = NO
TAILSCALE_TRUST_CHANGE = NO
PAID_RESOURCE_AUTHORIZATION = NO
SHARED_RUNTIME_ACTIVATION = NO
MIGRATION_033 = NO
```

The prior continuity-driven freeze is not a valid independent blocker after this rebaseline. Any remaining freeze must be justified by another explicit safety, data-integrity, runtime or deployment condition.
