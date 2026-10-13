# P24.1 — regional official-source transport recheck (2026-10-13)

**Status:** TRANSPORT_RECHECK_COMPLETE / P24_1_IN_PROGRESS / RESEARCH_ONLY.

## Provenance

- Host: `kgm-e4-owner-pilot`, native `aarch64` (isolated owner-pilot; **not** production verification).
- UTC host time at resumed session: `2026-10-13T17:59:23Z`.
- Code reference: PR #163, separate draft research head `8e79191eba704927df0ff8b069c2d19095b8f378` retrieved with read-only Git fetch from the existing isolated checkout. This recheck did **not** modify PR #163 or its working tree.
- Transport: Python requests, **one** direct HTTPS GET per URL; `allow_redirects=False`, bounded connect/read timeout `(4, 6)` seconds, no credentials, proxy bypass or paid provider.

## Actual observations

| Source | Requested official URL | Observed outcome | Interpretation |
|---|---|---|---|
| ASEAN | https://asean.org/category/news/ | HTTP 307; response Server: Sucuri/Cloudproxy; `Location` header absent; 1411 response bytes | Direct owner-pilot source article fetch not established; no redirect target inferred and no parser acceptance |
| OAS | https://www.oas.org/en/media_center/press_releases.asp | HTTP 403; response Server: cloudflare; `Location` header absent; 5578 response bytes | Direct official press-release listing blocked; no page-content parser acceptance |
| GDELT | https://api.gdeltproject.org/api/v2/doc/doc?query=ukraine&mode=artlist&format=json&maxrecords=1 | Python requests `ConnectTimeout` during bounded TLS/HTTPS connection; no HTTP response code | Network transport unavailable in this one observation, not proof of upstream 429 or a GDELT outage |

## Gate decision

- `asean-news`: **BLOCKED_TRANSPORT_307 / NO_LIVE_PARSER**.
- `oas-press`: **BLOCKED_TRANSPORT_403 / NO_LIVE_PARSER**.
- `gdelt-doc-v2`: **TRANSPORT_UNAVAILABLE / NO_HTTP_STATUS**.
- **No automatic VERIFIED, independent-origin credit, freshness, source activation, production or cross-project effects.**
- African Union and GCC live-parser PASS from earlier documented, separately tested official article samples remain research-only. A live parser PASS is not verified factual evidence and does not imply uninterrupted source availability.

## Suggested next engineering gates

1. ASEAN: inspect and document Sucuri interstitial as a *blocker*; do not assume that site HTML/JSON is an article or invent a Location target. Any alternative official public feed must be provenance-checked and separately admitted.
2. OAS: research alternative public official per-article or syndication URLs without evading access controls; retain 403 fail-closed for the direct listing.
3. GDELT: compare DNS/TCP/TLS endpoints under a strictly bounded one-shot diagnostic, distinguish connect from handshake failure; no unbounded retries or proxies.
4. Split PR #163 (currently 189 changed files) before any canonical-main research code acceptance; preserve P23.4 and explicit source-activation gate.

No production changes, service restart, persistent scheduler, public Plugin change, resource-limit relaxation, paid fallback, VPN or source activation occurred in this recheck.
