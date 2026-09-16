# P21.0 — Coverage Policy & Criticality Validation Matrix

Date: 2026-09-16
Status: `IMPLEMENTATION_VALIDATION_READY / GLOBAL_POLICY_APPROVAL_PENDING`
Gate: `P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

| Requirement | Validation rule | Current result |
|---|---|---|
| Reuse P20.2 semantics | Existing requirement states, cell dimensions and source/origin/health thresholds remain present | PASS |
| Preserve P20 history | P20.0/P20.1/P20.2 evidence is read-only and unchanged | PASS |
| Policy authority explicit | `authority_state` is mandatory and constrained to `DRAFT/APPROVED/RETIRED` | PASS |
| Criticality explicit | Every target cell has an operational `criticality` | PASS |
| Freshness targets explicit | Collection and content freshness thresholds are distinct | PASS |
| Unobserved cells allowed | Target policy may define cells absent from observed matrix | PASS |
| Global macroregional baseline | Draft explicitly represents Europe, Middle East, East/Southeast/South/Central Asia, Caucasus, North/Sub-Saharan Africa, North/Latin America, Brazil, Oceania and GLOBAL cross-cutting classes | PASS |
| Priority country cells preserved | Ukraine, Russia and United States direct official/media requirements remain explicit rather than hidden inside broad regions | PASS |
| Language diversity explicit | Draft includes local/regional language targets and does not treat English or `multi` as universal substitutes | PASS |
| Cross-cutting source classes | Wire, sanctions/regulatory, economic/energy, research and public OSINT roles are represented separately | PASS |
| Global does not mean exhaustive | `default_requirement_state = UNSET`; unspecified cells remain unknown rather than implicitly adequate or not required | PASS |
| `UNSET` fail-closed | Default may remain `UNSET`; it cannot mean `NOT_REQUIRED` | PASS |
| Independence fail-closed | Independent-origin requirement cannot be satisfied by source/domain/language count | PASS |
| Truth boundary preserved | Coverage/criticality/health cannot promote P13 factual verification | PASS |
| Draft cannot drive canonical gap/adequacy | Only `APPROVED` policy may drive P21.3 canonical adequacy decisions | PASS |
| Live/runtime boundary | No live source, ingest, runtime, deployment, provider or migration mutation | PASS |
| Target policy approved | Explicit owner-approved target manifest exists | PENDING |

## Current draft

`docs/evidence/P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json`

Version: `0.2-draft-global-baseline`

The draft contains 33 target cells spanning 20 geography scopes and 15 language labels. This is a global operational baseline, not a claim of exhaustive country-by-country or language-by-language coverage.

## Gate rule

Contract implementation validation and policy authorization are separate evidence items.

The P21.0 gate remains **not granted** while the target manifest is `authority_state = DRAFT`.

The proposal is intentionally reviewable and non-operative. Its cells must not be treated as canonical gaps until separately approved.
