# P5.4 Source diagnostics v2 — scoped repair and Critic (2026-10-26)

Actual owner run 40265906728 returned Consilium SUCCESS/0, GDACS SIZE_LIMIT_EXCEEDED (512,000-byte cap), GDELT NETWORK_FAILURE without subclass. No independently verified evidence acquired, so P5.5 remains blocked.

## Scoped changes
- GDACS RSS only: configurable per-endpoint cap at most 2,000,000 bytes; owner probe uses 1,500,000 bytes for GDACS, while Consilium/GDELT remain at 512,000 bytes. Three-source total is still bounded. No new endpoints.
- GDELT transport error subclass: DNS, timeout, TLS, refused connection and other. Only fixed-safe enum outputs, no raw error details, URLs or source content. No automatic retry and no TLS bypass.
- Consilium: after successfully bounded RSS read, count total item entries and entries matching the simple textual query before filter. Counts are aggregate only; no raw item content logged.
- Owner-only manual workflow and endpoint allowlist unchanged. No production writes, no scheduled watches, no send.

## Critic
- These improvements are not an OS-level egress policy.
- The 1.5MB GDACS cap may still be insufficient. Official GDACS 2025 documentation lists paged API alternatives, but no unverified alternate endpoint is enabled here. See https://gdacs.org/Documents/2025/GDACS_API_quickstart_v1.pdf.
- GDELT timeouts are only classified, not automatically retried.
- Consilium text matches are not full semantic relevance.
- No actual publication freshness, independence, corroboration or full report is attested.
- Actual effectiveness requires one separate manual owner dispatch after CI and merge.

Gate: P5_4_DIAGNOSTIC_V2_OFFLINE_CI_PENDING / LIVE_RECHECK_PENDING / P5_5_REPORT_BLOCKED / PRODUCTION_NO_GO. FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD preserved.
