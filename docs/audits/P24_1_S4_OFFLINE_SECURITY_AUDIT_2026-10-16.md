# P24.1 S4 offline exchange security audit — 2026-10-16

Status: **S4_PARTIAL_VALIDATED / S4F_ACCEPTANCE_PENDING / PRODUCTION_NO_SEND**.

## Verified accepted modules
- S4a exchange contract PR #199: GitHub CI SUCCESS, native ARM64 1549/1549 PASS.
- S4b immutable artifact PR #201: CI SUCCESS, ARM64 1554/1554 PASS.
- S4c generation PR #203: CI SUCCESS, ARM64 1574/1574 PASS.
- S4d replay selector PR #205: CI SUCCESS, ARM64 1577/1577 PASS.
- S4e ledger PR #208: CI SUCCESS, ARM64 1586/1586 PASS; failed earlier PR #206 was closed without merge.
- Canonical main at entry: `ce0067d42dbf2087701afd583c80d14ac70a5808` following handoff/state synchronization PR #209.
- S4f atomic ledger PR #210: **DRAFT** and not accepted until exact-head CI and full ARM64 regression.

## Security and correctness boundaries

1. Contract and replay tests validate synthetic local records and cursor-selection semantics; do not prove consumer authorization at a network boundary.
2. S4e original ledger is not automatically equivalent to S4f atomic replacement. Do not silently migrate live data, switch reader modules, or authorize delivery.
3. S4f writes a full ledger to a temporary file, fsyncs file, replaces target, fsyncs directory, and uses cooperative flock. Tests include idempotency, two batches, torn-file rejection, replace failure, and missing generation.
4. Remaining adversarial cases to qualify separately: symlink/hardlink/path-race controls for ledger reads and batch publication; multi-process concurrent append/replay under crash; fsync failure injection; invalid or untrusted cursor; ledger truncation/retention; malicious consumer policy or cross-tenant access.
5. Do not claim exactly-once external side effects, production crash safety, live source validation, or verified facts from fixture-only tests.
6. A network transport, remote delivery, K-Sentinel/K-Trader consumer enrollment, and any source activation require independent explicit owner gate.

## Follow-up sequence

- Accept PR #210 only if exact-head CI plus independent ARM64 full regression PASS.
- Add negative, multi-process and failpoint tests to the appropriate dedicated S4 module; assess need for a ledger-v1 to ledger-v2 migration contract without performing migration.
- Reconcile ROADMAP and state after actual acceptance, then stage S5 completion. Production and export remain OFF.

Infrastructure: FREE_ONLY KGM owner-pilot ARM64 and GitHub CI; no HP-OMEN, KRC or K-Trader shared infrastructure.
