# KGM P5.4 diagnostic-only revision — 2026-10-26

The actual owner one-shot run 40265116609 completed at source collection status PARTIAL with 0 items: Consilium SUCCESS/0; GDACS and GDELT FAILED/0. The previous aggregate intentionally omitted error strings and cannot prove upstream outage or cause.

This revision adds **bounded, non-sensitive source diagnostic classifications**, not a new endpoint or a new background mechanism. Exact HTTP error status from existing transport is mapped to `source_http_status_NNN` internally; reported status is only a three-digit code and fixed `HTTP_RESPONSE_FAILURE` category, never raw response, redirect, URL, error text, credentials, query, or source content. Network, redirect, response-size, RSS/GDELT parse failures map to fixed enums. Unknown errors remain UNKNOWN. No retry occurs automatically.

An adapter successfully returning 0 items is labeled `ZERO_MATCHES_OR_EMPTY_FEED`. This is not source corruption and is not evidence the queried event is absent; it may reflect topic mismatch, feed window, or empty feed.

The original public source probe remains owner-only `workflow_dispatch`, topic validated, isolated project SQLite, no persistent watches and no send. Bounds remain three fixed public HTTPS sources, max three requests, seven-second per-source timeout and response limit 512KB. There is no OS-level egress firewall on the live runner; it **must not be called production-approved**.

Acceptance: CI/tests for these categories and normal project regression; actual effectiveness of categories requires **one separate explicit owner manual run**, without automatic repeat or a schedule. P5.5 independent provenance and report gate remains BLOCKED until data exists.

FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
