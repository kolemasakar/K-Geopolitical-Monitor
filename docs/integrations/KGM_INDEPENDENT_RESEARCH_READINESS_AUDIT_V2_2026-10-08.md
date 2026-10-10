# KGM independent research readiness audit v2 — 2026-10-08

Status: **NOT READY FOR GATE**

Exact validated code SHA before this audit: `2cdf937201990d32ca59efd83c145c39e1330e33`.

Selected isolated regression: **231/231 PASS in 3.93 s**.

This audit supersedes the 2026-10-07 readiness audit for the owner-pilot independent-research execution track. It does not change the canonical Phase 23 strategic position.

## Previous blocking gaps — current disposition

### 1. Synthetic/offline-only execution
**RESOLVED FOR OWNER-PILOT CURRENT MODE.**

Real public/free/read-only source execution is proven through the canonical research worker path:
- GDACS;
- USGS Earthquake FDSN;
- GFZ GEOFON;
- GDELT fail-closed rate-limit/cooldown behavior.

### 2. Fixture-only coverage assessment
**PARTIALLY RESOLVED.**

Real source coverage, cross-source correlation, origin assessment and verification policy have been demonstrated on live disaster/earthquake data.

However the canonical research path is still narrow relative to KGM's geopolitical mission. The repository also contains approved controlled-pilot Consilium RSS and an older GDELT live-source stack, but those paths are not yet unified with the new canonical `research_source_*` contract.

### 3. No canonical worker/provider adapter
**RESOLVED FOR BOUNDED ONE-SHOT OWNER-PILOT.**

A deterministic durable worker and multiple real adapters are proven.

Persistent unattended scheduling and production activation remain intentionally inactive and separately owner-gated.

### 4. Legacy helper coupling
**RESOLVED.**

Canonical lifecycle/storage/state modules were decoupled into neutral primitives and regression-validated.

### 5. Production/Sentinel/K-Trader activation
**STILL OUTSIDE THIS GATE BY OWNER POLICY.**

No Sentinel or K-Trader interaction is required to continue the independent KGM research-readiness audit.

## Newly proven since audit v1

- real external typed E2E cycle;
- multi-source mixed-health execution;
- durable GDELT cooldown;
- source-balanced bounded result selection;
- structured earthquake event identity;
- structured claim signatures;
- underlying-origin assessment;
- independent-origin GFZ corroboration;
- event-level corroboration de-duplication;
- typed result v2;
- fail-closed verification eligibility boundary;
- explicit immutable verification decision artifacts;
- immutable revision/revocation lineage;
- evidence-bound revision v2;
- deterministic effective verification-state resolution;
- stale-state signal for unapplied post-head evidence.

## Current blocking readiness gaps

### P0-1. Expected source portfolio is not bound to the request/worker

The worker decides COMPLETE from the adapters actually supplied at execution time.

It does not yet prove that the caller supplied every source required by the approved source portfolio for that request.

Therefore an accidentally omitted intended source could still allow a false COMPLETE relative to policy intent.

**Required:** explicit expected-source set / source-policy binding, with missing required sources mapped to PARTIAL or failure.

### P0-2. Live source observations are not durably staged before terminal publication

A source adapter can return real observations, but a crash after retrieval and before result publication can cause the source to be queried again on retry.

The second query may return a changed external snapshot.

Existing retry semantics prove recoverability, but do not yet preserve the exact first observed live snapshot across that crash boundary.

**Required:** immutable/durable normalized-observation staging before typed result construction, with restart reuse of the staged snapshot.

### P0-3. Canonical geopolitical source breadth is still too narrow

The new canonical research path is strongest for disaster/earthquake data.

The repository already has a controlled-pilot Consilium official RSS adapter in the older live-source stack, but it is not yet migrated into the canonical source-observation contract.

GDELT remains a discovery source and recently returned HTTP 429 in the new owner-pilot path.

**Required:** migrate at least one official political/diplomatic source such as Consilium into the canonical research pipeline and validate mixed-domain execution.

### P0-4. Real HISTORICAL_AS_OF source evidence is fail-closed, not yet operational

The contract correctly prevents live retrieval from backdating `available_at_utc`.

For GDACS, USGS, GFZ and GDELT owner-pilot adapters, a present-time query cannot prove historical availability at an earlier `as_of_utc`.

This is safe, but it means the real historical research path is not yet proven.

**Required:** durable source snapshots/archives with recorded first-seen availability, then historical replay exclusively from evidence known available at the requested historical cutoff.

### P1-1. Cross-source event/claim identity is domain-specific

Structured identity/correlation is currently implemented for earthquakes.

Generic political, diplomatic, military and economic claims do not yet have equivalent typed correlation keys.

**Required:** domain-neutral claim/event identity or per-domain typed identity families.

### P1-2. Source adapter identity is validated but not fully policy-bound

Observation `source_id` is syntactically validated, but the generic worker does not yet enforce that an injected adapter may emit only the source identity assigned to it by an approved source specification.

**Required:** explicit adapter descriptor / expected source-id binding.

### P1-3. Source PARTIAL semantics remain coarse

The generic observation contract treats SUCCESS and PARTIAL similarly and does not preserve an explicit partial-error reason on evidence-bearing observations.

**Required:** typed partial reason/error semantics without allowing failed evidence to masquerade as successful evidence.

### P1-4. Duplicate evidence detection remains identity-based

Current duplicate rejection is based on `(source_id, observation_id)`.

Equivalent evidence can still be represented under multiple native observation ids.

**Required:** bounded evidence fingerprint / canonical provenance duplicate detection.

## Activation constraints preserved

Even after these readiness gaps are closed:
- production/live daemon activation remains separately owner-approved;
- Sentinel transport remains separately owner-approved;
- K-Trader integration remains separately owner-approved;
- paid providers/fallbacks remain prohibited;
- HP-OMEN remains excluded.

## Decision

Do **not** declare `KGM_INDEPENDENT_RESEARCH_READY`.

The owner-pilot path has advanced materially beyond the previous audit, but P0 completeness, durable observation snapshotting, canonical political-source breadth and real historical replay remain blocking.

## Next technical track

`SOURCE_PORTFOLIO_COMPLETENESS_AND_DURABLE_OBSERVATION_STAGING`

Priority order:
1. bind required source portfolio to execution;
2. durably stage normalized live observations;
3. prove crash/restart reuse without re-query;
4. migrate an official political source into the canonical path;
5. use staged first-seen evidence for historical replay.
