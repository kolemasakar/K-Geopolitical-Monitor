# P22.4 — Operational Coverage Rebaseline Result

Status: `VALIDATED_WITH_MEASURED_DEGRADATION`

Gate: `P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED`

Canonical base: `5ed788f54af816f06568981bd58b34f6e447b1b4`.

## Structural result

Post-Wave-A baseline:

```text
OVERALL  = 1 ADEQUATE / 2 DEGRADED_COLLECTION / 20 MISSING_EXPECTED_COVERAGE / 10 THIN
REQUIRED = 1 ADEQUATE / 1 DEGRADED_COLLECTION / 20 MISSING_EXPECTED_COVERAGE / 5 THIN
```

After P22.3 B1 partial onboarding:

```text
OVERALL  = 1 ADEQUATE / 4 DEGRADED_COLLECTION / 18 MISSING_EXPECTED_COVERAGE / 10 THIN
REQUIRED = 1 ADEQUATE / 3 DEGRADED_COLLECTION / 18 MISSING_EXPECTED_COVERAGE / 5 THIN
```

Required missing coverage improves by `-2`; adequate-cell count does not change.

## Changed cells

### `global.en.sanctions_regulatory`

`MISSING_EXPECTED_COVERAGE -> DEGRADED_COLLECTION`

- repository-active path: `ofac-recent-actions-en`;
- collector health: PASS;
- content-freshness credit: none;
- confirmed publication-stream origin group: `official:us-treasury-ofac`;
- UK Sanctions List candidate remains blocked by the bounded response-size limit.

### `united_states.en.official_government`

`MISSING_EXPECTED_COVERAGE -> DEGRADED_COLLECTION`

- repository-active path: `white-house-briefings-en`;
- collector health: PASS;
- content-freshness credit: none;
- confirmed publication-stream origin group: `official:us-white-house`.

The cells do not become `THIN` or `ADEQUATE` because P22.3 did not observe publication-time freshness. Fail-closed operational coverage therefore preserves collection degradation.

## Unchanged blocker

`russia.ru.official_government` remains `MISSING_EXPECTED_COVERAGE` because `russian-government-news-ru` failed the owner-node health probe with `TRANSPORT_TIMEOUT` and was not repository-activated.

## Provenance / truth boundary

- repository-active source-path delta: `+2`;
- collector-health PASS path delta: `+2`;
- healthy/fresh path delta: `0`;
- confirmed source-network origin-group lower-bound delta: `+2`;
- automatic factual independence credit delta: `0`;
- P13.5/P13.6 remain factual-verification authority.

This is a structural operational-coverage improvement, not evidence that the corresponding underlying claims are true.

## Runtime containment

No deployed runtime mutation, service restart, persistent owner-operation activation, paid/shared dependency, migration 033, production/live cutover or Plugin publication is authorized or performed.

Next gate: `P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED`.
