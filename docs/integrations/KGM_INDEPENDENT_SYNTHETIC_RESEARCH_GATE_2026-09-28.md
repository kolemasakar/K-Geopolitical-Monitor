# KGM-only synthetic research exchange — independent checkpoint

Date: 2026-09-28. Owner direction: finish all possible KGM work independently; **do not contact or depend on K-Trader** until its separate implementation is ready. PR #163 remains draft.

## Implemented
- Strict bounded `kgm.research.request.v1` validation and dual historical publication/availability cutoff.
- In-memory synthetic request lifecycle and correlated minimal `kgm.research.result.v1` fixture (NOT real research).
- `research_spool_v1.py`: dedicated offline POSIX directory; validated allowlisted consumer/policy submission; fsynced atomic request publication; digest-based idempotency; one fixture-only correlated result per request; per-consumer result directory; fsynced atomic result publication; digest/correlation/policy checks at retrieval. Lock serializes cooperative submission/fixture processing. No network, live provider or canonical KGM read.
- Negative synthetic cases: conflicting retry, unauthorized consumer, cross-consumer retrieval, historical lookahead, revoked processing/retrieval, partial empty coverage, stored request tampering, result tampering and corrupt replay.
- Earlier generation artifact, ledger, replay and non-destructive retention modules remain *separate candidate utilities*, not connected to the request spool.

## Measured evidence
Isolated clone on authorized KGM host `kgm-e4-owner-pilot`; exact code SHA `a8aceacc55fe0fdb5f164e18b391f1d3b77117f3`. Eleven explicit synthetic test modules (exchange and research): **79 passed in 0.72s; exit 0**. Research subset: **26 passed in 0.23s**. No production service/DB/configuration touched.

## Unresolved gates — do not misrepresent as deployed
This is a KGM-local *fixture*, not an approved real research service or cross-host E2E. Its allowlist is caller-provided, not authenticated transport identity; directory creation alone does not prove filesystem ACLs or prevent malicious local actors. Current spool does not durably persist every lifecycle transition, enforce quotas, reject all hostile filesystem layouts, integrate approved immutable generation publisher, or include complete canonical evidence/provenance/contradiction/forecast semantics. SHA-256 integrity does not authenticate the sender. No real historical corpus/source-health measurement or real data release approval.

Next independent KGM tasks: versioned canonical typed response and semantic fixture validation; hardened persistent lifecycle, quota and retry/expiry; dedicated restricted inbox/outbox layout and negative local permission tests; snapshot/coverage/no-lookahead fixture matrix; standalone sender/receiver test bundle for later Sentinel/K-Trader acceptance. Do not call K-Trader or attempt live exchange until owner schedules the joint gate. Plugin PR #161 remains paused. Phase 23 remains unchanged.
