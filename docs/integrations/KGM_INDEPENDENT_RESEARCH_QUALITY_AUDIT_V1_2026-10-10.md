# KGM Independent Research Quality Audit v1 — 2026-10-10

## Decision

**INDEPENDENT_RESEARCH_QUALITY_AUDIT_V1 = PASS_WITH_KNOWN_LIMITATIONS**

Exact validated implementation/test SHA:
`91afabe40c8875e68d343cf0d4c599db2bafa4ce`

Selected research/exchange regression:
**305/305 PASS in 6.08 s**

This audit applies only to the bounded private owner-pilot independent-research path. It does not authorize production/live daemon operation, unattended scheduling, Sentinel transport, K-Trader integration, paid providers/fallbacks, shared runtime, public Plugin publication or HP-OMEN use.

## Audit objectives

The audit explicitly tested resistance to:

- false merge;
- false split;
- silent claim-disagreement collapse;
- false COMPLETE from unavailable/missing required sources;
- false VERIFIED / automatic verification;
- duplicate evidence masquerading as independent evidence;
- false source-origin independence;
- historical replay non-reproducibility.

It also reviewed the accumulated live owner-pilot corpus across:
- political;
- diplomatic;
- military/security;
- economic;
- earthquake/disaster;
- archive-backed historical replay.

## 1. False-merge resistance — PASS

Two observations with:
- same event family;
- same day;
- same actors;
- same claim;

but **different structured subject keys** produce different event identities and remain separate records.

No fuzzy title similarity, wording similarity or same-day coincidence can merge them.

## 2. False-split resistance — PASS

Two sources with different natural-language wording but the same explicit structured:
- event descriptor;
- claim descriptor;

produce:
- one shared event identity;
- one shared claim signature;
- one merged record with two evidence paths.

The record remains `UNVERIFIED`.

## 3. Claim disagreement handling — PASS

Two sources referring to the same explicit event identity but carrying different non-null claim signatures:
- are not silently merged;
- produce separate `DISPUTED` records;
- contain contradiction references;
- set worker disagreement state.

## 4. Source-origin independence — PASS

Two publication paths with the same explicit `origin_group`:
- produce `SAME_ORIGIN`;
- receive no independent-origin credit.

Two explicit distinct origin groups:
- may receive `DISTINCT_ORIGIN` credit;
- still do not auto-verify a record.

## 5. False VERIFIED resistance — PASS

Across deterministic audit cases and accumulated live owner-pilot artifacts:
- generic merged records remain `UNVERIFIED`;
- independent-origin credit does not change record verification;
- corroboration eligibility never creates automatic verification;
- explicit verification remains a separate immutable decision-artifact path.

Accumulated live artifact review:
- artifacts reviewed: **7**
- total typed records: **44**
- VERIFIED records created automatically: **0**
- automatic factual-verification corroboration flags: **0**

One earthquake corroboration group was eligible for explicit verification in an earlier owner-pilot artifact, but still had no automatic verification credit.

## 6. Duplicate-evidence resistance — PASS

The same normalized HTTPS publication path presented under different:
- source IDs;
- native observation IDs;

is rejected by canonical evidence-fingerprint duplicate detection.

This prevents one publication URL from masquerading as multiple independent evidence items.

## 7. False-COMPLETE resistance — PASS WITH SEMANTIC LIMITATION

Missing required adapters are denied before PROCESSING.

A required source returning `UNAVAILABLE` forces:
- `PARTIAL`;
- `PARTIAL` coverage;
- `DEGRADED` source health.

### Known completeness semantic

The approved source-policy contract treats an invoked source that successfully returns zero matching observations as a healthy `EMPTY` run.

Therefore `COMPLETE` means:
- all required adapters were invoked under policy;
- none failed or degraded;
- available evidence had no detected disagreement;

and does **not** mean every required source contributed at least one evidence item.

This is deliberate existing behavior, but downstream consumers must not interpret `COMPLETE` as “all required sources corroborated the event.”

The first multi-domain military acceptance exposed the practical importance of this distinction: a too-narrow UTC query window legitimately produced a healthy-empty GOV.UK run until the exact publication timestamp was included.

## 8. Historical reproducibility — PASS

Two separate `HISTORICAL_AS_OF` requests replayed from the same immutable archived CURRENT snapshot produce semantically identical:
- source observations, excluding request rebinding;
- typed records.

No provider calls are required for replay.

The historical archive remains first-seen bounded and no-lookahead protected.

## 9. Live corpus quality review

Accumulated live owner-pilot artifacts reviewed:

1. POLITICAL two-origin mapping — COMPLETE / HEALTHY.
2. MILITARY two-origin mapping — COMPLETE / HEALTHY.
3. ECONOMIC two-origin mapping — COMPLETE / HEALTHY.
4. DIPLOMATIC NATO + Moldova MFA mapping — COMPLETE / HEALTHY.
5. Multi-source earthquake origin/corroboration cycle — PARTIAL / DEGRADED due bounded GDELT state.
6. CURRENT archive seed cycle — PARTIAL / DEGRADED.
7. HISTORICAL replay cycle — PARTIAL / DEGRADED, preserving archived source health.

Aggregate:
- artifacts: **7**
- COMPLETE artifacts: **4**
- PARTIAL artifacts: **3**
- typed records: **44**
- automatic VERIFIED records: **0**
- automatic corroboration verification credits: **0**

## 10. Material known limitation discovered by this audit

Generic political/diplomatic/military/economic mappings merge correctly at the record layer through explicit `event_identity` / `claim_signature`.

However, the current `research_corroboration_v1` report is still built from structured earthquake `event_parameters` association.

Therefore generic two-source mapped records currently have:
- merged multi-source evidence at the record layer;
- explicit origin groups on source observations;
- but **no generic event-level corroboration report entry**.

Consequences:
- the generic mapping path cannot yet pass through the same typed corroboration → verification-eligibility boundary used by earthquake associations;
- generic independent-origin evidence must remain `UNVERIFIED`;
- this is fail-closed, not a false verification, but it is a real quality/feature gap.

This is the primary next technical issue.

## Audit verdict

The quality audit found no demonstrated false merge, false split, false VERIFIED, duplicate-evidence inflation, source-origin inflation, or historical replay drift in the tested bounded owner-pilot path.

The gate is therefore:

`INDEPENDENT_RESEARCH_QUALITY_AUDIT_V1 = PASS_WITH_KNOWN_LIMITATIONS`

Current readiness remains:

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS`

The most important remaining limitation is architectural rather than safety-critical:
generic event mappings are not yet propagated into the canonical corroboration / explicit-verification eligibility report.

## Next technical track

`GENERIC_CORROBORATION_AND_COMPLETENESS_SEMANTICS_V2`

Priority:
1. build generic corroboration groups from explicit event identity + origin metadata without reintroducing fuzzy matching;
2. preserve one physical-event independence credit and same-origin de-duplication;
3. keep generic records UNVERIFIED until explicit verification decision;
4. expose source-run contribution semantics so COMPLETE cannot be misread as universal corroboration;
5. add adversarial and live multi-domain acceptance for the new v2 semantics.
