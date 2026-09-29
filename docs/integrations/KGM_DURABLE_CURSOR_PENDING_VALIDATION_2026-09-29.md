# KGM durable recovery cursor — pending exact-SHA validation

Recorded 2026-09-29. PR #163 remains draft. Code commit: `46e296b11e4de0865ea1fdfb95929f70ca70b7ee`. Test commit and current checked PR head at recording: `71ad8ec8baf0250456d43bb5c84c53f7dc47bc48`.

Added `src/kgeopolitical_monitor/research_durable_cursor_v1.py`: owner-only, explicitly invoked synthetic recovery wrapper using a cooperative exclusive run lock and fsynced atomic on-disk cursor. A completed pass saves the returned cursor; a crash before cursor persistence can replay work, relying on the existing idempotent completion/expiry paths. Invalid stored cursor structure and symlink cursor paths fail closed. Three new tests cover persistence and wraparound, invalid cursor, and empty queue.

**Verification pending.** Fetch of the test commit to the authorized isolated KGM host succeeded in the previous session. Subsequent remote checkout and HEAD inspection were blocked by the tool security layer. Do not claim that the new tests passed. Last independently verified exact code SHA: `c2ae0a672cd5eae19e115838fca5cec7e0aaf51d`, with **131/131 selected tests passed in 1.71s**, exit code 0.

Next validation: use only the authorized isolated KGM checkout `/tmp/kgm-pr163-validation-AWDJxqb2/repo` on `kgm-e4-owner-pilot`; checkout exact SHA `71ad8ec8baf0250456d43bb5c84c53f7dc47bc48`, run the three new cursor tests and the full selected exchange/research regression modules, then record exact results. Do not touch production, HP-OMEN, K-Trader, live providers or unrelated project resources.

Limits: durable cursor does not bound full O(total inbox) snapshot scanning; max_items only bounds processed items. No unattended daemon, cross-host transport, authenticated external consumer or real corpus validation. Legacy synthetic entry points remain.
