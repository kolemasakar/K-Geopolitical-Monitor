# KGM S5 read-only operational audit — 2026-10-25

Status: **RESEARCH_OFFLINE_PASS_WITH_KNOWN_LIMITATIONS / OPERATIONAL_EVIDENCE_INCOMPLETE / PRODUCTION_NO_GO**.

## Provenance
- Canonical GitHub main at inspection: `d492501c08d4d21d9894da9e1eed686d916cc22f` (merged PR #249).
- S5 accepted evidence: `docs/audits/P24_S5_OFFLINE_ACCEPTANCE_ADDENDUM_2026-10-25.md`; historic entry snapshot is not current qualification.
- Inspection mode: owner-authorized read-only Remote Desktop Commander commands on `kgm-e4-owner-pilot`; no service restart, deployment, migration, artifact cleanup, live write, network send, or experiment on production.

## Runtime observations
| Observation | Result |
|---|---|
| Host / architecture | kgm-e4-owner-pilot / aarch64 |
| Service | kgm-monitor.service active/running |
| User/group | kgm/kgm |
| Main PID | 125277 |
| Started | 2026-10-24 06:39:45 UTC |
| NRestarts / Result | 0 / success |
| Restart | on-failure |
| ProtectSystem / NoNewPrivileges | strict / yes |
| ReadWritePaths | /opt/k-geopolitical-monitor/data |
| Disk | 45G total, 11G used, 34G available |
| Memory | 5.8Gi total, 5.0Gi available |
| Working tree HEAD | b31b2136b5fe982d0b63b0135479b1549041906c |
| Working tree untracked | src/k_geopolitical_monitor.egg-info/ |
| Loaded-code attestation | UNKNOWN |

The Git checkout is not canonical S5 main and runtime loaded-code parity is **not verified**. A healthy systemd state does not establish successful ingest, freshness, source independence, correctness or forward-state integrity. The current user could not inspect authoritative unit journal data; lack of visible warning/error lines must not be treated as zero errors. No automated HTTP/source probes were run.

## S5.1 crash/failpoint coverage (previous accepted synthetic evidence)
- PR #243: separate-process lease holder, SIGKILL, successor recovery; exact-head ARM64 1709 PASS.
- PR #247: hard-exit after atomic replacement before directory fsync; synthetic failure; exact-head ARM64 1711 PASS.
- Tests qualify **isolated local replay/recovery only**, not physical power-loss durability, remote exactly-once delivery or live database migration.
- **Open:** power-loss/fsync durability proof under an isolated disposable filesystem/VM; fault matrix across write/rename/sync stages; documented guarantees for rollback/replay. Never inject faults into the running service.

## PR reconciliation
- #215: historical S5 proposal. Do not merge stale decision over accepted S5.
- #241: separate P24.4 isolated release/root gate; remains independent of S5 and production approval.
- #249: merged final offline evidence addendum.
- #250: state-only reconciliation draft; CI and branch comparison required before merging. Avoid duplicating/conflicting state edits.

## Decision and next gate
**S5_OPERATIONAL_READINESS_EVIDENCE_GATE = OPEN / PRODUCTION_NO_GO**.
Mandatory checks: (1) loaded-code/provenance attestation and forward-state invariants; (2) privileged yet bounded journal and completed cycle evidence; (3) source health/freshness/provenance sampling; (4) isolated fsync/power-loss model and migration rollback rehearsal; (5) PR #241 boundary test and exact-head CI+ARM64; (6) explicit separate owner go/no-go for any release, migration or consumer enrollment.

Policy: **FREE_ONLY / NO_SEND / CLEANUP_HOLD**. No consumer activation, delivery, transport, cleanup, release switch, backup/restore, writer resume or restart is approved.
