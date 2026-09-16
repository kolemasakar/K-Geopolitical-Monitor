# P21.3 Operational Coverage Adequacy Baseline Result

Date: 2026-09-16
Status: `VALIDATED`
Gate: `P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_VALIDATED`

## Inputs

- approved P21.0 33-cell target policy;
- P20 source inventory/taxonomy and observed matrix;
- P21.1 source provenance resolution;
- P21.2 fresh owner-local health baseline.

## Deterministic result

```text
TARGET_CELLS = 33
REQUIRED_CELLS = 27
OPTIONAL_CELLS = 6
ADEQUATE = 1
THIN = 10
MISSING_EXPECTED_COVERAGE = 21
DEGRADED_COLLECTION = 1
UNKNOWN = 0
```

Required cells:

```text
ADEQUATE = 1
THIN = 5
MISSING_EXPECTED_COVERAGE = 21
```

Optional cells:

```text
THIN = 5
DEGRADED_COLLECTION = 1
```

The only `ADEQUATE` cell is `eu.en.international_organization`. It has three governed source paths, two confirmed distinct institutional origin groups, two sources meeting the P21.0 cell health/freshness thresholds, one failed Parliament path, a stale/failed share of 1/3, and a fail-closed dominant-origin upper bound of 2/3, below the policy maximum 0.75.

`global.multi.public_osint` remains `DEGRADED_COLLECTION` because the fresh GDELT measurement returned HTTP 429. GDELT receives no independence credit.

Required cells with zero matching governed source paths are classified `MISSING_EXPECTED_COVERAGE`. Required cells that have some coverage but cannot meet the minimum source-count threshold are `THIN`. Unknown origin never supplies independence credit.

## Delta from Phase 20 closure

Phase 20 closed with 17 observed cells, all `UNKNOWN`, because target policy was unset, source-level origin evidence was unresolved, and current health was unmeasured. P21.3 does not reinterpret that historical closure. It evaluates the separately owner-approved P21.0 target policy against the new P21.1/P21.2 evidence and therefore exposes confirmed adequacy and confirmed gaps for the first time.

## Epistemic boundary

Operational coverage adequacy is not factual verification. Health, freshness, source count, geography/language coverage, and origin topology cannot promote a claim to `VERIFIED`. P13.5/P13.6 remain the factual-verification authority.

## Safety boundary

P21.3 performs repository/evidence evaluation only. It does not authorize or perform:

- live source expansion or onboarding;
- runtime deployment or service restart;
- paid/shared provider use;
- migration `033`;
- Plugin build/publication;
- production/live activation.

Validation: GitHub CI #1682 / run `35131568836`, job `104913591458`: `1271 passed in 99.74s / SUCCESS`. Merge anchor: `2e0666ed1f2a0b16d0ec3b4dda664664ce151f04`. Formal closure advances the next executable gate to P21.4 without authorizing live source onboarding.
