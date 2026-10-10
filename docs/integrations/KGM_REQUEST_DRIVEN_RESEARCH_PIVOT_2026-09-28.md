# KGM request-driven research — authoritative owner correction

Date: 2026-09-28. Source: owner comment https://github.com/kolemasakar/K-Geopolitical-Monitor/pull/163#issuecomment-5871136756; Sentinel contract `docs/integrations/KGM_KTRADER_REQUEST_DRIVEN_RESEARCH_V0_1.md` at commit `46683870a4c262366672fc70dcc7bed69cd9f76f`.

**Architecture correction:** KGM is an **on-demand current and historical research provider**, not a push-first feed of all events. K-Trader submits scoped requests; KGM selects, evaluates and returns request-correlated significant results; K-Trader alone owns any trading-impact interpretation. Sentinel secures identity/connectivity and coordinates acceptance, not research. Old immutable artifacts, ledger/replay and retention are potential request-correlated delivery utilities, not a justification for an always-on news feed. Prior push-first integration documents are superseded where inconsistent.

## Implemented offline starting point
`research_request_v1.py` enforces candidate `kgm.research.request.v1` fields, bounded time span/symbols/results/topic filters, strict CURRENT vs HISTORICAL_AS_OF mode, UTC timestamps and separate historical publication/availability cutoff via `historically_available`. It does **not** authorize consumer identity/scope, make provider calls, process a request queue or validate the full eventual response. Exact code SHA `f26b938faace47b1948734ac8c9bb7681499d0ab` checked in isolated KGM host clone: **8 synthetic tests passed in 0.05s, exit 0**.

## Next primary KGM work
1. Explicit KGM owner per-consumer request policy and allowlisted instruments/topics/time spans; fail closed on unknown policy, origin or missing historical corpus.
2. Idempotent async lifecycle RECEIVED -> ACCEPTED -> PROCESSING -> COMPLETE/PARTIAL/FAILED/EXPIRED, bounded quotas, no duplicate provider execution.
3. Versioned `kgm.research.result.v1` with request/result correlation, typed claims/contradictions/revisions/forecasts, evidence provenance, factual multidimensional confidence, coverage and source health; historical no-lookahead against BOTH publication and actual availability/ingestion.
4. Distinct per-consumer restricted inbox/outbox; publish complete immutable correlated results only after approved projection/release policy. Sentinel validates private bidirectional transport and negative permissions before deployment.
5. Isolated synthetic request -> selected research fixture -> correlated result acceptance; K-Trader handles PARTIAL/FAILED/UNKNOWN with no live trading side effects.

**No live provider calls or production activation authorized by this design work.** KGM runtime source availability still unmeasured through approved owner read path. Private Plugin PR #161 stays paused and strategic Phase 23 remains unchanged.
