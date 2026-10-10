# KGM explicit verification decision artifact — 2026-10-08

## Decision

**KGM_EXPLICIT_VERIFICATION_DECISION_ARTIFACT = PASS_WITH_IMMUTABLE_OVERLAY**

Exact validated code SHA: `f2ce95efc39cc5f8f70efcf8836577d4ad1f8119`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, change the canonical Phase 23 strategic gate, or authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Model

Verification is now a separate immutable policy artifact rather than a mutation of the immutable research result.

Schema:
`kgm.verification.decision.v1`

Required bindings:
- request id;
- consumer id;
- exact immutable result id;
- exact immutable result artifact SHA-256;
- corroboration id;
- explicit decision id;
- explicit actor id;
- request policy version;
- UTC decision timestamp;
- bounded rationale;
- decision action.

Supported actions:
- `VERIFY`
- `REJECT`
- `DEFER`

A `VERIFY` action is accepted only when the target corroboration group is already:
- `ELIGIBLE_FOR_EXPLICIT_VERIFICATION`;
- free of verification blockers;
- non-ambiguous;
- independently originated;
- structurally claim-agreeing.

The decision timestamp cannot predate the immutable research result.

The actor must be explicitly authorized for the request policy version.

## Immutability

Decision artifacts are stored separately under the owner-only research root.

Properties:
- same decision id + exact same canonical content → idempotent replay;
- same decision id + different content → immutable conflict;
- artifact is bound to the exact result artifact hash;
- symlink destinations are denied;
- base research result remains immutable.

The effective verification state is an overlay:
- VERIFY → VERIFIED
- REJECT → DISPUTED
- DEFER → UNVERIFIED

The worker does not invoke verification decisions automatically.

## Real owner-pilot explicit verification

A live eligible corroboration target from result:

`result-f1d23762fe3c577e4e28aa29`

was explicitly selected:

`corr-a7d18a9a3186cd5a9d1d99c4`

Eligibility at the immutable result boundary:
- ambiguous: false;
- claim relation: AGREES;
- independent-origin credit: true;
- origin assessment: DISTINCT_ORIGIN;
- origin groups: `gfz-geofon`, `usgs-neic`;
- source paths: GDACS, GFZ GEOFON, USGS;
- verification blockers: none.

Explicit owner-pilot decision:
- decision id: `verify-chagos-001`;
- action: `VERIFY`;
- effective verification overlay: `VERIFIED`;
- decision artifact SHA-256: `7a88529f673d3907a1b45936a8e0f4a8b9b04681e19840313eb76e27b8a29c41`.

An exact replay returned the same decision artifact SHA and effective state.

The immutable base research result was not rewritten.

## Validation

Targeted verification decision/boundary/v2/corroboration/worker suite:
- **32/32 PASS**

Selected exchange/research regression:
- **213/213 PASS in 3.23 s**

Negative coverage includes:
- ineligible corroboration cannot be VERIFY;
- unauthorized actor denied;
- wrong result-artifact hash denied;
- decision timestamp before result denied;
- conflicting replay denied.

## Result

KGM now has a complete bounded chain:

`real sources → normalized evidence → event correlation → origin assessment → corroboration → verification eligibility → explicit immutable verification decision`

No step before the final explicit decision can set an effective VERIFIED state.

Next technical track:
`VERIFICATION_REVISION_AND_REVOCATION_LINEAGE`

The next step must define how a later correction, source revision, or contradictory evidence can supersede or revoke a prior verification decision without deleting history.
