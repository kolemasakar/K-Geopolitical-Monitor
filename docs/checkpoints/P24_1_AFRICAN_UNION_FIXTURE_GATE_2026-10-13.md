# P24.1 African Union Single-Article Adapter: Fixture Gate

Date: 2026-10-13
Status: FIXTURE_VALIDATED, LIVE_RESPONSE_BLOCKED, NOT_ACTIVATED

## Real primary-source inspection (read-only)
- African Union publisher list: https://au.int/en/happening/pressreleases
- Example release: https://au.int/en/pressreleases/20261012/african-union-advances-implementation-africa-urban-resilience-programme
- Public indexed page representation shows heading and publication date Oct 12, 2026; AU urban resilience working group held meetings Sept 22–24 (different event dates).
- Direct HTTPS owner-pilot page retrieval yielded HTTP 403 on recent attempt; a prior directory request had returned HTTP 200. NO live end-to-end parse accepted.

## Implementation
- New isolated research_source_african_union_v1.py; no source registration, unattended activation or deployment.
- Restrict to allowlisted au.int official HTTPS article URLs; reject fragments, credentials, foreign domains and unapproved paths.
- Explicit metadata date required from article published-time, JSON-LD datePublished or time datetime. Date-only input uses a UTC midnight day anchor, NOT an asserted exact publication clock.
- Fail closed on malformed HTML, missing heading, oversized payload, invalid or naive date. Transport exceptions produce UNAVAILABLE, not fabricated no-event.
- Historical observed-after-cutoff records INVALID with HISTORICAL_AVAILABILITY_UNPROVEN.
- AU is the publisher origin; its attribution never establishes factual corroboration of political or military claims.

## Test scope
- Controlled synthetic fixture (not real AU HTML): 18 parser/negative cases; 13 candidate source gate cases.
- Isolated owner-pilot ARM64 focused run on code SHA 26d43f27baa04337abe7d63f496d36114442b26c: 31 PASS in 0.15s.
- Full exact-head ARM64 and CI pending. PR #173 stacked on PR #171, itself stacked on unmerged research PR #163.
- Before actual live-source acceptance, fetch original HTML on approved network, inspect terms and timestamp precision, record fixture and prove source parser normalizes real publisher markup; obtain separate owner-pilot activation gate.
