# Current K-Geopolitical Monitor Handoff

Status: `AUTHORITATIVE_POINTER / PHASE_21_IN_PROGRESS / P21_5_VALIDATED / P21_6_READY`

Canonical prior validated strategic baseline:
`PHASE_20_GLOBAL_SOURCE_COVERAGE_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`

Approved strategic block:
`Phase 21 — Source Network Operational Adequacy & Evidence Population`

Current Phase 21 position:
`PHASE_21_P21_5_VALIDATED_P21_6_READY`

Next gate:
`P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED`

Roadmap decision:
`docs/decisions/PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_ROADMAP_DECISION_2026-09-16.md`

Implementation plan:
`docs/implementation/PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_PLAN.md`

P21.0 result:
`docs/implementation/P21_0_COVERAGE_POLICY_CRITICALITY_RESULT.md`

P21.0 checkpoint:
`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-16_P21_0_COVERAGE_POLICY_VALIDATED_PLUGIN_REBASED.md`

## P21.0 approved global baseline

Canonical reviewed manifest:
`docs/evidence/P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json`

Reviewed version:
`0.2-draft-global-baseline`

Reviewed Git blob:
`d1d7ea7f36443b2b350a290114f3c8a6417a447e`

Owner approval envelope:
`docs/evidence/P21_0_TARGET_COVERAGE_POLICY_APPROVAL_2026-09-16.json`

Approved baseline dimensions:

- target cells: `33`;
- geography scopes: `20`;
- language labels: `15`;
- unspecified/default requirement state: `UNSET`;
- `GLOBAL` remains scope, not proof of exhaustive global coverage.

The pre-approval manifest remains immutable evidence; approval binds to its exact Git blob. Any changed manifest requires a new approval record.

## P21.1 provenance resolution

Gate: `P21_1_SOURCE_PROVENANCE_RESOLUTION_VALIDATED`.

- 10/10 governed sources reviewed; publisher identity explicit for 10/10.
- 3 direct institutional streams have confirmed source-level origin groups.
- 6 streams remain `MIXED_ORIGIN` and require item-level provenance.
- GDELT remains `DERIVED_MULTI_ORIGIN / NO_INDEPENDENCE_CREDIT`.
- exact portfolio-wide independent-origin count remains `UNKNOWN`.
- implementation anchor: `3ff9df391f31ff8c7d19e6c229e4647e8dc88597`.
- CI: `1260 passed`.

## P21.2 fresh operational health baseline

Gate: `P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED`.
Decision: `VALIDATED_WITH_MEASURED_DEGRADATION`.

Fresh owner-local snapshot at `2026-09-16T16:59:49.917696+00:00` from `kgm-e4-owner-pilot` (`aarch64`) measured all 10 governed source paths from an isolated canonical checkout. Result: `8 success / 2 failure`, `260 items`, `10/10 CURRENT` measurement freshness.

Measured degradation retained for P21.3:
- `gdelt-doc-2`: `UNAVAILABLE / TRANSPORT`, HTTP 429;
- `eu-parliament-press-releases`: `UNAVAILABLE / PARSER`;
- `eu-commission-press-corner`: collector healthy, content stale;
- `osce-latest-news`: collector healthy, content stale.

Six paths were `HEALTHY / FRESH`: Consilium, Haberturk, Meduza, RMF24, GOV.UK, Ukrainska Pravda. CI run `35126109733`: `1263 passed`; merge anchor `7affa9ee3ca875ddff472972ee63d11a03ed1054`.

The deployed runtime was not updated or restarted. Operational health/freshness remains truth-neutral and cannot create independent-origin or factual-verification credit.

## P21.3 operational coverage adequacy baseline

Gate: `P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_VALIDATED`.

- target cells: `33`; required: `27`; optional: `6`;
- overall: `1 ADEQUATE / 10 THIN / 21 MISSING_EXPECTED_COVERAGE / 1 DEGRADED_COLLECTION / 0 UNKNOWN`;
- required cells: `1 ADEQUATE / 5 THIN / 21 MISSING_EXPECTED_COVERAGE`;
- only adequate cell: `eu.en.international_organization`;
- degraded cell: `global.multi.public_osint` due fresh GDELT HTTP 429;
- P20 closure remains historical (`17 UNKNOWN / 0 ADEQUATE / 0 confirmed gaps`) and is not rewritten;
- CI #1682: `1271 passed in 99.74s`; merge anchor: `2e0666ed1f2a0b16d0ec3b4dda664664ce151f04`.

## P21.4 gap-driven source expansion plan

Gate: `P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED`.

- 32 non-adequate target cells assigned to 6 policy-derived waves;
- minimum deficits: `49 source paths / 49 healthy-source positions / 54 origin-evidence positions`;
- `global.multi.public_osint` remains repair-or-alternate-first because the current GDELT path is degraded;
- public/free-first qualification is required; independence is not inferred from path/domain/language counts;
- GitHub CI #1710: `1281 passed in 115.53s`; implementation merge anchor: `277b219726008c70671cf4d804c857c98f8ab0c4`.

P21.4 is planning-only and did not activate any source. At P21.4 closure the position was `P21_4_VALIDATED / P21_5_OWNER_DECISION_REQUIRED`; that historical gate was superseded by the explicit owner authorization recorded for P21.5 on 2026-09-16.


## P21.5 controlled public/free onboarding

Gate: `P21_5_CONTROLLED_SOURCE_ONBOARDING_VALIDATED`.

- Wave A sources: `ukraine-government-kmu-uk`, `suspilne-uk`;
- repository-active paths: `2`; P20.5 qualified: `2`; automatic independence credit: `0`;
- fresh probe: `2/2 SUCCESS`, `120 items`;
- `suspilne-uk`: fresh against 120-minute threshold;
- `ukraine-government-kmu-uk`: collector/parser healthy but content stale (~464 minutes against 240), limitation preserved;
- PR #123; merge anchor `e2b78f8511154e9b626a39d0525d9b118c842bd2`;
- CI #1752: `1292 passed in 141.35s / SUCCESS`;
- deployed runtime not mutated or restarted.

## OpenAI / ChatGPT architecture rebase

Canonical decision:
`docs/decisions/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md`

Current direction:

```text
PRIMARY_CHATGPT_SURFACE = PLUGIN
LEGACY_GPT_SURFACE = TRANSITIONAL_ONLY
PUBLIC_GPT_ACTION = LEGACY_INTEGRATION_CONCEPT
CUSTOM_ACTION_AS_LONG_TERM_ARCHITECTURE = NO
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
PHASE_17_PLUGIN_CAPABILITY_REVALIDATION_REQUIRED = YES
```

The historical Phase 17 account-capability constraint remains historical evidence for the old external-publication surface. It must not be projected unchanged onto Plugins. Plugin build/upload/sharing capability must be freshly validated on the actual launch account/workspace.

Future KGM ChatGPT-facing architecture is Plugin-first:

- workflow/policy -> Plugin skill(s);
- reference assets -> versioned Plugin resources;
- external capabilities -> supported App / Connector / custom MCP candidate;
- sharing/access/permissions -> explicit launch-time validation;
- selected ChatGPT model -> not a canonical KGM dependency.

This rebase does not activate a Plugin or change source/truth/runtime semantics.

## Preserved boundaries

- `P21_5_BOUNDED_PUBLIC_FREE_ONBOARDING = AUTHORIZED_WAVE_A`;
- `DEPLOYED_RUNTIME_SOURCE_EXPANSION = NO`;
- `DEPLOYED_LIVE_INGEST_CHANGE = NO`;
- `RUNTIME_DEPLOYMENT = NO`;
- `SERVICE_RESTART = NO`;
- `PAID_PROVIDERS = NONE_APPROVED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033` = `NOT_CREATED / NOT_PREAUTHORIZED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- P13.5/P13.6 remain authoritative for factual verification.

P21.5 controlled public/free onboarding was explicitly authorized by the owner on 2026-09-16. Authorization begins with Wave A and does not authorize deployed-runtime mutation, paid/shared resources, production/live cutover or Plugin/publication activation.

## Next substantive action

`BEGIN P21.6 INTELLIGENCE QUALITY IMPACT VALIDATION. Compare pre/post Wave-A exact cohorts where feasible without converting coverage/health/source-count changes into factual-verification authority.`
