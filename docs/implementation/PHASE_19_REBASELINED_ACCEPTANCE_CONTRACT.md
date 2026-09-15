# Phase 19 Rebaselined Acceptance Contract

Date: 2026-09-15
Status: `ACTIVE / TARGETED_VALIDATION_EXECUTED / REMEDIATION_REQUIRED`
Authority: `docs/decisions/PHASE_19_REQUIREMENTS_REBASELINE_2026-09-15.md`
Latest evidence: `docs/evidence/PHASE_19_TARGETED_CATCHUP_FRESHNESS_VALIDATION_2026-09-15.md`

## Purpose

Validate that KGM can recover an analytically useful current state after an interruption. This contract deliberately does **not** validate uninterrupted scheduler/evidence cadence.

## Evidence that may be reused

Existing P19 evidence may satisfy unchanged controls when it demonstrates:

- owner-local runtime Path A availability;
- successful bounded health checks;
- preserved access/security invariants;
- gap detection;
- successful post-gap health without deployment or restart.

Attempts 1–3 remain historical evidence under their original strict-continuity contracts; their continuity result is not a blocker under this contract.

## Targeted validation sequence

Use a known/documented collection or scheduler gap. A new artificial outage is not required.

For the selected gap and representative configured sources:

1. identify the last valid pre-gap collection watermark/state;
2. identify the first successful post-gap collection execution;
3. prove collection resumed without relying on a continuity assumption;
4. for sources supporting historical retrieval, verify catch-up over the recoverable missed interval and check deduplication/idempotency;
5. for sources that cannot fully backfill, persist/report the unrecoverable interval explicitly rather than silently treating it as complete;
6. evaluate current source/data freshness using the source-specific freshness policy already applicable to that source class;
7. verify the analytical layer can distinguish recovered data, known missing data and current data;
8. confirm security/runtime-control invariants remain unchanged.

## Required PASS fields

```text
P19_GAP_DETECTION = PASS
P19_COLLECTION_RESUME = PASS
P19_APPLICATION_LEVEL_CATCH_UP = PASS
P19_UNRECOVERABLE_GAPS_EXPLICIT = PASS
P19_POST_GAP_DATA_FRESHNESS = PASS
P19_DEDUP_IDEMPOTENCY_AFTER_CATCH_UP = PASS
P19_SECURITY_INVARIANTS = PASS
```

### Catch-up semantics

`P19_APPLICATION_LEVEL_CATCH_UP = PASS` does not require every external source to expose historical data.

PASS requires:

- all recoverable configured source windows selected for the validation are backfilled to the extent supported by their source/API semantics;
- duplicate/replayed items do not create silent duplicate canonical information;
- any non-recoverable interval is explicitly represented as a coverage limitation or gap;
- no unsupported claim of completeness is emitted.

### Freshness semantics

`P19_POST_GAP_DATA_FRESHNESS = PASS` requires current data to meet the applicable source-specific freshness policy after recovery. It does not introduce a universal project-wide polling interval or universal maximum gap.

If a source is legitimately stale/unavailable, that state must remain explicit and must not be converted into a false global PASS for source completeness.

## Current validation result — 2026-09-15

The targeted validation was executed against the exact deployed owner-local candidate without mutating production runtime state.

```text
P19_GAP_DETECTION = PASS
P19_COLLECTION_RESUME = PARTIAL_EVIDENCE / CANONICAL_SELECTED_GAP_COLLECTION_WATERMARK_NOT_OBSERVED
P19_APPLICATION_LEVEL_CATCH_UP = NOT_PROVEN
P19_UNRECOVERABLE_GAPS_EXPLICIT = FAIL
P19_POST_GAP_DATA_FRESHNESS = NOT_PROVEN
P19_DEDUP_IDEMPOTENCY_AFTER_CATCH_UP = COMPONENT_PASS / INTEGRATED_CATCH_UP_NOT_PROVEN
P19_SECURITY_INVARIANTS = PASS

P19_TARGETED_CATCH_UP_AND_FRESHNESS_VALIDATION = NOT_PASSED
P19_CLOSURE = NOT_ELIGIBLE
```

Key findings:

- an overdue watch resumes execution under exact deployed code;
- deterministic live-cycle/idempotency tests pass;
- GDELT's configured rolling 24-hour window is nominally capable of covering the selected 8.337-hour gap, but the live source returned unusable/HTTP 429 responses during validation;
- Consilium acquisition succeeded with zero bounded watch matches, so content freshness remains `UNKNOWN` under existing P12.5 semantics;
- the deployed live/unattended path does not persist the recovery interval or explicitly represent an unrecoverable temporal portion as a coverage limitation;
- the production runtime database remains intentionally unreadable to `kgmops`, so no privilege expansion was introduced merely to produce closure evidence.

This result requires narrow application-level remediation. It does **not** reinstate strict continuity, Attempt 4, or a multi-day soak.

## Failure conditions

The targeted validation fails when any of the following occurs:

- collection does not resume;
- a recoverable interval is silently skipped;
- unrecoverable missing data is represented as complete;
- catch-up creates unresolved canonical duplicates or corrupts provenance;
- freshness is claimed without meeting the applicable source policy;
- post-gap analytics cannot distinguish known missing/limited coverage from current evidence;
- a security/runtime-control invariant regresses.

A scheduler/evidence gap by itself is **not** a failure under Normal Monitoring Mode.

## Closure rule

When all required PASS fields are evidenced:

```text
P19_TARGETED_CATCH_UP_AND_FRESHNESS_VALIDATION = PASS
P19_STRICT_CONTINUITY_GATE = RETIRED
P19_BETA_OPERATIONAL_STABILITY = REBASELINED_VALIDATED
P19_CLOSURE = ELIGIBLE
NEXT = FORMAL_P19_CLOSURE → P20
```

No Attempt 4, 24h/72h/7d continuity chain or additional multi-day soak is required.