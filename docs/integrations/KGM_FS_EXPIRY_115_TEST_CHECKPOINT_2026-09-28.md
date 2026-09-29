# Independent KGM-only filesystem and expiry validation — 2026-09-28

Exact tested code SHA: `f1e7067b021106a8bac762bd97d6ebf72e7f9878`. Authorized isolated host `kgm-e4-owner-pilot`, isolated checkout `/tmp/kgm-pr163-validation-AWDJxqb2/repo`; 19 explicitly selected exchange/research test modules, **115 passed in 1.28s, exit 0**. No production modification, live source calls, K-Trader access or cross-host test.

Implemented and verified:
- Disposable-directory negative filesystem tests: symlinked root and request alias rejection, corrupted stored request rejection, corrupted published result reconciliation rejection.
- `research_expiry_v1.py`: explicit deadline-based expiry of synthetic pending states, idempotent EXPIRED replay, policy authorization and monotonic timestamp checks. If any result artifact already exists, expiry fails closed and requires artifact reconciliation first. No background scheduling.
- Existing `research_completion_v1.py` crash reconciliation remains tested.

**Remaining gates:** OS-level ACL verification and adversarial concurrent filesystem race tests; unified typed durable admission/worker API (legacy minimal fixture path remains); fully automated bounded recovery/expiry worker; real historical source coverage and owner-approved real data policy; authenticated private cross-host transport. The synthetic test suite is not a production security certification. Keep PR #163 draft; Plugin PR #161 paused; do not contact K-Trader.
