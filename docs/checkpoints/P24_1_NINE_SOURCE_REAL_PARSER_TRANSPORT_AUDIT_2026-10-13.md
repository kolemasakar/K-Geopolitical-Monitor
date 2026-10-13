# P24.1 — Nine Real-Response Parser Acceptance and Transport Boundary

Recorded: 2026-10-13. State: P24_1_IN_PROGRESS / NINE_OF_ELEVEN_REAL_RESPONSE_PARSER_PASS.
Host: isolated kgm-e4-owner-pilot, Python imports explicitly pointed at research source checkout.
Reference research PR #163 HEAD before current P24.1 test PR: 2bfd2cc4b0c71072abff64d4be1231a11feb2cfc.

## Read-only real endpoint probes (bounded single HTTPS attempt per endpoint)

| Adapter | Normalization on actual public response | Observations | Notes |
|---|---|---:|---|
| GOV.UK | SUCCESS | 1 | Earlier Oct 13 direct article; exact UTC publication time. |
| Bundesregierung | SUCCESS | 1 | Earlier Oct 13 direct article; date-only UTC anchor, NOT clock precision. |
| Consilium RSS | SUCCESS | 3 | Oct 13: same Council origin across all 3. |
| ECB RSS | SUCCESS | 3 | Oct 13: one ECB origin across entries. |
| GDACS SEARCH | SUCCESS | 3 | Oct 13: two USGS-NEIC origin tags; one unknown; cannot count independent of USGS. |
| GFZ GEOFON text | SUCCESS | 3 | Oct 13: GFZ origin, publication-at field reflects observation time, not independent historical release timestamp. |
| NATO news search | SUCCESS | 2 | Oct 13: NATO origin; listing time precision limited. |
| Moldova MFA | SUCCESS | 1 | Oct 13: source Romanian article, 2026-10-07T10:51:51Z publication; official origin only. |
| Elysee | SUCCESS | 1 | Oct 13: older official article published 2026-05-05; date-only anchor; article contains later-linked material, beware event vs page publication dates. |
| USGS FDSN query | UNAVAILABLE | 1 explicit error | Oct 13: bounded 7s timeout; not proof of upstream outage or no earthquakes. |
| GDELT DOC v2 | UNAVAILABLE | 1 explicit error | Oct 13: one 6s timeout; earlier TLS handshake timeout. No unbounded retries, no evidence of general outage. |

The 9/11 denominator is the adapter inventory, not geographic/global coverage. It describes at least one observed successful parser response across two bounded checks. Do not treat counts as number of independently confirmed geopolitical events.

## Source independence and meaning
- Nine parsers handling real responses is not nine independent corroborations for any one substantive claim.
- Cross-publisher or cross-feed reuse of underlying origin is common: two GDACS earthquake records were tagged usgs-neic; a separate USGS item would not add independent origin by itself.
- EUROPE/OECD official policy feeds and global geophysical/disaster endpoints dominate dedicated research coverage. Africa, Asia, Middle East and Americas official political adapters remain coverage gaps.
- Date-only page timestamps and first observed availability differ from verified exact publication times. Unknown timing must not be reconstructed as precise.
- Official-source statements prove attributable publication, not the truth of contentious claims.

## Deterministic contract tests
- Research PR #168 (stacked on draft PR #163) adds 7 tests on a new research-only code branch.
- Explicit transport failures: GDELT TimeoutError/OSError => UNAVAILABLE, max_attempts=1; USGS timeout => UNAVAILABLE, never empty/zero-event success.
- GDACS NEIC same-origin identity and unknown-origin non-promotion; malformed ECB/GFZ payloads fail closed.
- Focused suite on exact research code HEAD fe83fdf1206af02512e21092f410c695b2614c3f: 51 passed in 0.80 s on isolated ARM64.
- Full GitHub CI and exact-head research regression required before accepting code PR #168.

## P24.1 follow-up
1. Separate transport availability, successful normalization, origin independence and fact corroboration in all coverage scores.
2. Assess bounded USGS/GDELT transport recovery and error taxonomy (TLS/timeout vs 429) without bypassing cooldown, proxy or paying.
3. Extend regional original-source adapters for Africa, Middle East, Asia and Americas only after representative fixture/source licensing and owner-pilot validation.
4. Keep canonical P23.4 gate and draft PR #163 independent. Do not activate production/unattended/public Plugin/paid services/K-Trader/K-Sentinel.

## Bounded retry correction — same day, after initial snapshot

A second, deliberately bounded USGS diagnostic found FDSN version HTTP200 and FDSN GeoJSON query HTTP200. Repeating the **actual USGS adapter** with max_results=2 successfully normalized two public events, both status SUCCESS and origin `usgs-neic`; update timestamps were `2026-10-13T10:20:27Z` and `2026-10-13T10:57:06Z`. Therefore the UPDATED evidence total is **10/11 adapters with at least one successful real-response parse**. The earlier timed-out USGS query is retained as historical evidence of a transient transport failure, not overwritten.

GDELT remained unavailable under a bounded 5-second check with TLS handshake timeout. GDELT is now the sole adapter without a confirmed successful live-response parse in this checkpoint. No blanket outage, firewall cause, or paid bypass is inferred.

**CURRENT CHECKPOINT STATUS = TEN_OF_ELEVEN_REAL_PARSER_PASS_GDELT_TRANSPORT_DEGRADED.** The file name preserves original checkpoint identity; this addendum supersedes the initial 9/11 tally, not its first observation log.

## GDELT transport-layer diagnostics

Read-only DNS lookup resolved api.gdeltproject.org to 104.197.47.124 (observation, not a pinned/guaranteed address). curl with `--max-time 6` connected to destination TCP/443, transmitted TLSv1.3 ClientHello, then timed out without receiving a completed TLS handshake or HTTP status; curl error 28. Thus: DNS=OK, TCP_CONNECT=OK, TLS_HANDSHAKE=TIMEOUT, HTTP_STATUS=NOT_OBSERVED. Cannot classify the current failure as HTTP 429, nor prove server-side outage versus network-path filtering. No VPN/proxy bypass, excessive retries, paid fallback or production reconfiguration was attempted.
