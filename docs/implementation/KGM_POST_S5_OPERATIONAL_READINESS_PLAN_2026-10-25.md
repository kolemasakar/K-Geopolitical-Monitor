# KGM — operational readiness follow-up plan (post S5)
Date: 2026-10-25
Status: **PROPOSED RESEARCH PLAN / OWNER PRODUCTION DECISION REQUIRED**
Baseline: GitHub main `d492501c08d4d21d9894da9e1eed686d916cc22f`.
Evidence: `docs/audits/KGM_S5_READONLY_OPERATIONAL_AUDIT_2026-10-25.md`.

## O1 — Runtime proof (P0)
Read-only establish service loaded-code parity (not inferred from disk HEAD), writer/process inventory, scoped logs and cycle completion with timestamped failures; inventory persistent forward-state without exposing secrets or writing data.
**Gate:** timestamped, reproducible proof of observed runtime, or UNKNOWN/BLOCKED retained.

## O2 — Isolated durability (P1)
Use disposable local fixtures and independent processes; simulate crash windows before/after replace and fsync; probe corruption, replay, lease races, ACL/path containment; record limitations of synthetic power-loss tests.
**Gate:** exact-head native ARM64 + CI PASS, all unaffected production directories.

## O3 — Ledger migration and release boundary (P1)
Finish synthetic v1/v2 recovery/rollback validation, verify checksum preservation and idempotency; review #241 isolated-release ownership/lease invariants; no live migration, no release switch.
**Gate:** independent evidence, rollback design, no production operation.

## O4 — Source and consumer boundary (P1)
Offline negative contract suite for KGM → K-Sentinel → K-Trader (NO_SEND enforced); read-only real-source reachability/freshness sampling only with separate authorization; verify independent original sources and COMPLETE/PARTIAL semantics, not just parser success.
**Gate:** source provenance explicit; no external send.

## O5 — Docs/PR reconciliation and owner decision (P1)
Classify #215 historical, #249 merged, #250 state-only pending CI, #241 release gate separate. Synchronize ROADMAP/state/handoff preserving dual Phase 23 operational vs Phase 24 research pointer.
**Gate:** reviewed CI/ARM64 proof, no stale merge, separate owner **PRODUCTION_GO/NO_GO** decision.

## Preservation
FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO. Never restart, redeploy, restore, migrate, clean up, enroll consumer, send or resume writer as an implicit consequence of research acceptance.
