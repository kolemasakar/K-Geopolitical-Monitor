# KGM export retention checkpoint

Date: 2026-09-28. Issue #162, draft PR #163, Sentinel PR #26, K-Trader PR #87.

On authorized KGM host kgm-e4-owner-pilot, isolated clone at exact code SHA `c64f4497c4817b00fa50fa1cec52df968d613bef` ran eight synthetic test modules: **53 passed in 0.51 seconds, exit 0**. No production DB, running process, network or permissions modified.

New `exchange_retention_v1.py` is a **non-destructive planner**, not a retention daemon. It evaluates a configured age window and every explicitly registered consumer's acknowledged cursor, blocks history expiry for lagging consumers, requires a separately approved snapshot, and never authorizes actual deletion. Synthetic tests cover a lagging consumer, approved snapshot still not authorizing deletion, missing consumer registry, cursor ahead of producer, sequence gaps and an empty expiry set.

Important: current producer ledger does not persist UTC publication timestamps or an approved consumer registry. The planner's synthetic timestamps must not be mistaken for a live retention capability. To connect the planner, add verified ledger timestamps, signed-off consumer registry and immutable snapshot/recovery contract; explicitly handle CURSOR_EXPIRED before deleting any generation. No live retention schedule is authorized.

Next Sentinel gate: restricted dedicated read-only consumer identity, proved private KGM-to-Trader connectivity, pinned SSH host key, staging-only synthetic transfer and denied direct DB/raw evidence access. KGM cannot claim these checks from the existence of a Tailscale node. Owner release policy, measured canonical source/analysis/forecast outputs and real sanitized sample remain pending. Private Plugin PR #161 stays paused.
