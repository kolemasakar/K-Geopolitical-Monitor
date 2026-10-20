# P24.2-A hardened cleanup preflight — review handoff

**State: CLEANUP HOLD. Production deletion is NOT authorized.**

## Existing risk
The current `ops/p24_diag/kgm-p24-cleanup` uses unchecked `rm -f`, suppresses directory deletion errors and emits PASS without pre/post checks. It remains unchanged and MUST NOT be executed.

## Candidate
`ops/p24_diag/kgm-p24-cleanup-preflight.py` **contains no deletion logic**. It checks:
- Four fixed file paths and both candidate target directories, including their root-owned ancestor directories.
- No symlinks; exact directory membership; regular files, root owner, one hard link.
- Expected snapshot SHA-256 and size for both DBs; accepted report and manifest checksums; manifest backup identity.
- Any discrepancy aborts with `PREFLIGHT_FAIL`; successful preflight prints `PREFLIGHT_PASS` but still `cleanup=HOLD` and `deletion_performed=false`.

Reference evidence: `docs/evidence/P24_2_A_OWNER_ACCEPTANCE_2026-10-17.json`.

## Verification
A matching locally constructed draft was exercised on isolated temporary fixtures:
- good fixture, hash tamper, unexpected entry, symlink, hardlink, missing file and wrong owner: **7/7 unittest PASS**.
- The committed source itself still needs CI execution and independent code review; do not treat local draft results as CI acceptance.
- TOCTOU resistance, production symlink ancestors outside the fixed root, mutation-time error propagation and post-delete proof are NOT IMPLEMENTED. They are required of any future separately approved executor.
- No cleanup attempted on KGM VM.

## Required next gates
1. Add fixture tests to repository CI and perform security review.
2. Privileged **preflight-only** run with exact accepted evidence on KGM VM; redact sensitive output; preserve originals.
3. Implement a distinct reviewed executor with directory-descriptor-based path pinning, verified inode identities before mutation, propagate all errors and verify post-state; require owner authorization separately.
4. Capture new consistent backup + isolated restore before any cutover. Production NO-GO, FREE_ONLY, NO_SEND remain.
