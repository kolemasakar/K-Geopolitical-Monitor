# KGM durable recovery cursor — exact-SHA verification

Verified 2026-09-29 on authorized isolated KGM host `kgm-e4-owner-pilot`, checkout `/tmp/kgm-pr163-validation-AWDJxqb2/repo`.

**Exact tested code SHA:** `71ad8ec8baf0250456d43bb5c84c53f7dc47bc48`.
- New durable cursor module tests: **3 passed in 0.12s**.
- Selected 25 exchange/research regression modules: **134 passed in 1.89s**.
- Remote command returned successful pytest output. No production changes.

Durable cursor uses a cooperative exclusive run lock, validates its stored structure, and writes the next key atomically with fsync. Verified fixture tests cover persisted rotation and wraparound, invalid stored cursor rejection and empty inbox. Recovery replay relies on previously tested idempotent completion and expiry paths; this checkpoint does not prove all possible power-loss or filesystem failure scenarios.

**Remaining gates:** full inbox snapshot still O(total inbox); max_items only bounds processing. Add injected write-failure and mixed-consumer stale-cursor tests; isolate legacy fixture APIs; no unattended scheduler or live corpus. Owner-only model remains; malicious local human-user testing is out of scope. No HP-OMEN, K-Trader, providers or production activation.

Supersedes `KGM_DURABLE_CURSOR_PENDING_VALIDATION_2026-09-29.md` (historical pending record retained for audit).
