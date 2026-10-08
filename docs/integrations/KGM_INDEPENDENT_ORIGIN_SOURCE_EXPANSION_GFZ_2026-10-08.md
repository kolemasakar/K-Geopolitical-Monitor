# KGM independent-origin source expansion — GFZ GEOFON — 2026-10-08

## Decision

**KGM_INDEPENDENT_ORIGIN_SOURCE_EXPANSION_GFZ = PASS_WITH_BOUNDED_ASSOCIATION**

Exact validated code SHA: `bd59dcf533788b6bcdde498ff112830137144d46`.

This checkpoint advances only the bounded owner-pilot research-execution track. It does not declare `KGM_INDEPENDENT_RESEARCH_READY`, change the canonical Phase 23 strategic gate, or authorize production, persistent scheduling, Sentinel/K-Trader integration, paid providers, shared runtime, or Plugin publication.

## New source

Added a public/free/read-only GFZ GEOFON FDSN earthquake adapter:

- source id: `gfz-geofon`
- origin group: `gfz-geofon`
- bounded query window and result limit;
- structured event parameters: origin UTC, latitude, longitude, magnitude;
- explicit claim signature;
- historical live retrieval remains fail-closed;
- no credentials or paid fallback.

Because the GFZ text endpoint does not expose a publication-update timestamp, KGM uses the first observed availability timestamp as a conservative non-backdated publication boundary for CURRENT owner-pilot use. Historical backdating is not permitted.

## Conservative association

Added earthquake association based on explicit structured parameters.

Default owner-pilot limits:
- origin-time delta: <= 30 seconds;
- epicentral distance: <= 50 km.

The association result records the measured time and distance deltas. Missing parameters or events outside the limits fail closed as non-matches.

Association is separate from factual verification.

## Live 24-hour independent-origin comparison

USGS/NEIC versus GFZ GEOFON, minimum magnitude 4.5:

- USGS observations: **13**
- GFZ observations: **11**
- unique conservative matches: **10**
- ambiguous USGS matches: **0**
- matched pairs assessed as DISTINCT_ORIGIN: **10**
- matched pairs receiving origin-level independence credit: **10**
- SAME_ORIGIN matches: **0**

Observed matched examples included events in Japan, Kamchatka/Russia, Philippines, Chagos, Indonesia, Fiji region, Mexico and South Sandwich Islands.

For the matched cohort, measured time and epicentral differences remained within the bounded conservative association thresholds.

## Live full source-path cycle

A live read-only owner-pilot worker cycle used:

- GDACS earthquake source;
- USGS earthquake source;
- GFZ GEOFON earthquake source;
- GDELT under active durable RATE_LIMITED cooldown.

Observed typed result:

- `research_status = PARTIAL`
- `coverage = PARTIAL`
- `source_health = DEGRADED`
- records: **20**
- represented healthy sources: `gdacs-events`, `gfz-geofon`, `usgs-earthquake`
- GDELT network calls during cooldown: **0**
- result id: `result-c281836a0265f545ab0be3b1`
- recovery pending: empty

PARTIAL remains correct because GDELT was unavailable under cooldown.

## Validation

Targeted GFZ/origin/identity/multi-source/source/worker suite:
- **38/38 PASS**

Selected exchange/research regression:
- **196/196 PASS in 2.94 s**

## Interpretation

The previous GDACS/USGS correlated cohort had zero independent-origin credit because both paths resolved to `usgs-neic`.

GFZ GEOFON adds a genuinely distinct explicit origin group for the matched cohort. This is the first owner-pilot proof in this track that KGM can:

1. observe the same physical event from multiple source paths;
2. separate publication path from underlying origin;
3. conservatively associate two independently originated event solutions;
4. grant bounded origin-level independence credit without promoting the event to factual VERIFIED status.

Next technical track:
`INDEPENDENT_ORIGIN_CORROBORATION_INTEGRATION`
