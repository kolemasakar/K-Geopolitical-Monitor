# KGM event/claim identity owner-pilot acceptance — 2026-10-07

## Decision

**KGM_EVENT_CLAIM_IDENTITY_OWNER_PILOT = PASS_WITH_ORIGIN_LIMITATION**

Exact validated code SHA: `fe836769bd2742fe91f0c00d8e0410805477608f`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, does not change the canonical Phase 23 strategic gate, and does not authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Problem addressed

Native source IDs are not safe cross-source correlation keys. Two sources can use different IDs for the same physical event, while coincidentally equal native IDs can refer to unrelated events. Likewise, source titles can describe the same event with different wording and must not be treated as contradictions merely because the strings differ.

## Implemented model

### Structured event identity

For earthquake observations, KGM derives a conservative event identity from structured source fields:

- UTC origin timestamp to the second;
- latitude rounded to 0.01 degree;
- longitude rounded to 0.01 degree.

Magnitude is deliberately **not** part of event identity so that later magnitude revisions do not create a different physical event identity.

Example:

`eq-20261007T181504-n5448-e16256`

### Structured claim signature

Magnitude is represented separately as a claim signature:

`mag-48`

This permits KGM to distinguish:

- **same event + same structured claim** → merge provenance into one UNVERIFIED event record;
- **same event + different structured claim** → separate DISPUTED records with mutual contradiction references;
- **different source-native IDs without event identity** → never cross-merge;
- **different source wording with the same event identity and claim signature** → not a contradiction.

Correlation does **not** grant factual verification or source-independence credit.

## Live correlation validation

A real public/free/read-only 24-hour earthquake probe was run against:

- GDACS earthquake events;
- USGS Earthquake FDSN API, minimum magnitude 4.5.

Observed:

- GDACS earthquake observations: **32**
- USGS observations: **16**
- shared structured event identities: **16**
- shared identities with equal magnitude claim signatures: **16**
- shared identities with differing magnitude claim signatures: **0**

The same physical events were represented with materially different source wording while retaining matching structured identity. Examples included events in Indonesia, Kermadec Islands/New Zealand, Japan, Russia, Vanuatu, South Sandwich Islands, Mexico and the Fiji region.

This proves that title-string equality is not a valid correlation/disagreement rule.

## Live typed owner-pilot cycle

A second real cycle ran:

`CURRENT request → live GDACS EQ + live USGS M>=4.5 + GDELT durable cooldown → normalization → event/claim correlation → typed artifact`

Observed:

- `research_status = PARTIAL`
- `coverage = PARTIAL`
- `source_health = DEGRADED`
- typed result records: **20**
- correlated records with both GDACS and USGS provenance: **16**
- DISPUTED records: **0**
- GDELT network calls during active cooldown: **0**
- result id: `result-861584d228496bf5478c3355`
- recovery pending: empty

PARTIAL is intentional because GDELT remained unavailable under active RATE_LIMITED cooldown. Correlated GDACS/USGS evidence therefore did not falsely promote the overall result to COMPLETE.

## Validation

Targeted identity/multi-source/source/worker suite:

- **31/31 PASS**

Selected exchange/research regression:

- **189/189 PASS in 2.81 s**

## Origin limitation

GDACS and USGS are distinct public source paths, but shared event identity is **not evidence of independent underlying origin**. KGM therefore grants:

- event-correlation credit: YES;
- merged provenance paths: YES;
- automatic factual verification credit: NO;
- automatic independent-origin corroboration credit: NO.

Independent-origin assessment remains a separate provenance problem governed by existing KGM verification policy.
