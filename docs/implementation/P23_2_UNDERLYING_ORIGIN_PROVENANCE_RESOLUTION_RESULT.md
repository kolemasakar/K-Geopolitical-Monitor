# P23.2 — Underlying-Origin / Provenance Resolution Result

Date: 2026-09-20
Status: `VALIDATED_WITH_ZERO_UNDERLYING_ORIGIN_RESOLUTION`
Gate: `P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED`

## Result

The exact Phase-22 semantic cohort remains 28 publication-attribution claims:

- OFAC: 15;
- White House: 13;
- `ATTRIBUTION_ONLY`: 28;
- current resolved underlying origins: 0;
- current unresolved underlying origins: 28;
- semantic independence assessments: 0;
- automatic factual-independence credit: 0.

P23.2 adds a read-only `UnderlyingOriginResolutionObserver` that explicitly separates first-party publication provenance from underlying-origin resolution.

A matching first-party publication host is contextual provenance only. It does not resolve the underlying origin and does not create independence credit.

A claim is counted as resolved only when the current `UNDERLYING_ORIGIN` role points to a concrete provenance entity with `OBSERVED` attribution. `ASSERTED`, `UNKNOWN/UNRESOLVED`, and `MIXED` remain non-resolved.

## Decision

P23.2 is validated because the project can now deterministically measure origin resolution without publisher/domain shortcuts. The measured current result is zero resolved origins, not an uplift claim.

No source activation, runtime mutation, resource-limit relaxation, production/live change, persistent owner operation, migration 033, paid/shared dependency or Plugin publication occurs.

Next gate: `P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED`.
