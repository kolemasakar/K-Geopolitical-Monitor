# KGM independent-origin corroboration integration — 2026-10-08

## Decision

**KGM_INDEPENDENT_ORIGIN_CORROBORATION_INTEGRATION = PASS_WITH_NO_AUTO_VERIFICATION**

Latest validated head: `8fb9f6fa7197b59d01fb65a8a5f7b50a3c048804`.
Live v2 owner-pilot execution used behaviorally identical code at `29f47567338b04cb8bfebfb9aeb96131fabc3387`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, change the canonical Phase 23 strategic gate, or authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Typed result v2

The canonical owner-pilot worker now emits `kgm.research.result.v2` with a bounded top-level `corroboration` section.

Each corroboration group represents one conservatively associated physical event rather than a pair of source paths. This prevents duplicated independence credit when multiple publication paths share the same underlying origin.

Each group records:
- member source/observation identities;
- unique source paths;
- maximum association time delta;
- maximum epicentral distance;
- structured claim relation: AGREES / DIFFERS / UNKNOWN;
- underlying-origin assessment: UNKNOWN / SAME_ORIGIN / DISTINCT_ORIGIN;
- explicit origin groups;
- one event-level independent-origin credit flag;
- ambiguity flag;
- `factual_verification_credit = false`.

## Double-counting protection

A real event may appear through:
- USGS/NEIC;
- GDACS carrying the same NEIC origin;
- GFZ GEOFON carrying a separate GFZ origin.

Pair-level counting would incorrectly count both USGS↔GFZ and GDACS↔GFZ as two independent corroborations.

The integrated model now creates one physical-event corroboration group and grants at most one event-level independence credit.

Deterministic tests confirm:
- SAME-origin duplicate publication paths do not double-count;
- an ambiguous one-to-many same-source association denies independence credit;
- typed v2 validation rejects automatic factual-verification credit;
- typed v2 validation rejects retained independence credit on ambiguous groups.

## Live owner-pilot result

Live read-only cycle:
`CURRENT → GDACS + USGS + GFZ + GDELT cooldown → normalized observations → event-level corroboration → typed result v2`

Observed:
- schema: `kgm.research.result.v2`
- research status: `PARTIAL`
- coverage: `PARTIAL`
- source health: `DEGRADED`
- result records: **20**
- represented healthy sources: GDACS, GFZ GEOFON, USGS
- corroboration groups: **13**
- DISTINCT_ORIGIN groups: **10**
- event-level independent-origin credits: **10**
- SAME_ORIGIN groups: **3**
- ambiguous groups: **0**
- structured claim-difference groups: **9**
- automatic factual-verification credits: **0**
- GDELT network calls during cooldown: **0**
- result id: `result-68f7dbfc09fa3f29f01a5970`
- recovery pending: empty

The nine claim-difference groups primarily reflect differing earthquake magnitude solutions across agencies. They are retained as structured disagreement metadata and are not silently converted into factual contradiction or verification status.

## Validation

Targeted v2/corroboration/worker/source suite:
- **31/31 PASS** on latest head.

Selected exchange/research regression:
- **200/200 PASS in 2.91 s**.

## Result

KGM now has a bounded owner-pilot path from real multi-source observations to explicit event-level origin corroboration metadata without:
- double-counting downstream source paths;
- confusing correlation with origin independence;
- confusing origin independence with factual verification;
- promoting ambiguous associations.

Next technical track:
`CORROBORATION_TO_VERIFICATION_POLICY_BOUNDARY`

The next step must define what additional evidence is required before any correlated event can move from UNVERIFIED toward VERIFIED. Independent-origin credit alone remains insufficient.
