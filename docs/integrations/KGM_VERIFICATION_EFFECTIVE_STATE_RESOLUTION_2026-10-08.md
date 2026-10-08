# KGM verification effective-state resolution — 2026-10-08

## Decision

**KGM_VERIFICATION_EFFECTIVE_STATE_RESOLUTION = PASS_WITH_STALENESS_SIGNAL**

Exact validated code SHA: `2cdf937201990d32ca59efd83c145c39e1330e33`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, change the canonical Phase 23 strategic gate, or authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Resolver

Added deterministic resolution of the effective verification state from immutable verification artifacts.

The resolver:
- requires exactly one root verification decision for a corroboration target;
- walks the single supersedes chain to the current head;
- validates decision/revision artifact integrity;
- detects missing superseded links;
- detects lineage forks;
- detects cycles/disconnected artifacts;
- enforces monotonic timestamps;
- validates evidence-bound v2 revision basis SHA and target binding;
- resolves the current effective state as VERIFIED / DISPUTED / UNVERIFIED.

## Evidence staleness signal

The resolver also inspects immutable verification-basis artifacts.

It reports:
- all unapplied basis artifacts for the corroboration target;
- basis artifacts created after the current lineage head;
- `effective_state_stale = true` when post-head evidence exists but has not yet been applied through a revision.

This does not automatically change verification state. It signals that the currently resolved state requires explicit review.

## Real owner-pilot resolution

The real owner-pilot target:

`corr-a7d18a9a3186cd5a9d1d99c4`

resolved as:

- root decision: `verify-chagos-001`;
- head artifact: `verify-chagos-001`;
- effective verification: `VERIFIED`;
- lineage length: 1;
- decision artifact SHA-256: `7a88529f673d3907a1b45936a8e0f4a8b9b04681e19840313eb76e27b8a29c41`;
- unapplied basis: none;
- post-head basis: none;
- effective state stale: false.

No synthetic revision/revocation was applied to this real target.

## Controlled validation

Validated positive chain:
`VERIFY → evidence-bound REVOKE → evidence-bound VERIFY`

The resolver returns the latest effective state and full ordered lineage.

Negative coverage includes:
- multiple independent root decisions fail closed;
- manually introduced fork detected;
- missing lineage link detected;
- integrity and basis-linkage checks retained.

A post-head unapplied evidence basis correctly marks the current state stale without mutating it.

## Validation

Targeted resolver/basis/revision/decision suite:
- **24/24 PASS**

Selected exchange/research regression:
- **231/231 PASS in 3.93 s**

## Result

KGM can now deterministically reconstruct the current verification state from immutable history instead of trusting a mutable status field.

Next technical track:
`INDEPENDENT_RESEARCH_READINESS_AUDIT_V2`

The next step is a consolidated audit of the complete owner-pilot research chain and remaining blockers before any readiness gate can be considered.
