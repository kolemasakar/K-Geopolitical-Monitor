# KGM durable cursor failure-injection checkpoint

Date: 2026-09-29. Exact tested code SHA `e013925f15da84a73b0aede07620b1aa2291520c`, authorized isolated host `kgm-e4-owner-pilot`. New three tests passed in 0.12s. Selected **26 exchange/research modules: 137 passed in 1.98s**.

New tests: synthetic cursor write failure leaves previous durable cursor unchanged; stale cursor rotates correctly when the pending queue changes; malformed stored cursor is rejected without overwriting it. Prior tests cover persistent wraparound and empty queue. These are deterministic fixture tests, not exhaustive filesystem crash/power-loss certification.

Open limitations: recovery still reads full inbox O(total items); max_items bounds processed entries only. The cursor and pending request snapshot are not a single transactional database; idempotent replay remains necessary. Older minimal fixture entry points remain for compatibility and must not be used for production exchange. Owner-only, offline synthetic; no live providers, production, HP-OMEN or K-Trader activity.

Next: explicit legacy entry-point inventory and migration/deprecation gates, then evaluate bounded indexed recovery without compromising integrity.
