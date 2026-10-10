# KGM corroboration-to-verification policy boundary — 2026-10-08

## Decision

**KGM_CORROBORATION_TO_VERIFICATION_POLICY_BOUNDARY = PASS_WITH_EXPLICIT_VERIFICATION_REQUIRED**

Exact validated code SHA: `8207ee2efeedc154286cb2a03256c94e7d8171a7`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, does not change the canonical Phase 23 strategic gate, and does not authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Policy boundary

KGM now distinguishes three states at the corroboration boundary:

### ELIGIBLE_FOR_EXPLICIT_VERIFICATION

Required:
- non-ambiguous association;
- DISTINCT_ORIGIN assessment;
- independent-origin credit = true;
- at least two source paths;
- at least two explicit underlying origin groups;
- structured claim relation = AGREES.

Even then:
- `automatic_verification = false`;
- `factual_verification_credit = false`.

Eligibility means the event may proceed to a separate explicit verification decision process. It does not mean VERIFIED.

### EVENT_CORROBORATED_CLAIM_UNRESOLVED

Used when:
- the physical event is independently corroborated;
- but structured claims differ across origins.

The event itself may be strongly corroborated while the disputed claim remains unresolved.

### INELIGIBLE

Triggered by one or more blockers:
- ambiguous association;
- no independent-origin credit;
- insufficient source paths;
- insufficient distinct origins;
- claim agreement unknown.

The policy is fail-closed.

## Live owner-pilot boundary validation

Live read-only cycle:
`CURRENT → GDACS + USGS + GFZ + GDELT cooldown → event-level corroboration → verification eligibility boundary → typed result v2`

Observed:
- research status: `PARTIAL`
- coverage: `PARTIAL`
- source health: `DEGRADED`
- result records: **20**
- corroboration groups: **12**
- DISTINCT_ORIGIN groups: **9**
- independent-origin credit events: **9**
- SAME_ORIGIN groups: **3**
- ambiguous groups: **0**
- claim agreement groups: **4**
- claim difference groups: **8**
- `ELIGIBLE_FOR_EXPLICIT_VERIFICATION`: **1**
- `EVENT_CORROBORATED_CLAIM_UNRESOLVED`: **8**
- `INELIGIBLE`: **3**
- automatic verification events: **0**
- factual verification credits: **0**
- GDELT network calls during cooldown: **0**
- result id: `result-f1d23762fe3c577e4e28aa29`
- recovery pending: empty

The live result demonstrates the intended strictness: nine events had independent-origin credit, but only one satisfied the stronger claim-agreement boundary for explicit verification eligibility. Eight remained event-corroborated with unresolved claim differences.

## Validation

Targeted verification-boundary/v2/corroboration/worker/source suite:
- **38/38 PASS**

Selected exchange/research regression:
- **207/207 PASS in 3.03 s**

## Consequence

Independent-origin corroboration is necessary but not sufficient for factual verification.

The next technical track is:
`EXPLICIT_VERIFICATION_DECISION_ARTIFACT`

That track must define a separately auditable decision object that can move an eligible claim from UNVERIFIED to VERIFIED only through an explicit policy action, with provenance and rationale preserved.
