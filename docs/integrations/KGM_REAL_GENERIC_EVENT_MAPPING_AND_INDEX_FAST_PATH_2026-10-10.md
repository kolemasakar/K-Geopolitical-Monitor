# KGM Real Generic Event Mapping and Archive Index Fast Path — 2026-10-10

## Decision

**REAL_GENERIC_EVENT_MAPPING_AND_INDEX_FAST_PATH = PASS_WITH_LIVE_ADAPTER_MAPPING_LIMITATION**

Exact validated implementation SHA:
`8fef756bcaeff9514718e579f0dfa1fc23328f70`

Selected research/exchange regression:
**278/278 PASS in 5.10 s**

This checkpoint advances only the bounded private owner-pilot independent-research track. It does not authorize production/live daemon operation, persistent unattended scheduling, Sentinel transport, K-Trader integration, paid providers/fallbacks, shared runtime, public Plugin publication or HP-OMEN use.

## 1. Auditable real-source generic mapping

Added:
`kgm.research.generic-mapping.v1`

The mapper accepts only explicit structured source facts. It performs no:
- NLP extraction;
- synonym inference;
- fuzzy matching;
- source-independence scoring;
- factual verification.

It maps explicit source facts into the existing generic event/claim identity primitives and reports only:
- event identity agreement;
- claim signature agreement;
- distinct-origin candidacy.

## 2. Real official-source acceptance pair

A real diplomatic event was used as an acceptance pair:

Event:
- date: 24 September 2026;
- actors: NATO Secretary General Mark Rutte and President of Ukraine Volodymyr Zelenskyy;
- location: New York, United States;
- action: MEET;
- bounded common claim: the bilateral meeting occurred.

Official source paths:
1. NATO official news path.
2. Official website of the President of Ukraine.

The two source facts map to:

- event identity:
  `geo-diplomatic-20260924-2afad3e80899d4325c7776b7c596737d`
- claim signature:
  `claim-status-c25aaea1abcf75af8864c6bc15f5896a`
- event match: true
- claim match: true
- distinct origin groups:
  - `nato`
  - `president-ukraine`
- independent-origin candidate: true

The mapping layer does **not** convert this candidate into VERIFIED status.

### Retrieval limitation

The official President of Ukraine page was publicly retrievable through the external public-web research path, but direct HTTP retrieval from the isolated owner VM returned HTTP 403.

Therefore this checkpoint proves:
- real official-source semantic mapping at source-fact level;
- deterministic identity agreement across two independent official origins;

but does **not** yet prove a live owner-VM adapter path for the President of Ukraine source.

NATO remains directly retrievable through the owner VM.

## 3. Fail-closed mapping behavior

Deterministic acceptance tests prove:
- a different event day yields a different event identity and no event match;
- source facts cannot silently mutate identity;
- real-source origin candidacy does not create verification fields;
- duplicate source identities in one explicit mapping batch are denied.

## 4. Archive index canonical fast path

Added:
`select_historical_snapshot_fast(...)`

Behavior:
1. use the verified rebuildable archive index when present and valid;
2. verify index/archive filename-manifest equality;
3. load and re-validate the selected authoritative archive artifact;
4. if the index is missing, stale, corrupt, or otherwise unusable, fall back to the authoritative archive scan;
5. fallback scan is bounded to 10,000 archive entries by default;
6. above that fallback bound, the system fails closed until the index is rebuilt.

The immutable archive remains authoritative. The index remains a cache.

The policy-bound historical worker now uses this fast-path selector.

## 5. On-disk benchmark

A real on-disk benchmark used hard-linked copies of a previously validated immutable archive artifact. This measures filesystem enumeration plus JSON archive/index processing without fabricating an alternate schema.

### 1,000 archive entries

- index rebuild: 1.9132 s
- authoritative scan: 2.0836 s
- indexed selection: 0.0211 s
- speedup: 98.89x
- indexed and authoritative selection SHA: identical

### 10,000 archive entries

- authoritative scan: 21.3310 s
- indexed selection: 0.1952 s
- speedup: 109.25x
- indexed and authoritative selection SHA: identical

The earlier metadata-only validation benchmark remains:
- 1,000 entries: 0.0049 s
- 10,000 entries: 0.0523 s
- 100,000 entries: 0.5367 s

No claim is made here about a 100,000-file full on-disk rebuild/scan benchmark.

## 6. Validation

Targeted real-mapping / archive-index / worker suite:
**22/22 PASS**

Full selected research/exchange regression:
**278/278 PASS in 5.10 s**

## Readiness interpretation

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS` remains valid.

The previous primary P1 limitation, generic real-source semantic mapping, is closed at the explicit source-fact level.

Remaining quality limitation:
- live owner-VM adapterization / structured extraction for additional independent political/diplomatic/military/economic official sources must be proven before generic cross-source mapping can be treated as fully unattended.

## Next technical track

`LIVE_GENERIC_MAPPING_ADAPTERIZATION_AND_ARCHIVE_INDEX_MAINTENANCE`
