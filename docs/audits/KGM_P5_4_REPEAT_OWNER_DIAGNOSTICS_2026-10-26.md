# KGM P5.4 — repeat owner live source probe with failure taxonomy

Date: 2026-10-26. Canonical GitHub Actions run: https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/40265906728

## Exact runtime observations

- Trigger: owner `workflow_dispatch` on `main`, source SHA `ba5cd2c0fd0aad416e97aaf2b08a7fa42382e036`.
- GitHub run 40265906728 completed SUCCESS. Job `one-shot-probe` ID `121388169626` completed SUCCESS; all job steps SUCCESS.
- Observation time `2026-10-26T03:49:09.378511+00:00`.
- Result: `collection_status=PARTIAL`, `source_success_count=1`, `source_failure_count=2`, `item_count=0`.
- Consilium (`consilium-press-releases`): `SUCCESS`, item_count 0, `ZERO_MATCHES_OR_EMPTY_FEED`. A successful empty filtered collection does NOT establish that official RSS itself is empty.
- GDACS (`gdacs-rss`): `FAILED`, `SIZE_LIMIT_EXCEEDED` under application-level 512KB response cap; do not describe as confirmed GDACS outage or permission denial.
- GDELT (`gdelt-doc-2`): `FAILED`, `NETWORK_FAILURE` without established DNS/TLS/timeout subclass. Do not infer a definitive provider outage.
- `analysis=NOT_EXECUTED`, `independent_claim_verification=NOT_ATTESTED`, `send=NONE`, `watch_persistence=EPHEMERAL_ONLY`.
- `network_policy=IN_PROCESS_ALLOWLIST_ONLY_NOT_OS_EGRESS_ATTESTATION`: no claim of OS-level network egress enforcement.

## Critic and next conditions

PASS: real owner manual event and complete bounded source-attempt accounting; safe source-level diagnostic categories; no report sending.

PARTIAL: 1/3 source attempts succeeded but produced zero evidence.

SHORTFALL: zero collected source items, no date/freshness checks on articles, no provenance or independent corroboration, and no actual geopolitical report.

Corrective plan:
1. GDACS: inspect compressed vs uncompressed response size and negotiate/feed pagination or metadata-only bounded variants where officially documented; do not unilaterally raise global 512KB response limit.
2. GDELT: distinguish DNS/network timeout/TLS/connectivity and HTTP outcomes using enum-only diagnostics; avoid raw URLs, source data and environment details.
3. Consilium: verify raw feed entries count separately from filtered query matches using small bounded metadata counters; avoid claiming source coverage on a zero-match topic.
4. Add offline regression tests, preserve existing owner-only explicit manual trigger and NO_SEND, then re-run only upon owner instruction.

Gate: `P5_4_REPEAT_DIAGNOSTICS_PARTIAL_ZERO_EVIDENCE / P5_5_REPORT_BLOCKED / PRODUCTION_NO_GO`. Policy: FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD.
