# KGM-only lifecycle and offline acceptance checkpoint

Date: 2026-09-28. Owner authorized continued independent KGM preparation; do not interact with K-Trader.

**Exact tested code SHA** `d085cc9622f9f20ca358a56ee106d95f98e3bdd8`. Isolated authorized KGM host checkout; 16 explicit exchange/research test modules; **101 passed in 1.00s, exit 0**. No production modifications, live provider calls or other-project interaction.

Implemented:
- `research_durable_lifecycle_v1.py`: fsynced local POSIX fixture request state transitions under a cooperative lock, validated idempotent admission, bounded pending count per consumer, monotonic transition timestamps, persisted attempt counter and read-only restart recovery snapshot. No automatic recovery execution, deadline scheduler or real source work.
- `research_offline_acceptance_v1.py`: standalone explicit synthetic fixture acceptance harness: durable request admission → accepted state → recovery snapshot → typed validated immutable correlated result → local retrieval/digest check. Returns explicit `cross_host_exchange_tested=false` and `real_corpus_tested=false`.
- Prior typed result, no-lookahead and conservative synthetic coverage checks remain independent modules.

Known engineering debt / non-claims:
1. Legacy minimal spool `submit/process_fixture` and new `admit/advance/publish_typed_fixture` coexist; typed publication does not yet atomically advance durable lifecycle to COMPLETE/PARTIAL. Do not imply unified transaction or crash-safe job completion.
2. Cooperative lock and SHA-256 are not authenticated transport, malicious-local-user isolation, per-consumer OS ACL verification or protection against every filesystem race. The quota only covers requests admitted through the new admission function.
3. No measured actual historical corpus/source freshness, approved real-data release policy, source selection/research engine or trading relevance assessment. No no-news guarantee.
4. Cross-project exchange, Sentinel private channel and K-Trader tests remain deferred by owner. No production activation or Plugin PR #161 change.

Next independent tasks: harden single API and atomic lifecycle/result consistency, deadline/expiry policy and bounded recovery, isolated filesystem negative tests, and a controlled read-only actual KGM corpus inventory **only when existing authorized permissions allow**. Never bypass production file permissions.
