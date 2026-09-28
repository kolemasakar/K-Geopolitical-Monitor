# KGM exchange: release policy and replay acceptance gate

Date: 2026-09-28. Scope: issue #162, draft PR #163, Sentinel PR #26 and K-Trader PR #87.
Status: OFFLINE PROTOTYPE VALIDATED; REAL DATA RELEASE NOT APPROVED; TRANSPORT NOT DEPLOYED.

## Verified synthetic test evidence
On authorized KGM host kgm-e4-owner-pilot, disposable clone at exact code SHA `76e13f4501abe8f14d449742d9901a6f2d3b4a4c`, `PYTHONPATH=src /opt/k-geopolitical-monitor/.venv/bin/pytest -q -o filterwarnings= tests/test_exchange_contract_v1.py tests/test_exchange_artifact_v1.py tests/test_exchange_generation_v1.py tests/test_exchange_replay_v1.py`: **36 passed in 0.25 seconds, exit 0**. Production tree, credentials, DB, running service and strategic state were not changed.

## Offline implementation
- `exchange_generation_v1.py` is a **separate candidate**, not yet a replacement for `exchange_artifact_v1.py`. It writes files and completion marker into a temporary generation on one POSIX filesystem, fsyncs files and generation directory, renames the complete directory, then fsyncs parent. Reader requires exact three files, valid marker, approved v1 schema and matching digest/manifest. Incomplete temporary generations remain invisible to the reader; tests exercise absent marker, corruption, duplicate and unfinished staging.
- Current generation writer assumes **one trusted writer**. No cross-process writer lease, production crash/power-loss injection or full hostile-filesystem TOCTOU hardening is claimed. Old two-file writer must be retired or explicitly gated before production.
- `exchange_replay_v1.py` provides **pure bounded selection** from a caller-supplied contiguous producer ledger, with explicit `CURSOR_EXPIRED`, gap/reorder/duplicate rejection and 100-record maximum. It is not a persisted producer ledger, retention daemon or network receiver. Consumer acknowledgment storage remains the consumer's responsibility.

## Proposed fail-closed release policy (not owner-approved)
All real record classes default to WITHHELD until KGM owner approves the canonical read model, positive field allowlist, licensing and redaction for each class and each consumer. A valid schema does **not** grant permission to export. VERIFIED, DISPUTED, corrections/retractions, forecasts and source health require separate decisions. Preserve canonical P13.5 multidimensional confidence and contradiction states, publisher vs underlying origin and unmeasured source health. Never coerce forecast probabilities into factual confidence or emit trade instructions. Private DB IDs, filesystem paths, credentials and unlicensed full text must not cross the boundary. An approval record must identify policy version, allowed classes, allowed fields, recipients and evidence restrictions.

## Replay contract for Sentinel/K-Trader review
KGM must persist a monotonic stream sequence, immutable batch ID/digest, minimum retained sequence, generation time and approved policy version. A consumer requests batches strictly after its own last acknowledged sequence; any gap or expired cursor fails closed. Correction is a new record/version, never an overwrite. A fresh snapshot after expiry requires explicit approval; do not silently advance the cursor. Empty replay result is not proof of healthy feed or complete sources. As-of decisions must use both producer ingestion and consumer receipt timestamps.

## Remaining gates
- KGM owner release-policy decision and dedicated exporter identity without expanding `kgmops` DB access.
- Measured canonical source, semantic-analysis and forecast outputs via authorized KGM-owned observability.
- Persisted producer ledger, multi-process single-writer lock, recovery policy, genuine interrupted/power-loss test and receiver fixtures.
- Sentinel private Tailscale + restricted per-consumer identity and verified host key; actual reachability not assumed from node address.
- K-Trader isolated receiver and synthetic E2E with no live trading impact.
- PR #161 private Plugin remains paused; strategic Phase 23 remains unchanged.
