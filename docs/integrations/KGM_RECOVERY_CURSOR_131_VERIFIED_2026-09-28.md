# KGM recovery cursor checkpoint — 2026-09-28

Exact tested code SHA `c2ae0a672cd5eae19e115838fca5cec7e0aaf51d`. Authorized isolated host `kgm-e4-owner-pilot`, detached checkout `/tmp/kgm-pr163-validation-AWDJxqb2/repo`. **131/131 passed in 1.71s across 24 selected modules**, process exit 0. New cursor tests independently **2 passed in 0.10s**.

Added optional `after_key` to offline `recovery_pass` and canonical typed workflow; reports `next_cursor`, rotates deterministic pending snapshot with wraparound, rejects invalid cursor shape. Tests confirm a stalled first request does not indefinitely block later keys when caller supplies returned cursor.

**Limits:** Cursor is caller-managed, not yet durable; absent cursor repeats old fixed-first behavior. Every pass still scans the full inbox, so `max_items` bounds processed items but not scan cost. Not a daemon, not authenticated cross-host transport, no real corpus or provider. Legacy synthetic APIs are not yet isolated. No production or K-Trader operations.

Next: persist cursor with crash-safe owner-only storage, add stale-cursor/mixed-consumer and failure-injection tests, and document legacy entry-point deprecation.
