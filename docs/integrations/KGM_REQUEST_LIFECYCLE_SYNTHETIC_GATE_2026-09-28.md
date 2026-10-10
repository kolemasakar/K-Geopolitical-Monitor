# KGM request-driven research: isolated lifecycle checkpoint

Date: 2026-09-28. Owner correction: https://github.com/kolemasakar/K-Geopolitical-Monitor/pull/163#issuecomment-5871136756. Sentinel contract: `KGM_KTRADER_REQUEST_DRIVEN_RESEARCH_V0_1.md`.

Exact code SHA `7465159dcbb536aa4cef1e64bd815a6ebf41353e` tested on authorized KGM host in isolated clone: `tests/test_research_request_v1.py tests/test_research_lifecycle_v1.py` **15 passed in 0.10s; exit 0**. No production code deployed or real provider work performed.

Implemented candidate `research_request_v1.py`: bounded versioned current/historical request validation and dual publication/availability cutoff. Implemented `research_lifecycle_v1.py`: **in-memory synthetic-only** deterministic lifecycle and request digest idempotency, correlated result fixture with COMPLETE vs PARTIAL and separate source health. This response fixture intentionally has only minimal summary fields and is NOT the approved canonical typed result, evidence/provenance/contradiction or forecast representation. No claim that it conducts real research.

Priority before synthetic private E2E: durable idempotent request inbox with consumer authorization/quotas, immutable per-consumer result outbox, fully typed response preserving canonical KGM semantic verification, evidence provenance, corrections, forecasts and source health; approved release policy and measured historical corpus coverage. Sentinel must validate authenticated restricted bidirectional Tailscale transfer and deny cross-consumer/raw data access. K-Trader independently owns impact mapping and must treat PARTIAL/UNKNOWN as non-authoritative with no trading side effects.

Prior push-first exporter/ledger/retention remain secondary response delivery candidates. No live source calls, trading-risk linkage, production activation or Plugin PR #161 change.
