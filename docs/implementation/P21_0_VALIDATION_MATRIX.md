# P21.0 — Coverage Policy & Criticality Validation Matrix

Date: 2026-09-16
Status: `IMPLEMENTATION_VALIDATION_READY / POLICY_APPROVAL_PENDING`
Gate: `P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

| Requirement | Validation rule | Current result |
|---|---|---|
| Reuse P20.2 semantics | Existing requirement states, cell dimensions and source/origin/health thresholds remain present | PASS |
| Preserve P20 history | P20.0/P20.1/P20.2 evidence is read-only and unchanged | PASS |
| Policy authority explicit | `authority_state` is mandatory and constrained to `DRAFT/APPROVED/RETIRED` | PASS |
| Criticality explicit | Every target cell has an operational `criticality` | PASS |
| Freshness targets explicit | Collection and content freshness thresholds are distinct | PASS |
| Unobserved cells allowed | Target policy may define cells absent from observed matrix | PASS |
| `UNSET` fail-closed | Default may remain `UNSET`; it cannot mean `NOT_REQUIRED` | PASS |
| Independence fail-closed | Independent-origin requirement cannot be satisfied by source/domain/language count | PASS |
| Truth boundary preserved | Coverage/criticality/health cannot promote P13 factual verification | PASS |
| Draft cannot drive canonical gap/adequacy | Only `APPROVED` policy may drive P21.3 canonical adequacy decisions | PASS |
| Live/runtime boundary | No live source, ingest, runtime, deployment, provider or migration mutation | PASS |
| Target policy approved | Explicit owner-approved target manifest exists | PENDING |

## Gate rule

Contract implementation validation and policy authorization are separate evidence items.

The P21.0 gate remains **not granted** while the target manifest is `authority_state = DRAFT`.

The current draft proposal is:
`docs/evidence/P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json`

It is intentionally reviewable and non-operative. Its cells must not be treated as canonical gaps until separately approved.
