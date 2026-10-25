# KGM O1 — Owner-approved request-driven operating model (2026-10-25)

Decision source: explicit owner direction on 2026-10-25. **KGM does not perform continuous monitoring.** Collection and analysis are initiated by the user's request. Both persistent watch records remain disabled by design.

## 1. Runtime configuration audit

The owner's live read-only O1 watch scan at 2026-10-25T20:30:21Z: two stored watches, zero enabled, zero due and zero RUNNING-blocked. This is **EXPECTED_CONFIG**, not a failed watch scheduler.

At deployed disk release `b31b2136b5fe982d0b63b0135479b1549041906c`, `unattended_runner.build_unattended_service` configures a 60-second poll and adapters `ConsiliumRssAdapter` and `GdeltDoc2Adapter`. `due_watches()` checks only enabled watches; none currently qualify. Historical source-collection records with OTHER names do not attest current GDACS/GDELT support. The image of actual loaded process code remains UNKNOWN, so disk source is not proof of in-memory source selection.

The fresh singleton supervisor tick is a technical heartbeat, not a research request. Its per-tick execution counters are zero. Last successful timestamp is historical (Sep 1) and does **not** imply a freshness breach for a request-driven system without a pending request.

## 2. Target architecture and ROADMAP reconciliation

- **ON_DEMAND_ONLY**: Accept explicit user research topic, time window and source requirements. No recurring job is created.
- Verify applicable protocol and gates for source quality, provenance, disagreement and completeness on each request.
- Execute a bounded, one-time acquisition and analysis; no background watch enrollment and no unsolicited notifications.
- Report data cut-off timestamps, origin/source evidence, confidence and unknowns. Never claim current-source coverage or execution if only offline fixtures were used.
- The permanent supervisor may still be active for legacy reasons; removing or changing it requires a separate authorized operation. No scope change today.
- P24/S5 offline test acceptance is independent of operational readiness for a real user-requested query. **Production NO_GO for new live activation**, pending an explicitly reviewed path.

## 3. Bounded isolated one-shot validation protocol (NOT EXECUTED IN PRODUCTION)

**Input**: synthetic user request, fixed source adapter test doubles, fixed UTC clock, disposable SQLite and temporary project root; no network in offline test.

**Checks**:
1. Exactly one explicit request yields one execution; no request yields none.
2. Zero persisted enabled watches created as side effects; no mutation of the two live disabled watches.
3. Source success, failure, unavailable source and disagreement reflected in transparent PARTIAL/COMPLETE semantics; preserve evidence and deduplication.
4. Constrain network/CPU/time and aggregate output; NO_SEND means no Telegram/public/consumer dispatch.
5. Source timestamps, independent attribution and fail-closed exception behavior are examined.
6. Before/after disposable DB state shows expected controlled test mutations only, and no production path is used.

An existing `LiveOperationalCycle.execute_due` is watch-cadence-driven and **must not be invoked against live SQLite to simulate a user request**. A supported one-shot request entrypoint has not been independently established by this checkpoint. Do not repurpose production `--once` (one supervisor tick, not necessarily a research request) as proof of request handling.

## 4. Production gate

After validated isolated implementation and a separate owner decision, demonstrate **one actual user-invoked, bounded research request** through an already authorized on-demand route. Verify source retrieval, time cut-off, provenance, transformation/analysis, final response and lack of unsolicited side effects. If no such route exists, record `ON_DEMAND_ROUTE_NOT_ATTESTED` and design it offline first.

**No continuous polling obligation, scheduled watch activation, restart, migration, cleanup, database dump or broad permission grant follows from this plan.**

Acceptance: `SCHEDULER_CONFIG_EXPECTED`, `ON_DEMAND_EXECUTION_PENDING`, `PRODUCTION_NO_GO`. Policy: FREE_ONLY / NO_SEND / CLEANUP_HOLD.
