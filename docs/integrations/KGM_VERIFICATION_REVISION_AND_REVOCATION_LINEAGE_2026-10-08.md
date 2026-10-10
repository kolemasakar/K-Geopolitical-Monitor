# KGM verification revision and revocation lineage — 2026-10-08

## Decision

**KGM_VERIFICATION_REVISION_AND_REVOCATION_LINEAGE = PASS_WITH_IMMUTABLE_HISTORY**

Exact validated code SHA: `d428173e7ac947a627b950b89f9893de4a105faa`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, change the canonical Phase 23 strategic gate, or authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Lineage model

Verification revisions are separate immutable artifacts:

`kgm.verification.revision.v1`

A revision:
- references the exact request, consumer, result and corroboration target;
- supersedes exactly one prior verification decision or revision;
- binds to the exact SHA-256 of the superseded artifact;
- binds to the exact immutable research result artifact SHA-256;
- requires an explicitly authorized actor;
- requires a later UTC timestamp than the superseded artifact;
- requires a bounded rationale.

Supported lineage actions:
- `VERIFY`
- `REJECT`
- `DEFER`
- `REVOKE`

## Immutability and fork protection

Earlier decisions and revisions are never deleted or rewritten.

Rules:
- exact replay of the same revision is idempotent;
- conflicting content for the same revision id is denied;
- two different revisions cannot supersede the same prior artifact;
- self-reference is denied;
- superseded artifact hash mismatch is denied;
- non-monotonic timestamps are denied.

Therefore the lineage is a single auditable chain rather than a mutable latest-state file.

## Effective state

A lineage revision produces an effective overlay:

- VERIFY → VERIFIED
- REJECT → DISPUTED
- DEFER → UNVERIFIED
- REVOKE → UNVERIFIED

REVOKE is allowed only when the superseded effective state is VERIFIED.

A later VERIFY may supersede a valid revocation only if the immutable corroboration target remains verification-eligible under the bound result.

## Validation

Targeted verification lineage/decision/boundary/result suite:
- **29/29 PASS**

Selected exchange/research regression:
- **220/220 PASS in 3.47 s**

Covered negative cases:
- lineage fork denied;
- wrong prior artifact hash denied;
- non-monotonic revision denied;
- REVOKE of a non-VERIFIED lineage denied;
- conflicting revision replay denied.

Covered positive chain:

`explicit VERIFY → immutable REVOKE → later explicit VERIFY`

All three artifacts remain present and independently auditable.

## Live real-event policy

The previously created real owner-pilot decision:

`verify-chagos-001`

was **not revoked or revised**, because no new contradictory evidence or correction was established in this checkpoint.

This is intentional: the lineage mechanism was validated with controlled fixtures rather than manufacturing a factual revocation without evidence.

## Result

KGM now preserves the full verification history required for later corrections and source revisions without erasing prior decisions.

Next technical track:
`VERIFICATION_BASIS_EVIDENCE_LINKAGE`

The next step must bind a revision/revocation rationale to explicit new evidence or correction artifacts, so that a later verification-state change cannot rely on free-text rationale alone.
