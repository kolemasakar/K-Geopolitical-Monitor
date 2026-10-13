# P24.1 Regional Official Sources — African Union Preflight

2026-10-13. Status: SOURCE_CANDIDATES_REGISTERED / AU_FIXTURE_GATE_PASS / AU_LIVE_GATE_BLOCKED.

## Four candidate publishers
| Region | Official candidate | Observed transport from owner-pilot | Live parser acceptance |
|---|---|---|---|
| Africa | https://au.int/en/happening/pressreleases | prior HTTP200, later HTTP403 | NOT PASSED |
| Asia | https://asean.org/category/news/ | HTTP307 redirect unresolved | NOT PASSED |
| Middle East | https://gcc-sg.org/en/MediaCenter/News/Pages/default.aspx | HTTP200 | NOT PASSED |
| Americas | https://www.oas.org/en/media_center/press_releases.asp | HTTP403 | NOT PASSED |

These four sites do not count as active research sources, factual verification or global coverage. They are publisher-origin candidates only.

## AU research implementation
- PR #171: four-region candidate catalog, fail-closed not-enabled status; CI #3058 SUCCESS with 1765 passed.
- PR #173: African Union single-article parser on controlled local HTML fixture. Strict allowlisted official AU host/path, explicit publication timestamp, missing/invalid/naive date fail-closed, transport UNAVAILABLE, historical no-lookahead, never promotes event to verified.
- Focused ARM64 31 passed at code SHA 26d43f27baa04337abe7d63f496d36114442b26c; final full regression and exact-head CI required before closure.
- Example primary AU news release: https://au.int/en/pressreleases/20261012/african-union-advances-implementation-africa-urban-resilience-programme
- Source publication day Oct 12 and event described as September AU working-group meetings are separate, not interchangeable event and reporting timestamps.
- HTTP403 on latest direct owner-pilot request prevents empirical live-source parser acceptance. Do not claim live adapter works. No bypass, paid provider or unapproved proxy.

## Remaining gates
1. Accept PR #173 into PR #171 only after green exact-head CI and ARM64; then accept PR #171 into draft research PR #163 after updated CI.
2. Separately validate actual AU HTML response before any source activation. The synthetic fixture is not a representation of verified production markup.
3. Expand candidate investigation and language/precision fixtures for other regions under separate scoped gates.
4. Preserve canonical Phase 23 P23.4 gate and research PR #163 draft; no production, unattended execution, public Plugin or K-Trader/K-Sentinel integration.
