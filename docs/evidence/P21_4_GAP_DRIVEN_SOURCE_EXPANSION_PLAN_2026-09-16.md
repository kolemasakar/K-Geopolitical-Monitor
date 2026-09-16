# P21.4 Gap-Driven Source Expansion Plan

Date: 2026-09-16
Status: `IMPLEMENTED / VALIDATION_PENDING`
Gate candidate: `P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED`

## Deterministic planning baseline

```text
TARGET_CELLS = 33
ADEQUATE_EXCLUDED = 1
GAP_CELLS = 32
MINIMUM_NEW_SOURCE_PATH_DEFICIT = 49
MINIMUM_HEALTHY_SOURCE_DEFICIT = 49
ORIGIN_EVIDENCE_DEFICIT_FROM_CONFIRMED_LOWER_BOUND = 54
```

The 49-path figure is a deterministic minimum source-path deficit against the approved P21.0 thresholds. It is not an instruction to onboard 49 sources and does not imply that every candidate will qualify. Existing unresolved provenance may later reduce origin-evidence deficits without adding a source path.

## Priority waves

| Wave | Gap cells | Path deficit | Healthy deficit | Origin-evidence deficit* |
|---|---:|---:|---:|---:|
| `A_CRITICAL_REQUIRED` | 2 | 2 | 2 | 3 |
| `B_HIGH_REQUIRED` | 9 | 13 | 13 | 16 |
| `C_STANDARD_REQUIRED` | 14 | 27 | 27 | 28 |
| `D_WATCH_REQUIRED` | 1 | 1 | 1 | 1 |
| `E_OPTIONAL_STANDARD` | 4 | 4 | 4 | 4 |
| `F_OPTIONAL_WATCH` | 2 | 2 | 2 | 2 |

*Origin-evidence deficit is measured from the currently confirmed independent-origin lower bound. It is not a count of definitely new organizations required.

## Planning rules

- `REQUIRED` cells precede `OPTIONAL` cells; within required cells, approved criticality orders `CRITICAL -> HIGH -> STANDARD -> WATCH`.
- `MISSING_EXPECTED_COVERAGE` cells require candidate discovery; `THIN` cells require only the measured deficit; `DEGRADED_COLLECTION` first requires repair or an alternate public/free path.
- Public/free access is the default discovery constraint for P21.4. No paid provider or secret-dependent source is authorized.
- A candidate must match the policy cell geography/language/source-type contract and pass provenance, terms, technical-feasibility, health and freshness review before any adequacy credit.
- Publisher/domain/language/path counts do not create independent-origin credit. Unresolved provenance stays unresolved.
- Local-language evidence is not replaced by English when the approved policy requires the local language.
- P13.5/P13.6 remain the factual-verification authority; coverage planning cannot promote a claim to `VERIFIED`.

## Execution boundary

`P21.4 = PLAN_AND_CANDIDATE_DISCOVERY_ONLY`. No registry activation, live ingest change, deployment, service restart, paid provider, migration 033, Plugin publication or production activation is authorized.

Any live source onboarding is reserved for P21.5 and requires a separate explicit owner decision.

## Next gate

After CI validation, close P21.4 at `P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED` and stop at the P21.5 owner activation gate.
