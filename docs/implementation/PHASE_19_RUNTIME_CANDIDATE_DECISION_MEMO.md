# Phase 19 — Runtime Candidate Decision Memo

Date: 2026-09-11
Status: `PREPARED / DECISION_NOT_YET_APPLIED / NO_RUNTIME_MUTATION`
Base: `5714a76aaf12c77993ed5a02165c02a48d953758`

## Decision to be made

Phase 19 Attempt 2 is accumulating valid temporal evidence for the software actually deployed on `kgm-e4-owner-pilot`, while canonical repository `main` is materially newer.

Observed state:

```text
DEPLOYED_RUNTIME_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
CURRENT_CANONICAL_MAIN_AT_MEMO_BASE = 5714a76aaf12c77993ed5a02165c02a48d953758
CURRENT_MAIN_COMMITS_AHEAD_OF_DEPLOYED = 522
RUNTIME_CODE_DRIFT = MATERIAL
P19_RUNTIME_CANDIDATE_IDENTITY = UNRESOLVED
P19_ATTEMPT_2_BASELINE = 2026-09-11T07:38:44Z
```

This memo does not declare either SHA to be the final P19 candidate. It prepares the decision without deploying, restarting, or changing the live soak.

## Candidate paths

### Path A — freeze `b31b2136...` as the explicit P19 runtime candidate

Meaning:

- the current real-soak remains candidate-relevant;
- 24h/72h/7d elapsed evidence may be retained;
- P19 closure wording must state that the validated runtime candidate is exactly `b31b2136...`;
- newer `main` application code must not be described as covered by this soak.

Mandatory preconditions before Path A may be accepted:

```text
A1_EXACT_B31B_REPRODUCIBILITY = PASS
A2_EXACT_B31B_APPLICABLE_REGRESSION = PASS
A3_DEPLOYED_SHA_REVERIFIED = PASS
A4_NO_RUNTIME_MUTATION_DURING_ATTEMPT_2 = PASS
A5_24H_72H_7D_TEMPORAL_GATES = PASS
A6_CLOSURE_WORDING_CANDIDATE_SCOPED = PASS
```

Advantages:

- preserves current elapsed soak;
- lowest additional temporal cost;
- accurately validates the build currently operating on the owner-local VM.

Risks/limitations:

- canonical `main` remains a different software candidate;
- future deployment of newer application code needs its own release/convergence validation and must not inherit P19 temporal evidence implicitly;
- exact `b31b...` regression/reproducibility evidence may require reconstruction.

### Path B — converge owner-local runtime to a selected canonical release candidate

Meaning:

- select an exact canonical SHA;
- deploy it through a separately authorized bounded procedure;
- verify exact deployed SHA;
- establish a new real-soak baseline after deployment;
- no pre-deployment elapsed time validates the new candidate.

Advantages:

- repository candidate and deployed runtime converge;
- simpler final claim semantics;
- closes the drift directly.

Costs:

- current Attempt 2 cannot validate the newly deployed candidate;
- a fresh candidate-specific elapsed soak is required;
- earliest full 7-day temporal validation moves by approximately another seven days after the new baseline.

### Path C — retain Attempt 2 as operational evidence but keep full P19 open until later convergence

Meaning:

- complete the current 7-day soak for `b31b...`;
- record it as valid deployed-build operational evidence;
- do not close `P19_BETA_OPERATIONAL_STABILITY_VALIDATED`;
- later perform Path B and a fresh candidate-specific soak.

Advantages:

- preserves useful current evidence;
- strongest assurance if the project insists final P19 refer to canonical application code.

Costs:

- longest calendar path;
- duplicates temporal soak effort;
- leaves P20 operational entry blocked longer if P20 is strictly coupled to final P19 closure.

## Decision matrix

| Criterion | Path A | Path B | Path C |
|---|---:|---:|---:|
| Preserve current Attempt 2 elapsed time | **Yes** | No | Yes, evidence only |
| Final candidate matches current `main` | No | **Yes** | Eventually |
| Additional 7-day soak likely | No, if A1-A6 pass | **Yes** | **Yes** |
| Closure semantic complexity | Medium | Low after new soak | High |
| Calendar efficiency | **Best** | Lower | Lowest |
| Assurance for current deployed VM | **High** | Superseded after deploy | High |
| Assurance for newer canonical code | Separate later gate required | **High after new soak** | High after later convergence soak |

## Recommended default

For calendar efficiency **without overstating evidence**, the recommended default is:

> **Path A, conditionally**, only if exact `b31b2136...` reproducibility/regression evidence can be demonstrated and the project explicitly accepts that P19 validates that frozen deployed candidate rather than current repository `main`.

This preserves the current 7-day soak while keeping claims truthful.

After P19 closes on that candidate, any later deployment of newer canonical application code must pass a distinct release/convergence validation gate before being treated as operationally equivalent. That later gate must not silently reuse `b31b...` soak evidence.

If exact-`b31b...` reproducibility/regression cannot be established, the recommendation automatically falls back to **Path B**.

## Required read-only work before decision application

The following may be done during the active soak:

- re-verify exact deployed SHA through bounded `health` observation;
- inventory Git commit/tree availability for `b31b...`;
- identify CI/test suite state applicable to that commit;
- determine whether current deterministic/recovery evidence is candidate-independent or candidate-specific;
- prepare closure wording for Path A and deployment/reanchor runbook for Path B.

The following must not be done merely to resolve the memo during active Attempt 2:

```text
DEPLOY_APPLICATION_CODE = NO
RESTART_SERVICE = NO
CHANGE_BASELINE = NO
CHANGE_CADENCE = NO
CHANGE_P19_GATE_LOGIC = NO
CHANGE_TAILSCALE_TRUST = NO
```

## Proposed explicit decision record

When the owner approves the path, record exactly one of:

```text
P19_RUNTIME_CANDIDATE_DECISION = PATH_A_FREEZE_DEPLOYED_B31B
P19_RUNTIME_CANDIDATE_DECISION = PATH_B_CONVERGE_TO_EXACT_CANONICAL_SHA
P19_RUNTIME_CANDIDATE_DECISION = PATH_C_EVIDENCE_ONLY_THEN_CONVERGE
```

For Path A additionally record:

```text
P19_INTENDED_RUNTIME_CANDIDATE_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
P19_DEPLOYED_RUNTIME_SHA_MATCHES_INTENDED_CANDIDATE = PASS
```

For Path B, the selected candidate SHA must be written only after deployment authorization and exact deployment selection; this memo does not pre-authorize `5714a76...` or any later `main` SHA as a deployment target.

## Current result

```text
DECISION_MEMO = PREPARED
RECOMMENDED_PATH = PATH_A_CONDITIONAL
RUNTIME_CANDIDATE_DECISION = NOT_APPLIED
P19_ATTEMPT_2 = UNCHANGED
P19_BASELINE = UNCHANGED
RUNTIME_MUTATION = NO
```
