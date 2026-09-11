# Phase 19 Owner-Local Runtime Drift Audit

Date: 2026-09-11
Status: `READ_ONLY_AUDIT_COMPLETE`
Scope: `kgm-e4-owner-pilot` versus canonical repository state during P19 Attempt 2

## Executive result

```text
OWNER_LOCAL_HOST = kgm-e4-owner-pilot
OBSERVED_DEPLOYED_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
AUDIT_BASE_MAIN_SHA = b4c0f6b2e5d5772654842ebb3a22e7c2a87dfb4f
REPOSITORY_COMMITS_AHEAD_OF_DEPLOYED = 516
RUNTIME_CODE_DRIFT = MATERIAL
P19_RUNTIME_CANDIDATE_IDENTITY = UNRESOLVED
RUNTIME_MUTATION_PERFORMED_BY_THIS_AUDIT = NO
```

The live P19 health control is successfully proving the availability and bounded-control properties of the software currently deployed on the owner-local VM. It is **not** sufficient evidence that current repository `main` is the code running on that VM.

## Evidence

The post-merge P19 control run on canonical `main` reported:

```text
control_run = 34577394775
target = kgm-e4-owner-pilot
tailscale_ip = 100.102.136.23
repository_sha = b4c0f6b2e5d5772654842ebb3a22e7c2a87dfb4f
deployed_sha = b31b2136b5fe982d0b63b0135479b1549041906c
service_before = active
service_after = active
runtime_db_read_as_kgmops = denied
arbitrary_root_escalation = denied
restart = skipped
ansible = ok=10 changed=0 unreachable=0 failed=0 skipped=1
```

GitHub compare from deployed SHA to the audit-base `main` returned `ahead_by = 516` and `total_commits = 516`.

This is not documentation-only drift. Source-package contents and hashes differ. Current `main` contains runtime modules that are absent from the deployed tree, including examples such as `adapter_framework.py` and `authoritative_source_pack.py`, and multiple common runtime modules have different object hashes.

## Interpretation

The P19 real-soak clock remains useful as operational evidence for the **deployed owner-local build**. However, a temporal milestone such as 24h, 72h, or 7d must not be promoted into the final `P19_BETA_OPERATIONAL_STABILITY_VALIDATED` gate while the intended runtime candidate is ambiguous.

This distinction is required:

```text
SOAK_CONTROL_CODE = current canonical GitHub main
SOAK_TARGET_RUNTIME = deployed build b31b2136...
CURRENT_REPOSITORY_APPLICATION_CODE = newer than deployed build
```

The current control workflow reports both repository context and deployed SHA, but does not require equality between them.

## Closure decision required

Before final P19 closure, choose and evidence exactly one path:

### Path A — explicitly freeze the currently deployed build as the P19 runtime candidate

Required evidence:

- owner/project record explicitly names `b31b2136...` as the intended P19 runtime candidate;
- reproducibility and applicable regression evidence for that exact candidate is available or recreated;
- no later application change is implicitly claimed as covered by this soak;
- P19 closure wording states precisely what candidate was validated.

### Path B — converge the owner-local runtime to a selected newer canonical candidate

Required behavior:

- perform a separately authorized deployment using the normal bounded deployment/recovery procedure;
- verify exact deployed SHA after deployment;
- establish a fresh P19 real-soak baseline after deployment;
- do not reuse pre-deployment elapsed time for the new candidate.

No deployment, restart, baseline change, cadence change, or Tailscale trust change was performed by this audit.

## Current classification

```text
P19_REAL_SOAK_ATTEMPT_2_TEMPORAL_EVIDENCE = CONTINUES
P19_RUNTIME_SHA_DRIFT = DETECTED
P19_RUNTIME_SHA_DRIFT_SEVERITY = CLOSURE_BLOCKER
P19_FULL_GATE = OPEN
P20_EXECUTION = NOT_STARTED
```

The blocker concerns the semantics of the final P19 gate, not current VM health. The VM health/control evidence remains valid for the build actually deployed.
