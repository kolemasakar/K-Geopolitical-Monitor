# P22.3 B1 — Controlled High-Priority Onboarding Result

Status: `VALIDATED_WITH_PARTIAL_ONBOARDING`

Owner-authorized B1 was evaluated from exact canonical main `445699eb8b60fec3a70cbbfb5d831ffb35aa26a3` on `kgm-e4-owner-pilot` (`aarch64`).

## Measured live-health result

- OFAC Recent Actions: `SUCCESS / 15 items` -> health behavior `PASS`;
- White House Briefings & Statements: `SUCCESS / 13 items` -> health behavior `PASS`;
- UK Sanctions List: `BLOCKED`; official CSV response measured about `49,928,338 bytes`, exceeding the bounded `10,000,000` byte transport limit;
- Government of Russia News: `BLOCKED`; owner-node transport timed out.

Collector success does not create content-freshness credit when publication timestamps are not observed. P20.4 truth/latency boundaries remain preserved.

## P20.5 / repository decision

Only two sources satisfy the full P20.5 readiness contract in this cohort:

- `ofac-recent-actions-en` -> `ELIGIBLE_NOT_ACTIVE` -> P22.3 repository activation `ACTIVE`;
- `white-house-briefings-en` -> `ELIGIBLE_NOT_ACTIVE` -> P22.3 repository activation `ACTIVE`.

Blocked and not activated:

- `uk-sanctions-list-en` -> `BLOCKED / BOUNDED_RESPONSE_LIMIT`;
- `russian-government-news-ru` -> `BLOCKED / TRANSPORT_TIMEOUT`.

Repository activation is not deployed-runtime activation. `live_activation_authorized=false` and `live_activation_state=NOT_ACTIVE` remain true for all four P20.5 records.

## Containment

Before and after the probe:

- deployed SHA: `b31b2136b5fe982d0b63b0135479b1549041906c`;
- service: `active`;
- runtime deployment: none;
- service restart: none;
- persistent owner operation: not activated.

Automatic factual independence credit remains `0`. P13.5/P13.6 remain factual-verification authority.

Validation evidence:

- PR #140;
- merge anchor `9c730ccd4a646aecbd0ada13b972701b65596adf`;
- CI run `35451792014`, job `105920115982`;
- `1343 passed in 107.57s / SUCCESS`.

Gate: `P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED`.

Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED.md`.

Next gate: `P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED`.
