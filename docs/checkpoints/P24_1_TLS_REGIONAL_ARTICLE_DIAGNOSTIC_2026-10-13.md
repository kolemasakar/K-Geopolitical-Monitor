# P24.1 — GDELT TLS isolation and regional article-level reachability

Date: 2026-10-13; status: RESEARCH_ONLY / P24_1_IN_PROGRESS.

## Owner-pilot one-shot diagnostics
Host `kgm-e4-owner-pilot`, `aarch64`. One DNS/TCP/TLS diagnostic to `api.gdeltproject.org:443` with 4 s TCP and 5 s TLS socket timeouts:
- DNS `socket.getaddrinfo`: SUCCESS, IPv4 104.197.47.124.
- TCP connection to 104.197.47.124:443: SUCCESS.
- Python stdlib SSL handshake with SNI `api.gdeltproject.org`: `TimeoutError: _ssl.c:983: The handshake operation timed out`.
- No HTTP status received; **not evidence for HTTP 429** or an upstream service-wide outage. No proxy/VPN/paid fallback.

One independent bounded direct HTTPS GET per URL (redirect following disabled, requests timeout 4s connect + 6s read):

| Official URL | Direct owner-pilot result | Assessment |
|---|---|---|
| https://www.oas.org/en/media_center/press_release.asp?sCodigo=S-104 | 403 Cloudflare, 5611-byte denial | Per-article URL not accepted for live parsing |
| https://oas.org/en/media_center/press_release.asp?sCodigo=E-096%2F26 | 403 Cloudflare, 5600-byte denial | Alternate bare-host path also blocked |
| https://asean.org/ | 307 Sucuri/Cloudproxy, 1359 bytes, no Location | Home route also blocked; not a parser body |

Separate public web discovery observed official OAS article texts at https://www.oas.org/en/media_center/press_release.asp?sCodigo=S-104 and https://oas.org/en/media_center/press_release.asp?sCodigo=E-096%2F26; this is **only indirect retrieval** and is **not** evidence of accessible owner-pilot official source transport, verified provenance chain or content freshness.

## Decisions and constraints
- GDELT: `DNS_PASS/TCP_PASS/TLS_HANDSHAKE_TIMEOUT/HTTP_UNOBSERVED`; preserve `TRANSPORT_UNAVAILABLE`, avoid false rate-limit assertion.
- ASEAN: `307_NO_LOCATION`; no redirect target invented.
- OAS: `403_CLOUDFLARE` on both listing (prior checkpoint) and two individual release paths; source remains blocked.
- No origin-independence or VERIFIED credit; no source activation, scheduler, production, service restart, paid/HP-OMEN, Plugin release, Sentinel or K-Trader effect.
- Before source admission: legitimate official feed/direct-page transport from isolated owner-pilot, article-scoped deterministic parser, negative provenance/timestamp tests, exact-head CI and ARM64 regression, separate owner approval.
