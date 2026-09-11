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

This is not documentation-only drift. Source-package contents and hashes differ. Current `main` contains runtime modules that are absent from the deployed tree, including examples such as `adapter_framework.py` and `authoritative_source_pack.py`, and multiple repository/runtime-adjacent modules have different object hashes.

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

## 2026-09-11 supplemental candidate evidence

The repository advanced after the original audit. Against canonical pre-sync `main` `5714a76aaf12c77993ed5a02165c02a48d953758`, the deployed `b31b...` candidate is now 522 commits behind with zero commits in the opposite direction. The original 516-count remains historically correct for the earlier `b4c0f6...` audit-base.

An isolated re-run of the exact historical CI job for `b31b...` completed successfully on 2026-09-11:

```text
RUN_ID = 33486945121
RUN_ATTEMPT = 2
JOB_ID = 103264025849
HEAD_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
RESULT = SUCCESS
TEST_RESULT = 317 passed in 39.36s
```

This proves current-runner exact-source compatibility, not byte-for-byte reconstruction of the 2026-09-01 dependency environment. The historical candidate workflow used mutable action tags and broad dependency ranges; current canonical CI uses a stricter compatibility constraints contract.

A targeted post-candidate regression screening found no known candidate-runtime blocker in sampled explicit `fix`, `regression`, `security`, and `compatibility` changes. Exhaustive semantic review remains open.

### Active owner-local runtime path blob comparison

A structural blob comparison materially narrows the drift interpretation. The following active owner-local application path and direct dependencies are blob-identical between `b31b...` and `5714a76...`:

```text
unattended_runner.py
unattended_service.py
runtime_health.py
monitoring_cycle.py
operational_monitoring.py
live_operational_cycle.py
live_end_to_end.py
live_sources.py
database.py
runtime_lease.py
runtime_storage.py
reproducibility.py
operational_output.py
controlled_pilot.py
confidence_engine.py
```

The deployed systemd execution unit is also blob-identical:

```text
deployment/systemd/kgm-monitor.service
blob = 0ec08257ba49fdc28f2fd96f95baac93cab63fe9
```

The broader repository is not equivalent. For example, the E4 bootstrap script differs:

```text
b31b blob = 7231584fe80999681ccb9bfc3ae878c3eee76d29
5714a76 blob = c33aa51c70e79e6c8aa66335c0937bc0371d3b81
```

Current dependency policy, later modules, migrations, workflows, tests and documentation also differ.

Accordingly the refined interpretation is:

```text
OWNER_LOCAL_ACTIVE_RUNTIME_CODE_PATH_EQUIVALENCE = PASS_FOR_INSPECTED_BLOBS
OWNER_LOCAL_SYSTEMD_EXECUTION_CONTRACT_EQUIVALENCE = PASS
FULL_REPOSITORY_EQUIVALENCE = NO
FULL_DEPLOYMENT_TOOLING_EQUIVALENCE = NO
EXACT_DEPENDENCY_ENVIRONMENT_EQUIVALENCE = NOT_PROVEN
CURRENT_MAIN_RUNTIME_EQUIVALENCE = NOT_CLAIMED
PATH_A_READINESS = CONDITIONAL_PREFERRED_EVIDENCE_STRENGTHENED
```

The detailed acceptance/regression/blob evidence is staged in draft PR #79 and remains unmerged while the soak is active.

## Current classification

```text
P19_REAL_SOAK_ATTEMPT_2_TEMPORAL_EVIDENCE = CONTINUES
P19_RUNTIME_SHA_DRIFT = DETECTED
P19_RUNTIME_SHA_DRIFT_SEVERITY = FINAL_CLOSURE_SEMANTICS_BLOCKER
P19_ACTIVE_RUNTIME_PATH_BLOB_EQUIVALENCE = PASS_FOR_INSPECTED_BLOBS
P19_PATH_A = CONDITIONAL_PREFERRED_NOT_AUTHORIZED
P19_FULL_GATE = OPEN
P20_EXECUTION = NOT_STARTED
```

The remaining blocker concerns final candidate identity/closure semantics, exact dependency limitations, temporal gates, and bounded regression-review acceptance—not current VM health. The VM health/control evidence remains valid for the build actually deployed.
