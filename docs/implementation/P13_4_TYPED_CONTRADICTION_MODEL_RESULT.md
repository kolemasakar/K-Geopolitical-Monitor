# P13.4 Typed Contradiction Model and Resolution Lifecycle — Result

Date: 2026-09-02
Decision: `PASS`
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`
Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`

## Exact Validation Evidence

- x64 GitHub Actions run `33594740585`, job `100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594740549`, job `100135812546`: native `aarch64`, `447 passed, 1 warning / SUCCESS`;
- ARM64 host-bootstrap shell validation: PASS;
- ARM64 unattended one-tick smoke: PASS;
- ARM64 systemd unit contract: PASS.

The warning is the existing FastAPI/Starlette TestClient deprecation warning and is not a P13.4 regression.

## Validated Implementation

P13.4 adds migration `026_semantic_contradiction_model.sql`, module `src/kgeopolitical_monitor/semantic_contradictions.py`, deterministic tests and canonical migration coverage.

Validated persistence:
- append-only `semantic_contradiction_versions`;
- append-only `semantic_contradiction_evidence_links`.

Validated dimensions:
- occurrence/existence;
- attribution/responsibility;
- actor identity;
- quantity/value;
- time;
- location;
- status/outcome;
- scope/extent;
- explicitly modeled causal interpretation;
- other typed contradiction.

Validated lifecycle:
- `DETECTED`;
- `UNRESOLVED`;
- `EVOLVING`;
- `RESOLVED`.

Historical disagreement remains stored when later versions reconcile the contradiction. `RESOLVED` requires an explicit reconciliation code plus explanatory note and does not mean that the service has selected a canonical factual winner.

## Fail-Closed Boundaries

- contradiction identity cannot silently change claim-version pair or dimension;
- two identical semantic claim version IDs cannot form a contradiction;
- evidence links must point to the correct contradiction side;
- evidence links must use the current P13.3 evidence relation version at link time;
- a P13.3 `CONTRADICTS` relation does not automatically create or resolve a contradiction;
- source reputation, official status, publisher/domain/language count, source health, P13.3 independence metadata, graph/forecast/coverage context do not automatically resolve substantive truth;
- reconciliation vocabulary contains no `LEFT_TRUE` / `RIGHT_TRUE` shortcut.

## Compatibility

Legacy `src/kgeopolitical_monitor/contradictions.py` remains unchanged/readable. P13.4 is additive and does not destructively rewrite legacy claims/evidence/live-analysis state, P13.1 semantic claims, P13.2 provenance or P13.3 evidence/independence history.

## Explicit Non-Claims

P13.4 does not establish:
- canonical verification promotion;
- factual verification confidence;
- coverage confidence;
- a verification policy engine;
- live semantic-analysis cutover;
- production/live operation.

Those remain P13.5/P13.6 or later operational decisions.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## Conclusion

P13.4 implementation satisfies its deterministic x64/native-ARM64 validation requirements. Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.

Next sequential package after canonical closure: `P13.5_VERIFICATION_POLICY_CONFIDENCE`.