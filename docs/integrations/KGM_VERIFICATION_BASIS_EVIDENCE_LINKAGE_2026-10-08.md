# KGM verification basis evidence linkage — 2026-10-08

## Decision

**KGM_VERIFICATION_BASIS_EVIDENCE_LINKAGE = PASS_WITH_EVIDENCE_BOUND_REVISIONS**

Exact validated code SHA: `c87a48c9e489da200acbfc145065945f947c28ff`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, change the canonical Phase 23 strategic gate, or authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Problem addressed

The previous immutable revision lineage preserved history but a state change could still rely only on free-text rationale.

This checkpoint adds an immutable evidence-basis layer so a later VERIFY / REJECT / DEFER / REVOKE action can be bound to explicit evidence references.

## Verification basis artifact

Schema:
`kgm.verification.basis.v1`

A basis artifact binds:
- request id;
- consumer id;
- result id;
- corroboration id;
- exact result artifact SHA-256;
- explicit actor and policy version;
- UTC basis creation time;
- basis type;
- bounded rationale;
- one to twenty explicit evidence references.

Basis types:
- `CONFIRMATION`
- `CONTRADICTION`
- `CORRECTION`
- `SOURCE_REVISION`

Each evidence reference includes:
- reference id;
- source id;
- public HTTPS URL;
- observed UTC timestamp;
- content SHA-256;
- bounded summary.

Evidence timestamps later than the basis creation time are denied.

Basis artifacts are immutable and idempotent under exact replay.

## Evidence-bound revision v2

Schema:
`kgm.verification.revision.v2`

Every v2 revision binds to:
- exact superseded decision/revision id and SHA-256;
- exact immutable result artifact SHA-256;
- exact immutable basis id and SHA-256.

Action/basis policy:
- VERIFY requires CONFIRMATION or SOURCE_REVISION basis;
- REVOKE requires CONTRADICTION, CORRECTION or SOURCE_REVISION basis;
- REJECT requires CONTRADICTION, CORRECTION or SOURCE_REVISION basis;
- DEFER may use any recognized basis type.

Existing verification eligibility and lineage protections remain in force.

## Controlled lineage validation

Validated chain:

`VERIFY → CONTRADICTION basis → REVOKE → CONFIRMATION basis → VERIFY`

The chain preserves:
- original decision artifact;
- adverse evidence basis;
- revocation revision;
- later confirmation basis;
- re-verification revision.

No artifact is deleted or rewritten.

Negative validation includes:
- wrong basis SHA denied;
- future evidence timestamp denied;
- confirmation basis cannot revoke;
- immutable basis conflict denied;
- prior lineage and actor constraints remain active.

## Real-event policy

The existing real owner-pilot verification `verify-chagos-001` was not revoked or revised because no new contradictory or corrective real evidence was established during this checkpoint.

The evidence-bound revision mechanism was validated with controlled fixtures instead of manufacturing an unsupported real-world state change.

## Validation

Targeted basis/revision/decision/boundary suite:
- **24/24 PASS**

Selected exchange/research regression:
- **226/226 PASS in 3.64 s**

## Result

KGM verification-state changes can no longer rely solely on rationale. Revision v2 requires an immutable evidence basis with explicit provenance and content digests.

Next technical track:
`VERIFICATION_EFFECTIVE_STATE_RESOLUTION`

The next step must deterministically resolve the current effective verification state from the immutable decision/revision chain while detecting missing links, forks, cycles, integrity failures and stale/unapplied evidence.
