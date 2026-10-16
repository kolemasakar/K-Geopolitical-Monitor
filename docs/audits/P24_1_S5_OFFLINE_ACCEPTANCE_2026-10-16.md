# P24.1 S5 final offline readiness evidence — 2026-10-16

**Status: S5_IMPLEMENTED_WITH_PARTIAL_EVIDENCE / FINAL_MAIN_ARM64_ATTESTATION_OPEN / PRODUCTION_GATE_OPEN.**

## Verified owner decision and foundations
- S5 research-only decision PR #215 merged after CI PASS.
- Canonical S5 scope sync PR #216 merged after CI PASS.
- Read-only S5.4 runtime drift audit PR #220 merged after CI PASS; production checkout `b31b2136b5fe982d0b63b0135479b1549041906c`, active `kgm-monitor.service`, ARM64. No service change or code deploy.
- S5.1 process SIGKILL tests PR #217: CI PASS, 2 targeted tests PASS, independent native ARM64 **1597/1597 PASS** (970.86s). MERGED canonical SHA `9cd9a34e2e15da29c1398e567e80f7a93027035e`.
- S5.2 read-only ledger compatibility PR #218: CI PASS, 4 targeted tests PASS, independent native ARM64 **1599/1599 PASS** (982.28s). MERGED canonical SHA `8603ce4e9a975800dcbdf7e87bacfb5cd124a052`.
- S5.3 explicit deny-by-default no-send consumer contract PR #219: MERGED, GitHub CI SUCCESS, 12 targeted tests PASS. Independent original exact-head full-suite acceptance must be assessed separately; current S5 integration retested on PR #223 with 20/20 focused ARM64 PASS.
- S5.1b old draft PR #221 CLOSED WITHOUT MERGE because its base predates S5.1–S5.3. Replacement PR #223 rebased on full accepted S5 main: 20/20 focused ARM64 PASS, exact-head GitHub CI SUCCESS and PR #223 MERGED into main `9c10d4d2dec331f82db3e4a346bcaef6372df3b3`. Exact-head full ARM64 result for #223 and merged-main regression remain to be independently attested.

## Security boundaries and remaining proof
1. SIGKILL around `os.replace` demonstrates local file consistency and replay under tested stop points, **not** power-loss durability or exactly-once remote side effects.
2. Ledger v1/v2 compatibility is **read-only**. No live data migration, rollback execution, or permission for format cutover.
3. Consumer grants are **trusted injected test configuration**, not an externally authenticated identity. The NO_SEND policy cannot enroll a live K-Sentinel or K-Trader client.
4. `DISPUTED` material is forbidden for non-research scope by the S5.3 negative test; factual verification remains a separate KGM gate.
5. Symlink and hardlink tests address a concrete ledger read aliasing gap; full filesystem TOCTOU, interrupted directory-fsync and hostile multiprocess paths need separate review.
6. Deployment drift remains confirmed, and new research modules have not been deployed into the active unattended runtime.

## Exit criteria before final owner production decision
- PR #223 MERGED with exact-head CI SUCCESS and ARM64 full 1615/1615 PASS (591.47s). The subsequent integrated research-only S5 checkout containing all accepted code was independently rerun: **1615/1615 PASS** (466.86s, exit code 0), before documentation-only edits.
- S5 offline integration gate **PASS_WITH_KNOWN_LIMITATIONS** based on independent full ARM64 regression after S5.1b merge. Final documentation CI and state/handoff synchronization must still verify the documentation HEAD; code was not deployed to the operational runtime.
- Keep `FREE_ONLY / NO_SEND / PRODUCTION_NOT_APPROVED` until explicitly authorized after runtime/source/consumer security assessment.

**Gate:** `P24_1_S5_OFFLINE_PASS_WITH_KNOWN_LIMITATIONS_PRODUCTION_OPEN`.
