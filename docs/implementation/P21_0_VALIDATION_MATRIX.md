# P21.0 — Coverage Policy & Criticality Validation Matrix

Date: 2026-09-16
Status: `VALIDATED / GLOBAL_POLICY_APPROVED / P21_1_READY`
Gate: `P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

| Requirement | Validation rule | Current result |
|---|---|---|
| Reuse P20.2 semantics | Existing requirement states, cell dimensions and source/origin/health thresholds remain present | PASS |
| Preserve P20 history | P20.0/P20.1/P20.2 evidence is read-only and unchanged | PASS |
| Policy authority explicit | Policy authority is explicit and reviewable | PASS |
| Immutable approval | Owner approval binds to the exact reviewed manifest Git blob | PASS |
| Criticality explicit | Every target cell has an operational `criticality` | PASS |
| Freshness targets explicit | Collection and content freshness thresholds are distinct | PASS |
| Unobserved cells allowed | Target policy may define cells absent from observed matrix | PASS |
| Global macroregional baseline | Policy explicitly represents Europe, Middle East, East/Southeast/South/Central Asia, Caucasus, North/Sub-Saharan Africa, North/Latin America, Brazil, Oceania and GLOBAL cross-cutting classes | PASS |
| Priority country cells preserved | Ukraine, Russia and United States direct official/media requirements remain explicit rather than hidden inside broad regions | PASS |
| Language diversity explicit | Policy includes local/regional language targets and does not treat English or `multi` as universal substitutes | PASS |
| Cross-cutting source classes | Wire, sanctions/regulatory, economic/energy, research and public OSINT roles are represented separately | PASS |
| Global does not mean exhaustive | `default_requirement_state = UNSET`; unspecified cells remain unknown rather than implicitly adequate or not required | PASS |
| `UNSET` fail-closed | Default remains `UNSET`; it cannot mean `NOT_REQUIRED` | PASS |
| Independence fail-closed | Independent-origin requirement cannot be satisfied by source/domain/language count | PASS |
| Truth boundary preserved | Coverage/criticality/health cannot promote P13 factual verification | PASS |
| Approved policy may drive later adequacy | Only the exact manifest bound by the approved envelope may drive P21.3 canonical adequacy decisions | PASS |
| Plugin wrapper non-promotional | Plugin/App/Connector/MCP integration cannot create source independence, provenance, health or factual-verification credit | PASS |
| Live/runtime boundary | No live source, ingest, runtime, deployment, provider or migration mutation | PASS |
| Target policy approved | Explicit owner-approved target manifest exists | PASS |

## Canonical approved global baseline

Manifest:
`docs/evidence/P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json`

Reviewed manifest version:
`0.2-draft-global-baseline`

Reviewed manifest Git blob:
`d1d7ea7f36443b2b350a290114f3c8a6417a447e`

Approval envelope:
`docs/evidence/P21_0_TARGET_COVERAGE_POLICY_APPROVAL_2026-09-16.json`

Authority:
`APPROVED`

The approved baseline contains 33 target cells spanning 20 geography scopes and 15 language labels. It is a global operational baseline, not a claim of exhaustive country-by-country or language-by-language coverage.

The original proposal artifact remains immutable pre-approval evidence. Authority is attached to that exact reviewed blob by the separate approval envelope; any changed manifest requires new approval.

## OpenAI / Plugin architecture correction

The platform transition does not alter P21.0 evidence semantics. KGM is now explicitly Plugin-first for any future ChatGPT-facing surface, while legacy GPT Actions are transition-only. Plugin capability/sharing must be revalidated on the actual launch account/workspace and remains non-activated.

Decision:
`docs/decisions/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md`

## Gate result

```text
P21_0_CONTRACT_IMPLEMENTED = YES
P21_0_GLOBAL_BASELINE = APPROVED
P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED = PASS
LIVE_SOURCE_EXPANSION = NO
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
NEXT_GATE = P21_1_SOURCE_PROVENANCE_RESOLUTION_VALIDATED
```
