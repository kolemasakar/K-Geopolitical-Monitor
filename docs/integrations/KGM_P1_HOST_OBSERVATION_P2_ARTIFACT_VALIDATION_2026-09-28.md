# P1 measured host audit and isolated P2 artifact prototype — 2026-09-28

Related: #162, draft PR #163; Sentinel-Remote PR #26; K-Trader PR #87.
Status: HOST_PROCESS_OBSERVED; SOURCE_AND_ANALYSIS_OUTPUTS_NOT_MEASURED; OFFLINE_SYNTHETIC_PROTOTYPE_TESTED.

## Host observations (authorized RDC on kgm-e4-owner-pilot)
- UTC observation: 2026-09-28 13:18.
- `kgm-monitor.service`: active/running, main PID 133634, service start 2026-09-25 06:47:37 UTC, NRestarts=0 as reported by systemd.
- Running command: `/opt/k-geopolitical-monitor/.venv/bin/python -m kgeopolitical_monitor.unattended_runner --project-root /opt/k-geopolitical-monitor --poll-seconds 60`.
- Deployment tree root-owned; `/opt/k-geopolitical-monitor/data` permission 0750, owner/group `kgm:kgm`; `kgmops` not in group `kgm` (uid/gid 1002). No production database access attempted, no owner permissions changed.
- No KGM Docker container shown by name. KGM process/service evidence does not establish successful source collection, semantic analysis, forecast production, completeness, freshness or uninterrupted service history. Journal excerpt for the sampled period yielded no output under `kgmops`; this is not evidence of zero errors.
- Live P1 result: RUNNER_RUNNING / SOURCE_COLLECTION_NOT_MEASURED / ANALYSIS_NOT_MEASURED / FORECAST_NOT_MEASURED / EXPORT_NOT_OPERATIONAL.
- Production deployed SHA not independently verified: Git rejects repository read under `kgmops` due to owner mismatch; do not change global safe.directory as an audit shortcut.

## Isolated offline artifact prototype
- Added `exchange_artifact_v1.py` as an opt-in pure artifact writer over already-approved synthetic projections; **no** database reader, production scheduler, listener, consumer authentication or deployed transport.
- Writes a bounded canonical JSON batch and sidecar SHA-256 manifest into an existing dedicated directory with exclusive name reservations and atomic rename. SHA-256 is **integrity only**, not origin authentication or a signature.
- Strict allowlisted v1 contract remains fail-closed. The writer is not yet a hardened hostile-filesystem or crash-recovery implementation; an unexpected crash between file renames may leave an incomplete pair. Consumer must reject absent/mismatched manifest. Production readiness requires ownership/permission review, explicit crash recovery and signed/authenticated transport.
- Independent synthetic tests cover valid batch, disputed claim, unknown heartbeat, duplicate rejection, invalid payload, absent/symlink directory and integrity digest. No real intelligence records or other project secrets used.
- Exact SHA test run: `515aa4b993e6b6b15b4b7f27d6e29c15e5e91805`, isolated checkout under `/tmp/kgm-pr163-validation-AWDJxqb2/repo`, using existing KGM host venv; `PYTHONPATH=<isolated_repo>/src pytest -q -o filterwarnings= tests/test_exchange_contract_v1.py tests/test_exchange_artifact_v1.py` -> **21 passed in 0.17s, exit 0**.
- No production checkout, service, DB, credentials, source schedule or K-Trader strategy changed.

## Gates still required
1. KGM owner approval for separate exporter read identity, allowlisted release policy for disputed/corrected/forecast classes and dedicated artifact path.
2. Authorized read-only observability of actual collection/analysis/forecast metrics through approved administrative path (no `kgmops` direct DB permission).
3. Sentinel contract review: independent consumer identity, private transport, per-consumer replay/retention, audit, authentication, integrity, resilience.
4. K-Trader review: no automatic factual confidence coercion, preserve epistemic state, independent exposure/impact mapping, no trading integration without separate gate.
5. Crash-recovery, malformed nested values, privacy and backward compatibility hardening before merging. Private Plugin PR #161 remains paused.
