# P24.1 Source Coverage & Research Quality — Initial Inventory (2026-10-11)

Status: **INVENTORY STARTED — NO NEW SOURCE ACTIVATION**.

Scope: independent KGM research only. Inventory describes source adapter modules on PR #163 exact research implementation HEAD `f135014e2962907c76ea14bf3b10ddc7c288046c`, NOT currently deployed/healthy live coverage.

## Adapter inventory

| Domain | Source ID | Implementation |
|---|---|---|
| Political / diplomatic | `consilium-press-releases` | `research_source_consilium_v1.py` |
| Political / official | `germany-federal-government` | `research_source_bundesregierung_v1.py` |
| Political / official | `france-presidency` | `research_source_elysee_v1.py` |
| Political / official | `govuk-official` | `research_source_govuk_v1.py` |
| Diplomatic | `moldova-mfa` | `research_source_moldova_mfa_v1.py` |
| Defense / diplomatic | `nato-news` | `research_source_nato_v1.py` |
| Economic | `ecb-press` | `research_source_ecb_v1.py` |
| Disaster | `gdacs-events` | `research_source_gdacs_v1.py` |
| Earthquake | `usgs-earthquake` | `research_source_usgs_v1.py` |
| Earthquake | `gfz-geofon` | `research_source_gfz_v1.py` |
| Cross-domain discovery | `gdelt-doc-v2` | `research_source_gdelt_v1.py` |

**Count: 11** distinct dedicated adapter modules. Other KGM source inventory/framework modules are outside this specific owner-pilot adapter count.

## Known acceptance evidence vs caveats

- Source presence in source code is **not** evidence of current successful live access, geographic coverage, completeness, quality or reliability.
- The existing research state records successful individual live owner-pilot scenarios for official political, diplomatic, military/security and economic sources; earthquake distinct-origin pairing GFZ/USGS and disaster GDACS.
- `gdelt-doc-v2` has been observed `RATE_LIMITED_COOLDOWN` and degraded in a prior bounded portfolio; current live state requires fresh read-only evaluation.
- GDACS earthquake records can share `usgs-neic` underlying origin with USGS: separate feeds must not be counted automatically as independent corroboration.
- Explicit generic mapping is conservative: exact structured identities, no fuzzy/NLP merge; `UNVERIFIED` remains until explicit factual verification.
- Previous two-origin NATO + Moldova MFA example demonstrated source contributions and canonical corroboration, but is not a statistically representative coverage benchmark.

## P24.1 next acceptance steps

1. Build a source/region/domain/claim-type coverage matrix from the code, source policy and preserved owner-pilot evidence; distinguish `ADAPTER_PRESENT`, `TESTED_SYNTHETIC`, `TESTED_LIVE_HISTORICAL`, and `VERIFIED_LIVE_CURRENT`.
2. Run bounded free/read-only source health and evidence-contribution checks without enabling scheduler/production; capture source-specific errors and response timestamps.
3. Select representative cross-source events for political, diplomatic, military and economic domains; test same-origin, distinct-origin, claim agreement, claim disagreement, duplicate evidence, null and partial sources.
4. Establish measurable acceptance thresholds only after this grounded inventory; identify missing geographies and domains explicitly.
5. Record reproducible isolated ARM64 exact-head regression for each accepted implementation delta.

## P24.0 dependency

PR #163 research exact HEAD full ARM64 suite **1722/1722 PASS** (444.89 s), CI #2900 SUCCESS. PR #164 planning branch CI #2911 FAILED at head `9a035649b1b8a3fe131a4e11ff18d3966dfce4d2`; root cause not yet confirmed. P24.0 remains open until its own planning CI and cross-source consistency are resolved. PR #163 remains Draft and is not merged.

## Isolation

No persistent unattended operation, no production, no Sentinel/K-Trader integration, no paid services, shared resources, public Plugin or HP-OMEN.
