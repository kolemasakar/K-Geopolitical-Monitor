# Current K-Geopolitical Monitor Handoff

Status: `AUTHORITATIVE_POINTER / P20_6_READY_TO_BEGIN`

Canonical transition state:
`PHASE_20_P20_5_VALIDATED_P20_6_READY`

Read first:

1. `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-16_P20_5_SOURCE_ONBOARDING_CONTRACT_VALIDATED.md`
2. `docs/implementation/P20_5_SOURCE_ONBOARDING_CONTRACT.md`
3. `docs/evidence/P20_5_SOURCE_ONBOARDING_BASELINE_2026-09-16.json`
4. `docs/contracts/p20_5_source_onboarding.schema.json`
5. `docs/implementation/PHASE_20_SOURCE_COVERAGE_COLLECTION_QUALITY_DESIGN_SPEC.md`

P20.5 implementation PR: `#103`
P20.5 merge anchor: `320eac5ea23c427b0db1a2ab276b366af9dbfdb7`
Validation: GitHub CI run `35098764695` / CI `#1532` / `1227 passed in 153.91s / SUCCESS`.

Next gate:
`P20_6_COVERAGE_EVALUATION_REPORTING_VALIDATED`

P20.6 owns reproducible machine-readable and operator-readable coverage evaluation/reporting. It must compose P20.2 coverage cells/policy, P20.3 independence/monoculture evidence and P20.4 health/latency/missing-source evidence without inventing values where provenance or fresh health observations are absent.

Required report sections include global summary, region/language/source-type gaps, monoculture warnings, stale/failed sources, latency outliers, missing expected sources and changes since previous report. `UNKNOWN` must remain distinct from a confirmed gap or adequate coverage.

Coverage evaluation remains operational/source-network evidence and cannot promote claim verification. P13.5/P13.6 remains factual-verification authority.

No runtime deployment, service restart, live-source expansion, migration 033, paid-resource authorization, or shared-runtime activation is pending for the handoff.
