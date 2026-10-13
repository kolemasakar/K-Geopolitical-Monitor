# P24.1 — Official alternative feeds and PR #163 split audit

Date: 2026-10-13. Scope: read-only research and documentation only. **No activation or production changes.**

## Official-source alternatives

### OAS
- The official OAS Permanent Council publishes an RSS directory: https://www.oas.org/en/council/RSS/ . **This is a feed for Council work documents, not a substitute for OAS press releases**. Catalog candidate only; scope must remain `oas-permanent-council-documents` rather than claim press-release coverage.
- Official OAS press-release archives expose year/month paging: https://www.oas.org/en/media_center/press_releases.asp?nAnio=2026&nMes=9 . External public retrieval/indexing is possible, but owner-pilot direct transport is not demonstrated.
- Owner-pilot direct probe to https://www.oas.org/en/council/RSS/ returned HTTP403. No OAS candidate admitted.

### ASEAN
- Owner-pilot direct GET https://asean.org/feed/ returned HTTP403.
- Owner-pilot direct GET https://asean.org/wp-json/wp/v2/posts?per_page=1 returned HTTP307.
- Prior https://asean.org/ and https://asean.org/category/news/ were HTTP307 Sucuri without a useful Location. None are verified stable official feed transport from the host.
- WordPress-compatible URL shape does not prove API support, publication provenance or license. Source activation remains blocked.

### GDELT route gate
- Isolated owner-pilot GDELT DNS and TCP succeeded; TLS with SNI timed out. No HTTP status. Fail-closed as `TRANSPORT_UNAVAILABLE`.
- **No other KGM-approved isolated free egress host is confirmed for a route comparison.** Shared KRC/K-Trader, HP-OMEN, VPN or paid egress are not implicitly authorized. This gate remains blocked rather than claiming a route test was performed.
- To test an alternative route, first provision an owner-approved isolated free KGM endpoint and validate trust, origin, TLS and IP behavior; never bypass access restrictions without authorization.

## Draft PR #163 inventory and extraction gates

GitHub PR #163 (`integration/kgm-multiconsumer-export-20260928`, HEAD at audit `8e79191eba704927df0ff8b069c2d19095b8f378`) changes **189 files**: 62 code modules, 61 test modules, 65 docs files, and ROADMAP.md. Current PR remains draft/unmerged. This combination couples separate research, export and operational tracks; do not merge wholesale into canonical main.

Recommended independently reviewable sequence, each from the then-current canonical main, with explicit dependency pinning and fresh exact-head CI plus ARM64 test execution:

1. **S0 contracts, pure invariants:** exchange_contract, research_request, typed result, verification boundaries, source policy; small synthetic/negative tests; ensure no transport, scheduler, migrations or runtime side effects.
2. **S1 bounded collection and per-source parsers:** source adapters, cooldown, source modules, AU/GCC profiles and targeted source tests; maintain all new sources disabled and source/date metadata explicit. This slice may depend on S0.
3. **S2 event mapping and source independence:** event identity, origin assessment, generic mapping, explicit mapping profiles, corroboration, negative same-origin/disagreement tests. No automatic VERIFIED.
4. **S3 durable research operation:** storage, spool, worker, cursor, lifecycle, expiry, archive, crash-recovery tests. Keep unattended execution OFF and avoid production migrations.
5. **S4 optional multi-consumer export:** exchange ledger, artifact generation/replay/retention, side-effect isolation; keep downstream Sentinel/K-Trader disabled and require separate cross-project owner review.
6. **S5 docs and strategic state:** reconcile docs/handoff/state/ROADMAP after each accepted slice; never overwrite P23.4 gate or promote parser health to factual verification.

Before creating code slices, resolve exact module import dependencies with AST/static graph and confirm base main compatibility. Avoid cherry-picking all PR163 commits into any single slice. Author a clean selective extraction, test on isolated checkout; publish and merge only after acceptance evidence is complete.

## Current gate

P24.1 IN_PROGRESS; GCC and AU accepted as live-parser research only. ASEAN, OAS, GDELT blocked. No new source admission; no production, public Plugin, scheduler, paid/shared infrastructure, or downstream integration.
