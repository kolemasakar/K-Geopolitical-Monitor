# KGM P1 Research Quality Hardening — 2026-10-10

## Decision

**P1_RESEARCH_QUALITY_HARDENING = PASS_WITH_REMAINING_REAL_CROSS_SOURCE_IDENTITY_MAPPING**

Exact validated code SHA:
`9309bb98f886b72b396b7c032caacb3c0dcc5c71`

Selected research/exchange regression:
**272/272 PASS in 4.81 s**

This checkpoint advances only the bounded private owner-pilot independent-research track. It does not activate production/live daemon operation, persistent unattended scheduling, Sentinel transport, K-Trader integration, paid providers/fallbacks, shared runtime, public Plugin publication or HP-OMEN use.

## 1. Generic geopolitical event / claim identity families

Added conservative structured identity support for:
- POLITICAL
- DIPLOMATIC
- MILITARY
- ECONOMIC

Generic identities are generated only from explicit controlled descriptors:
- event family;
- UTC event day;
- action key;
- actor keys;
- target keys;
- subject key;
- optional location key.

Generic claim signatures are generated separately from:
- claim type;
- normalized value keys;
- optional unit key.

No NLP, synonym inference or fuzzy semantic matching is performed inside the identity primitive.

The source-observation contract binds any supplied:
- `event_descriptor` to the exact derived `event_identity`;
- `claim_descriptor` to the exact derived `claim_signature`.

Mismatched identities fail closed.

Deterministic end-to-end tests prove that two sources with different wording can merge into one event record only when both carry the same explicit structured event descriptor and claim descriptor.

### Remaining limitation

Automatic real-world cross-source semantic descriptor extraction for political/diplomatic reporting is not yet proven. The framework is ready, but real source-specific mapping rules remain a separate audited layer.

## 2. Typed PARTIAL semantics

The source observation contract now supports typed partial reasons.

Allowed reasons:
- `SOURCE_TRUNCATED`
- `UPSTREAM_PARTIAL`
- `RATE_LIMITED_PARTIAL`
- `FILTER_LIMIT`
- `PARSE_PARTIAL`
- `COVERAGE_GAP`
- `OTHER`

Rules:
- a PARTIAL evidence-bearing observation must carry one typed reason;
- a non-PARTIAL observation may not carry a partial reason;
- transport/source failures remain separate UNAVAILABLE/INVALID states.

## 3. Canonical evidence fingerprint duplicate detection

Evidence-bearing observations now receive a canonical publication-path fingerprint derived from normalized HTTPS provenance.

The source contract now also rejects:
- credential-bearing HTTPS URLs;
- fragmented URLs;
- missing-host HTTPS provenance;
- overly long provenance URLs.

Within one normalized observation batch, the same publication URL presented under different source/native observation IDs is rejected as duplicate evidence.

This is intentionally publication-path deduplication. It does not infer underlying-origin independence.

## 4. Official geopolitical source breadth expansion

### Existing official political/diplomatic source
- Council of the EU / European Council Consilium press releases.

### New official economic source
Added canonical ECB RSS adapter:
- source id: `ecb-press`;
- origin group: `ecb`;
- official public/free/read-only RSS;
- exact publication timestamps where supplied;
- live historical backdating denied.

Real ECB owner-pilot probe:
- 10 observations returned;
- official ECB HTTPS provenance;
- origin group `ecb`.

### New official military/security source
Added canonical NATO public news-search adapter:
- source id: `nato-news`;
- origin group: `nato`;
- official public/free/read-only NATO JSON listing endpoint;
- allowlisted security themes;
- bounded date window and result count;
- no credentials or paid fallback;
- publication day is used only for window membership;
- KGM first-seen time remains the conservative publication/availability boundary where NATO does not expose a trustworthy exact publication time.

Real NATO owner-pilot probe returned official deterrence/defence items including:
- Steadfast Noon 2026;
- REPMUS 2026.

## 5. Real broadened mixed-domain source portfolio

A live policy-bound owner-pilot cycle required seven source paths:

- Consilium press releases;
- ECB press;
- NATO news;
- GDACS;
- GDELT;
- GFZ GEOFON;
- USGS.

Observed source runs:
- Consilium: 10 / OBSERVED
- ECB: 10 / OBSERVED
- GDACS: 10 / OBSERVED
- GDELT: 1 / DEGRADED under durable RATE_LIMITED cooldown
- GFZ: 10 / OBSERVED
- NATO: 5 / OBSERVED
- USGS: 10 / OBSERVED

Total staged observations: **56**.

Result:
- `PARTIAL / PARTIAL / DEGRADED`
- result records: 10
- corroboration groups: 9
- GDELT network calls during cooldown: 0
- recovery pending: empty
- stage SHA:
  `72aede55bcc6222fa7b64417069070bb323f1cbec1b4b1c88020c12304b33791`
- result id:
  `result-7ba83ab17e713911b73f117c`

All six healthy official/public source paths were represented in the bounded result.

## 6. Historical archive indexing and retention planning

Added rebuildable:
`kgm.research.evidence-archive-index.v1`

The immutable archive remains authoritative.

The index is explicitly a cache and records:
- archive filename;
- stage SHA;
- staged timestamp;
- archived request window;
- policy version;
- source-policy digest;
- maximum evidence availability timestamp.

Safety properties:
- index SHA integrity validation;
- deterministic canonical sorting;
- symlink denial;
- index/archive filename manifest mismatch is treated as stale and denied by indexed selection;
- indexed selection still loads and verifies the chosen authoritative archive entry;
- corrupted index fails closed.

Added non-destructive retention planning:
- bounded `keep_latest`;
- keep/delete-candidate lists;
- no deletion is performed by the planner.

Deterministic tests prove:
- indexed and authoritative scan selection return the same snapshot;
- a new archive entry makes an older index stale;
- index corruption is denied;
- retention planning performs no destructive action.

### Metadata validation benchmark

Synthetic index validation on the isolated owner VM:

- 1,000 entries: 0.0049 s
- 10,000 entries: 0.0523 s
- 100,000 entries: 0.5367 s

This benchmark measures index metadata validation only, not full filesystem rebuild cost.

## Current readiness interpretation

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS` remains valid.

P1 items closed by this checkpoint:
- typed PARTIAL reason semantics;
- canonical evidence publication-path deduplication;
- official economic source breadth;
- official military/security source breadth;
- rebuildable historical archive index and non-destructive retention planner;
- generic typed identity primitive and end-to-end correlation contract.

Remaining primary P1 limitation:
- audited real-source mapping from political/diplomatic/military/economic source content into shared generic event/claim descriptors across independent sources.

Secondary archive hardening still recommended:
- make the rebuildable index an optional canonical fast path with authoritative-scan fallback;
- benchmark full rebuild/lookup on large on-disk archives before enabling automatic maintenance.

## Next technical track

`REAL_GENERIC_EVENT_MAPPING_AND_INDEX_FAST_PATH`
