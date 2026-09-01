# VERIFICATION_MODEL
Verification framework for K-Geopolitical Monitor.

Version: 2.0
Status: APPROVED / BASELINE_IMPLEMENTED_AND_VALIDATED

## Principle

Verification applies to claims/evidence and must remain separate from forecast probability, graph inference, coverage metrics, presentation and source reputation.

The current executable verification layer is a validated baseline, not yet the richer semantic verification/provenance engine planned for ROADMAP v4 Phase 13.

## Verification States

Canonical baseline states include:
- DETECTED;
- DEVELOPING;
- PARTLY_VERIFIED;
- VERIFIED;
- DISPUTED;
- UNVERIFIABLE.

## Confidence

Confidence and verification status are separate concepts.

A presentation confidence value must not hide its limitations or be treated as proof of verification. Phase 13 is planned to decompose verification/confidence dimensions further.

## Evidence Independence

Permanent rules:
- publisher/publication is not automatically the underlying origin;
- adapter/domain count is not automatically independent-origin count;
- same-origin duplicates do not strengthen verification;
- reposts, syndication, translations and citations do not create independent corroboration;
- an official statement establishes that the actor made the statement, not automatically that the substantive claim is true;
- discovery/index services do not corroborate a linked claim merely by discovering it.

## Source Reputation Boundary

Source reputation/status is analytical context and may affect review burden. `COMPROMISED` does not automatically make every new claim FALSE and source reputation cannot directly determine claim truth.

## Graph Boundary

Graph inference/relationship confidence is not source evidence and cannot promote verification or independent-origin count.

## Forecast Boundary

`raw_probability`, `calibrated_probability` and `scenario_confidence` are forecast semantics. None can promote present-tense factual verification.

## Coverage Boundary

`coverage_ratio` and `coverage_confidence` describe configured monitoring coverage. Coverage confidence cannot promote factual verification confidence, and `GLOBAL` does not prove exhaustive global coverage.

## Reporting / UI Boundary

API, dashboard, reports, private GPT and other presentation/orchestration surfaces must project canonical verification state without strengthening it.

## Reproducibility Boundary

Instrumented exact search/query/cut-off data may be persisted where available. Missing/uninstrumented history remains `NOT_INSTRUMENTED` and must not be reconstructed and labeled exact.

Unavailable persisted backend state cannot be replaced by ad hoc public-web research.

## Current Analytical Limitation

The current live claim grouping/verification implementation is intentionally recognized as coarse relative to the epistemic policy: title/host-level shortcuts remain in the baseline and do not prove full underlying-origin independence or semantic claim equivalence.

ROADMAP v4 Phase 13 is approved sequentially to implement richer semantic claim identity, provenance/origin relationships, typed contradictions and verification v2, but Phase 13 has not started.

## Current State

- verification policy boundary: `APPROVED`;
- executable verification baseline: `IMPLEMENTED / BASELINE_VALIDATED`;
- truth-boundary regressions: validated across the current engineering line;
- semantic verification/provenance v2: `PLANNED_PHASE_13 / NOT_STARTED`;
- P12.0 verification logic mutation: `NONE`.
