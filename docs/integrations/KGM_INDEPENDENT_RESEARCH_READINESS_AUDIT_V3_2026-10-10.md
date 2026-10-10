# KGM independent research readiness audit v3 — 2026-10-10

Status: **READY FOR OWNER-PILOT INDEPENDENT RESEARCH WITH P1 LIMITATIONS**

Gate:
`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS`

Exact validated implementation SHA: `322c55f8f47f62aca19fd563b3d7eb73538b1b52`.

Selected isolated exchange/research regression:
**249/249 PASS in 4.65 s**.

This gate applies only to the bounded private owner-pilot independent-research path. It does not authorize production/live daemon activation, persistent unattended scheduling, Sentinel transport, K-Trader integration, paid providers/fallbacks, shared runtime, public Plugin publication, or HP-OMEN use. The canonical Phase 23 strategic position remains separately gated.

## P0 readiness blockers from audit v2

### P0-1. Expected source portfolio not bound
**CLOSED.**

`kgm.source.policy.v1` binds consumer/policy, required source ids, optional source ids and the observation bound.

The policy-bound worker validates the complete adapter portfolio before PROCESSING. Missing required adapters and unknown adapters fail closed, and every adapter is bound to the source id it may emit.

False COMPLETE caused by accidentally omitting a required source is therefore denied.

### P0-2. Live observations not durably staged
**CLOSED.**

`kgm.research.observation-stage.v1` records an immutable normalized source snapshot before typed result construction.

Crash/restart acceptance proves:
- retrieval occurs once;
- the stage survives a crash after durable staging;
- retry reuses the exact staged snapshot;
- provider adapters are not re-queried;
- stage integrity and source-policy digest are validated.

### P0-3. Canonical geopolitical source breadth too narrow
**CLOSED FOR MINIMUM READINESS SCOPE.**

The canonical source contract now includes an official political/diplomatic source:

- Council of the EU / European Council Consilium press releases.

A real mixed-domain policy-bound cycle has been validated with:
- Consilium official political/diplomatic releases;
- GDACS disaster events;
- USGS earthquakes;
- GFZ GEOFON earthquakes;
- GDELT discovery path under fail-closed cooldown.

This closes the minimum breadth condition specified by audit v2. It does not claim comprehensive geopolitical-domain coverage.

### P0-4. Real HISTORICAL_AS_OF replay not operational
**CLOSED.**

Added immutable:
`kgm.research.evidence-archive.v1`.

Only a previously staged CURRENT snapshot may seed the archive.

Historical replay:
1. performs no provider/network calls;
2. requires an archived snapshot staged at or before `as_of_utc`;
3. requires the archived CURRENT request window to cover the requested historical window;
4. requires the same consumer/policy/source portfolio;
5. denies any archived evidence not known published and available by the requested cutoff;
6. rebinds the exact archived source snapshot to the historical request;
7. creates a new immutable observation stage and typed result from that snapshot.

A cutoff before first-seen staging has no eligible historical snapshot and fails closed.

## Real historical owner-pilot acceptance

A fresh real CURRENT mixed-domain source portfolio was captured and durably archived.

Current stage:
- observations: **41**
- Consilium: 10 / OBSERVED
- GDACS: 10 / OBSERVED
- GDELT: 1 / DEGRADED under active RATE_LIMITED cooldown
- GFZ: 10 / OBSERVED
- USGS: 10 / OBSERVED
- stage SHA-256:
  `ec9c2c4a28df332b52e6d265b780e21a7474b1b778dee3c68aa36f6be2a62743`
- current result:
  `result-000fea30af7ec8d6b78f5cc3`

A subsequent `HISTORICAL_AS_OF` request replayed from the archived snapshot only.

Historical result:
- status: PARTIAL
- observations: **41**
- same source snapshot: **true**
- maximum evidence `available_at_utc`:
  `2026-10-10T08:59:42Z`
- historical cutoff:
  `2026-10-10T08:59:44Z`
- GDELT network calls: **0**
- all provider network calls during historical replay: **0 by worker contract**
- historical stage SHA-256:
  `377811baccb993660879d6f75ee6b282f1cb8916713556025454e2e9733d696f`
- historical result:
  `result-7e93b41aa7c742826a5be357`
- recovery pending: empty.

The historical result remained PARTIAL because the archived required GDELT run was already DEGRADED; replay did not upgrade historical source health.

## Remaining P1 limitations

These do not block bounded owner-pilot independent research readiness, but remain required hardening work.

### P1-1. Generic non-earthquake event/claim identity
Earthquake identity/correlation is structured. Political, military and economic identity families remain incomplete.

### P1-2. Source PARTIAL semantics
Evidence-bearing PARTIAL observations do not yet carry a typed partial-reason field.

### P1-3. Evidence fingerprint duplicate detection
Duplicate detection remains primarily source/native-id based. Equivalent evidence under distinct native IDs can still evade canonical evidence-level deduplication.

The previous adapter source-id policy-binding limitation is **CLOSED** by `kgm.source.policy.v1` and the policy-bound worker.

## Readiness decision

The four P0 blockers defined by audit v2 are closed.

Therefore:

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS`

This means the private bounded owner-pilot KGM research path is ready for independent CURRENT and archive-backed HISTORICAL_AS_OF research under the validated source policy.

It does **not** mean:
- production service ready;
- unattended daemon ready;
- Sentinel transport ready;
- K-Trader integration ready;
- comprehensive geopolitical source coverage complete;
- automatic factual verification;
- public service/public Plugin ready.

## Next technical track

`P1_RESEARCH_QUALITY_HARDENING`

Priority:
1. generic typed event/claim identity families for political/military/economic domains;
2. typed PARTIAL reason semantics;
3. canonical evidence fingerprint duplicate detection;
4. broaden official political/military/economic source portfolio;
5. historical archive retention/indexing after correctness is preserved.
