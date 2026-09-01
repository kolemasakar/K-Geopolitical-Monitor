# E9A.1 Single-Instance Runtime Lease Result

Status: BASELINE_VALIDATED
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A — Owner-Only Production Runtime Hardening

## Scope

Add a project-local, OS-backed, non-blocking runtime lease so the canonical unattended runtime fails closed if a second daemon or manual `--once` invocation attempts to run concurrently against the same KGM project-local runtime.

## Implementation

Added:
- `src/kgeopolitical_monitor/runtime_lease.py`;
- `tests/test_runtime_lease.py`.

Updated:
- `src/kgeopolitical_monitor/unattended_runner.py`;
- `tests/test_unattended_runner.py`.

Behavior:
- canonical lease path: `<project_root>/data/.kgm-monitor.lock`;
- lease is acquired before `build_unattended_service()` and therefore before runtime/database initialization;
- `--once` and long-running daemon mode use the same lease boundary;
- lock acquisition is non-blocking;
- a second holder fails closed with `RuntimeLeaseError`;
- the OS lock, not PID text, is authoritative;
- PID content is diagnostic only;
- abnormal process termination releases the OS lock automatically;
- persistent stale PID text cannot by itself block a replacement process;
- storage remains `PROJECT_LOCAL_ONLY`.

## Truth/Storage Boundaries

PASS:
- no shared runtime DB introduced;
- no cross-project writes introduced;
- no public API/dashboard/GPT exposure introduced;
- watch/run truth semantics unchanged;
- database initialization is not performed by a rejected second `--once` process;
- E9 Shared Production Runtime remains NOT_APPROVED;
- production/live remains NOT_OPERATIONAL.

## Validation

Validated HEAD:
`3384fd4d1ddb3d23af6ccee9fc77a75d76d85583`

x64 GitHub Actions:
- workflow: CI;
- run: `33481341148`;
- job: `99771428967`;
- result: SUCCESS;
- regression: `299 passed, 1 warning in 32.38s`.

Native ARM64 GitHub Actions:
- workflow: E4 ARM64 Validation;
- run: `33481341134`;
- job: `99771428942`;
- architecture: `aarch64`;
- result: SUCCESS;
- full regression: `299 passed, 1 warning in 27.43s`;
- host bootstrap shell: PASS;
- unattended one-tick smoke: PASS;
- systemd unit contract: PASS.

## Gate Decision

`E9A.1_SINGLE_INSTANCE_RUNTIME_LEASE = BASELINE_VALIDATED`

Next step:
`E9A.2_SQLITE_RUNTIME_PROFILE`
