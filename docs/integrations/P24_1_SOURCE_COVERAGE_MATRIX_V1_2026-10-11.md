# P24.1 Source Coverage Matrix v1 — 2026-10-11

Status: INITIAL CODE + HISTORICAL ACCEPTANCE INVENTORY (current live availability not yet verified).

Authority: research-source implementation on PR #163 head `f135014e2962907c76ea14bf3b10ddc7c288046c`, and stored `docs/state/CURRENT_PROJECT_STATE.json` owner-pilot evidence. Independent live health checks are a separate acceptance requirement.

| Source ID | Family / geo-institution | Origin group | Prior evidence | Current availability |
|---|---|---|---|---|
| `consilium-press-releases` | EU political/diplomatic | `consilium-eu-council` | Prior live mixed-domain sample | NOT REVALIDATED |
| `germany-federal-government` | Germany / political, military | `germany-federal-government` | Prior live mapped political/military cases | NOT REVALIDATED |
| `france-presidency` | France / political, economic | `france-presidency` | Prior live mapped economic case | NOT REVALIDATED |
| `govuk-official` | UK / political, military, economic | `uk-government` | Prior live mapped multi-domain cases | NOT REVALIDATED |
| `moldova-mfa` | Moldova / diplomatic | `moldova-mfa` | Prior NATO/Moldova live corroboration | NOT REVALIDATED |
| `nato-news` | NATO / military, diplomatic | `nato` | Prior NATO/Moldova live corroboration | NOT REVALIDATED |
| `ecb-press` | Euro area / economic | `ecb` | Prior live official economic source cycle | NOT REVALIDATED |
| `gdacs-events` | Global / disasters | variable, including `usgs-neic` for sourced EQ | Prior live E2E | NOT REVALIDATED |
| `usgs-earthquake` | Global / earthquakes | `usgs-neic` | Prior live corroboration | NOT REVALIDATED |
| `gfz-geofon` | Global / earthquakes | `gfz-geofon` | Prior live independent-origin EQ cases | NOT REVALIDATED |
| `gdelt-doc-v2` | Global / media discovery | publication-dependent, cannot assume independent | Prior RATE_LIMITED_COOLDOWN/DEGRADED | NOT REVALIDATED |

## Code-driven limitations

- There are eleven dedicated research-source adapter modules in the PR #163 research implementation; this count does not represent all sources in legacy KGM source portfolios.
- Coverage is concentrated in Europe, transatlantic institutions, disaster and earthquake data. This *suggests* regional/source gaps elsewhere but does not quantify actual country or event-type coverage.
- `gdelt-doc-v2` is discovery, not automatically independent official factual confirmation.
- GDACS and USGS may share an underlying `usgs-neic` origin; independent publication URLs alone do not produce distinct-origin credit.
- Source mapping-profile support is explicit and optional for several official adapters. A source's ability to fetch is not proof that an event maps into canonical generic identity for any specific story.
- No automatic factual VERIFIED status is allowed from matching origin or claim records alone.

## Test acceptance matrix to complete

- **Availability:** fresh UTC access, response status, parser result, no credential/paid fallback, source-contribution status.
- **Mapping:** event identity and claim-signature populated only when exact controlled descriptors match; unsupported events fail closed.
- **Corroboration:** distinct vs same underlying origin, agreement vs disagreement, duplicate evidence, no false verification.
- **Geographic gaps:** compare Europe/Atlantic coverage to Asia, Africa, Middle East and Americas before prioritizing additional public official adapters.
- **Reliability:** healthy-empty vs degraded, cooldown 429, bounded timeouts, safe historical replay, deterministic deduplication.
- **Release:** each new adapter/mapping profile needs its own reproducible isolated ARM64 and CI evidence. No production runtime activation.

## Gate dependencies

Phase 24 is owner-approved; P24.0 planning CI must be green before formal gate closure. PR #163 stays draft pending scoped split; this inventory is documentation-only in PR #164.

## Bounded current transport probe — 2026-10-11 (owner-pilot VM)

Read-only HTTPS GET, up to 10 seconds per URL, on `kgm-e4-owner-pilot`:

| Public endpoint | HTTP | Duration (s) |
|---|---:|---:|
| Consilium press RSS | 200 | 0.110 |
| ECB press RSS | 200 | 0.100 |
| NATO home page | 200 | 0.172 |
| GDACS events SEARCH API | 200 | 0.937 |
| USGS earthquake FDSN version | 200 | 0.476 |
| GFZ GEOFON FDSN version | 200 | 0.170 |

These confirm basic HTTP reachability **only**, not parser readiness, API query coverage, mapped-event correctness, current contributor status, payload freshness or sustained reliability. NATO home and FDSN version routes are not full functional acceptance endpoints. The other five dedicated official adapters and GDELT are not part of this transport probe. No production/scheduler enabled.
