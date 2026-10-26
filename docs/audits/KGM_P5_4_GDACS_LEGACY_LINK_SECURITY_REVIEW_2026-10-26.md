# P5.4 — GDACS legacy HTTP link normalization design and GDELT HTTP 429 policy

Date: 2026-10-26. Based on manual run #40270968105, GDACS 320 feed entries, one topic match, one unsafe/non-HTTPS URL, zero accepted; GDELT HTTP 429.

## Upstream reference and constraint
Official GDACS historical guidelines listed the RSS feed as HTTP at `http://www.gdacs.org/xml/rss.xml`: https://www.gdacs.org/documents/gdacs%20guidelines%202014_-_final.pdf. Its 2025 API quick-start describes RSS/XML via https://www.gdacs.org/feed_reference.aspx and HTTPS API routes: https://www.gdacs.org/Documents/2025/GDACS_API_quickstart_v1.pdf. These sources support legacy HTTP usage in the ecosystem but **do not prove the scheme/host/path of the one specific rejected item in the actual October 26 feed**.

## Narrow trust rule (reviewed design)
A legacy article URL may be normalized to HTTPS **only when** original host is exactly `gdacs.org` or `www.gdacs.org`, scheme is HTTP or HTTPS, no credentials, custom port, fragment, backslash or control characters, path begins with a single slash, and URL length <=2048. Normalization creates `https://www.gdacs.org/<unchanged path and query>` without issuing any request for the article. Unknown hosts, special URLs, suspect authority and any other HTTP sites remain rejected. The original link text is never placed in GitHub output. Admitted record metadata tags normalization reason `TRUSTED_GDACS_HTTP_NORMALIZED`.

This is a **security-scoped enhancement**, not proof that the resulting URL is reachable or that its content is verified. A URL pointing to a GDACS redirect endpoint may still redirect at later consumer retrieval; downstream fetching must use its own strict redirect and egress allowlist and cannot silently follow arbitrary hosts. Claim provenance remains unverified. Do not treat GDACS feed entry as independently verified intelligence.

GDACS metadata counters now distinguish `ADMITTED` from `TRUSTED_GDACS_HTTP_NORMALIZED` and continue reporting other failures. Synthetic tests cover exact-host acceptance, credential spoofing, off-domain links, unusual ports and fragments, and confirm article URL never fetched here.

## GDELT HTTP 429
Actual run reported HTTP 429: rate-limiting. Do NOT loop requests, rotate IPs/proxies to bypass limits, ignore Retry-After, disable TLS, or automatically schedule a retry. Existing diagnostic retains `MANUAL_BACKOFF_ONLY` and marks collection PARTIAL. Any new direct GDELT collection requires a deliberate owner-authorized request after a reasonable cooldown, consistent with provider terms.

## Status
Offline code acceptance subject to full CI. Further live verification of the single GDACS entry still **PENDING**. P5.4 live source evidence = zero. P5.5 analysis, claim verification and report remain BLOCKED. No production access, watch activation or sends.

FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
