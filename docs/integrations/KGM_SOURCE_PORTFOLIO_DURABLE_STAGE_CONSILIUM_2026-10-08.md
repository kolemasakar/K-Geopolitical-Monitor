# KGM source portfolio completeness, durable observation staging and canonical Consilium — 2026-10-08

## Decision

**KGM_SOURCE_PORTFOLIO_DURABLE_STAGE_AND_OFFICIAL_POLITICAL_SOURCE = PASS**

Exact validated code SHA: `415e7893dfd9f0fb4cf8669ebb65344d48a95987`.

This checkpoint advances only the bounded owner-pilot independent-research track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, does not advance the canonical Phase 23 strategic gate, and does not authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## Required source portfolio binding

Added `kgm.source.policy.v1`.

The policy binds:
- consumer id;
- policy version;
- required source ids;
- optional source ids;
- maximum total observations.

Before the durable lifecycle enters PROCESSING:
- every required adapter must be supplied;
- unknown adapters are denied;
- duplicate/overlapping policy source ids are denied;
- each injected adapter is bound to the source id it is allowed to emit.

Therefore an accidentally omitted required source can no longer produce a false COMPLETE result.

## Durable observation stage

Added immutable:

`kgm.research.observation-stage.v1`

The stage binds:
- request digest;
- source-policy digest;
- stage timestamp;
- per-source execution ledger;
- normalized observations;
- artifact SHA-256.

Per-source run states:
- `OBSERVED`
- `EMPTY`
- `DEGRADED`

A required source that executes successfully but has no matching observations is explicitly recorded as `EMPTY`; it is not confused with an omitted source.

The stage is immutable and idempotent under exact replay.

## Crash/restart behavior

The new policy-bound worker:
1. validates the complete required source portfolio;
2. enters PROCESSING;
3. reuses an existing valid immutable stage if present;
4. otherwise queries each bound adapter once;
5. normalizes and atomically stages the exact source snapshot;
6. constructs the typed result only from the staged snapshot.

Live owner-pilot failure injection proved:

- GDACS network calls before crash: 1;
- USGS network calls before crash: 1;
- GFZ network calls before crash: 1;
- GDELT network calls: 0 because active cooldown was honored;
- staged observations: 30;
- crash injected after durable stage;
- retry adapter re-queries: **0**;
- retry completed from the exact staged snapshot;
- result: `PARTIAL / PARTIAL / DEGRADED`;
- recovery pending after completion: empty.

Stage SHA-256:
`96e12c501dc61af77e7389315f8f3db4af474df8093a103daee08034578023fe`

Result id:
`result-55f81b42450ed794295b0c12`

## Canonical official political source migration

Migrated Council of the EU / European Council press-release RSS into the canonical source-observation contract:

- source id: `consilium-press-releases`;
- origin group: `consilium-eu-council`;
- public/free/read-only;
- HTTPS only;
- response-size bound;
- XML parsing fails closed;
- query filtering bounded;
- historical live retrieval cannot backdate availability.

The current Consilium RSS feed omits `pubDate`.

KGM therefore does **not** fabricate or backdate a publication time. The date embedded in the official URL is used only to determine whether an item belongs to the requested CURRENT date window; the first KGM observation time is used as the conservative publication/availability boundary.

Live canonical probe:
- 10 official Consilium observations returned;
- all had official Consilium HTTPS provenance;
- all used `origin_group = consilium-eu-council`.

## Mixed-domain policy-bound live execution

A single live policy-bound source portfolio required:

- Consilium press releases;
- GDACS;
- GDELT;
- GFZ GEOFON;
- USGS.

Observed source runs:

- Consilium: 10 / OBSERVED;
- GDACS: 10 / OBSERVED;
- GDELT: 1 / DEGRADED under active RATE_LIMITED cooldown;
- GFZ: 10 / OBSERVED;
- USGS: 10 / OBSERVED.

Total staged observations: **41**.

Healthy evidence from all four available domains/source paths was represented in the bounded result:

- `consilium-press-releases`
- `gdacs-events`
- `gfz-geofon`
- `usgs-earthquake`

GDELT network calls during cooldown: **0**.

Result remained correctly:

`PARTIAL / PARTIAL / DEGRADED`

because one required source was degraded.

Mixed-domain result id:
`result-34a0ebda1b19908f1f132874`

## Validation

Targeted new worker/source tests:
- **14/14 PASS**

Selected exchange/research regression:
- **245/245 PASS in 4.17 s**

## Readiness impact

Readiness-audit-v2 blockers closed by this checkpoint:

- P0-1 expected source portfolio not bound → **CLOSED**;
- P0-2 live observations not durably staged → **CLOSED**;
- P0-3 canonical official political source breadth too narrow → **PARTIALLY CLOSED / MINIMUM OFFICIAL POLITICAL SOURCE PROVEN**.

Remaining primary P0 blocker:

- real `HISTORICAL_AS_OF` replay from first-seen durable evidence is not yet operational.

Next technical track:
`DURABLE_FIRST_SEEN_EVIDENCE_ARCHIVE_AND_HISTORICAL_REPLAY`
