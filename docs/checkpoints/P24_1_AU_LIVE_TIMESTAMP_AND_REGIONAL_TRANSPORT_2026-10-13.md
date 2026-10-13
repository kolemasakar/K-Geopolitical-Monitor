# P24.1 — African Union Live-Response Timestamp Repair and Regional Transport

Date: 2026-10-13. Status: AU_LIVE_TIMESTAMP_FIX_PASS / RESEARCH_ONLY / P24_1_CONTINUES.
Research PR #177 based on independent draft research PR #163; current validated code HEAD ed4ce2a8c4f463a03c0b34f87c8a5293ccd9bd16.

## Verified primary African Union page
URL: https://au.int/en/pressreleases/20261012/african-union-advances-implementation-africa-urban-resilience-programme
Owner-pilot HTTPS returned HTTP 200 and 124530-byte HTML. Existing AU parser incorrectly selected the first time element from a carousel of unrelated newer news, returning 2026-10-13T15:03:10Z for a release dated October 12. This was a REAL parsing/provenance error, not acceptable live verification.
Actual African Union pressrelease article contains field--name-field-date with datetime=2026-10-12T07:15:26Z. New parser scopes this timestamp to article.node-pressrelease rather than sitewide time; exact observed date 2026-10-12T07:15:26Z.
New negative tests reject sidebar-only date and require article-level publisher metadata; the fixture where newer carousel date precedes actual article date must yield actual article date.
On isolated ARM64 exact research HEAD, focused AU suite: 20 PASS. Live repeat: AU parser SUCCESS and source origin african-union, published_at_utc=2026-10-12T07:15:26Z, no automatic VERIFIED credit.
Important temporal distinction: release published October 12 describes programme meetings held September 22-24. This is NOT a new October meeting.

## Regional access boundaries
- ASEAN: both https://asean.org/category/news/ and home route returned HTTP307 via Sucuri Cloudproxy, with no Location header supplied to Python client. No accepted body or live parser.
- OAS: https://www.oas.org/en/media_center/press_releases.asp returned HTTP403 with Cloudflare. A separate public search interface indexed official OAS press-release pages (for instance https://www.oas.org/en/media_center/press_release.asp?sCodigo=S-104), but this DOES NOT establish owner-pilot direct access or permission for a live source adapter.
- African Union: prior HTTP403 is now observed recovered for specific article URL. One live page is successfully parsed with scoped timestamp correction; intermittent transport should remain monitored at bounded cadence.
- GCC: previous official GCC parser remains real-response SUCCESS but unactivated.
- GDELT: previous TCP connection succeeded with TLS handshake timeout, no observed HTTP status, not proven 429.

## Acceptance and restrictions
Full exact-head isolated ARM64 research suite and GitHub CI of PR177 must pass before code merge. Documentation-only PR against main does not activate research code or close P24.1. No paid services, VPN/proxy bypass, continuous polling, production, public Plugin, K-Sentinel or K-Trader integration.

## Final verified acceptance

GitHub CI #3113: 1802 passed in 235.33s. Isolated exact-head ARM64: 1802 passed in 460.89s at source HEAD ed4ce2a8c4f463a03c0b34f87c8a5293ccd9bd16. Code PR #177 merged ONLY into separate draft research PR #163 at SHA 8e79191eba704927df0ff8b069c2d19095b8f378. Main does not contain research code. New source is not activated. Live AU release timestamp 2026-10-12T07:15:26Z is attributable to the actual article field, not a sidebar.
