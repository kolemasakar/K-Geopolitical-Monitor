# Phase 19 Attempt 3 Semantic Runtime Drift Audit

Date: 2026-09-13
Status: `READ_ONLY_AUDIT_COMPLETE / ATTEMPT_3_ACTIVE`
Scope: deployed owner-local P19 runtime candidate versus canonical repository state

## Executive result

```text
OWNER_LOCAL_HOST = kgm-e4-owner-pilot
P19_ATTEMPT = 3
P19_RUNTIME_CANDIDATE = b31b2136b5fe982d0b63b0135479b1549041906c
CANONICAL_MAIN_AT_AUDIT = 3bfe4c1021fe27a363463d3eb8ecc3018b0989a3
P19_ATTEMPT_3_BASELINE_UTC = 2026-09-13T08:51:24Z
REPOSITORY_COMMITS_AHEAD_OF_DEPLOYED = 542
FULL_REPOSITORY_EQUIVALENCE = NO
INSPECTED_ACTIVE_RUNTIME_PATH_EQUIVALENCE = PASS_TRANSITIVELY
SYSTEMD_EXECUTION_CONTRACT_EQUIVALENCE = PASS_TRANSITIVELY
REDEPLOY_REQUIRED_BY_REPOSITORY_DRIFT_ALONE = NO
RUNTIME_MUTATION_PERFORMED_BY_THIS_AUDIT = NO
```

The repository has advanced substantially beyond the deployed owner-local build, but the evidence supports a narrower and operationally relevant conclusion: the inspected active application runtime path used by the P19 owner-local service remains blob-equivalent to the deployed Path A candidate. Later canonical changes between the last blob-equivalence anchor and Attempt 3 `main` are control-plane, evidence, documentation, and P19 support changes rather than modifications to the inspected active application runtime path.

This does **not** claim full repository equivalence or exact dependency-environment equivalence.

## 1. Broad repository drift

GitHub compare:

```text
base = b31b2136b5fe982d0b63b0135479b1549041906c
head = 3bfe4c1021fe27a363463d3eb8ecc3018b0989a3
status = ahead
ahead_by = 542
behind_by = 0
total_commits = 542
```

The broad diff contains extensive later-phase application modules, migrations, workflows, tests, documentation, activation tooling, and operational controls. Therefore:

```text
FULL_REPOSITORY_EQUIVALENCE = NO
REPOSITORY_SHA_EQUALITY = NO
```

Repository-level SHA drift must not be represented as if `main` were the exact deployed runtime.

## 2. Prior active-runtime blob-equivalence anchor

The 2026-09-11 runtime drift audit established blob identity between deployed `b31b...` and canonical anchor `5714a76aaf12c77993ed5a02165c02a48d953758` for the inspected active owner-local application path:

```text
src/kgeopolitical_monitor/unattended_runner.py
src/kgeopolitical_monitor/unattended_service.py
src/kgeopolitical_monitor/runtime_health.py
src/kgeopolitical_monitor/monitoring_cycle.py
src/kgeopolitical_monitor/operational_monitoring.py
src/kgeopolitical_monitor/live_operational_cycle.py
src/kgeopolitical_monitor/live_end_to_end.py
src/kgeopolitical_monitor/live_sources.py
src/kgeopolitical_monitor/database.py
src/kgeopolitical_monitor/runtime_lease.py
src/kgeopolitical_monitor/runtime_storage.py
src/kgeopolitical_monitor/reproducibility.py
src/kgeopolitical_monitor/operational_output.py
src/kgeopolitical_monitor/controlled_pilot.py
src/kgeopolitical_monitor/confidence_engine.py
```

The deployed systemd execution unit was also blob-identical:

```text
deployment/systemd/kgm-monitor.service
blob = 0ec08257ba49fdc28f2fd96f95baac93cab63fe9
```

The historical audit explicitly did not claim full repository, deployment-tooling, or exact dependency-environment equivalence.

## 3. Anchor-to-Attempt-3 main semantic review

Current GitHub compare:

```text
base = 5714a76aaf12c77993ed5a02165c02a48d953758
head = 3bfe4c1021fe27a363463d3eb8ecc3018b0989a3
status = ahead
ahead_by = 20
behind_by = 0
total_commits = 20
changed_files_returned_by_compare = 17
```

The changed paths returned by the current compare are:

```text
ARCHITECTURE.md
docs/checkpoints/PROJECT_CHECKPOINT_2026-09-11_P19_CONTROL_PLANE_RECONCILIATION.md
docs/checkpoints/PROJECT_CHECKPOINT_2026-09-11_PHASE_19_PRE_24H_FINAL_SYNC.md
docs/checkpoints/PROJECT_CHECKPOINT_2026-09-11_PHASE_19_PRE_24H_PARALLEL_PREP_COMPLETE.md
docs/checkpoints/PROJECT_CHECKPOINT_2026-09-11_PHASE_19_REAL_SOAK_ATTEMPT_2_ACTIVE.md
docs/checkpoints/PROJECT_CHECKPOINT_2026-09-13_P19_PARALLEL_PREP_AND_AUDIT_REFRESH.md
docs/evidence/PHASE_19_ATTEMPT_2_CONTINUITY_FAILURE_2026-09-13.md
docs/evidence/PHASE_19_ATTEMPT_3_PATH_A_OWNER_DECISION_2026-09-13.md
docs/evidence/PHASE_19_OWNER_LOCAL_RUNTIME_DRIFT_AUDIT_2026-09-11.md
docs/evidence/PHASE_19_PRE_24H_RUNTIME_REVALIDATION_2026-09-11.md
docs/evidence/REPOSITORY_SECURITY_STATIC_AUDIT_2026-09-11.md
docs/implementation/PHASE_19_CLOSURE_PREP_AND_EVIDENCE_RETENTION.md
docs/implementation/PHASE_20_SOURCE_COVERAGE_COLLECTION_QUALITY_DESIGN_SPEC.md
docs/ops/KGM_RDC_BACKGROUND_AUTOSTART_ACCEPTANCE_2026-09-11.md
docs/ops/KGM_RDC_ON_DEMAND_ACCEPTANCE_2026-09-11.md
docs/ops/KGM_TAILSCALE_ANSIBLE_CONTROL_PLANE.md
ops/p19/real_soak_baseline.txt
```

None of the inspected active application runtime modules listed in section 2, and not the deployed `deployment/systemd/kgm-monitor.service`, changed between `5714a76...` and Attempt 3 `main` `3bfe4c...`.

Accordingly, the transitive evidence is:

```text
b31b... -> 5714a76... active inspected runtime blobs = IDENTICAL
5714a76... -> 3bfe4c... inspected active runtime paths = UNCHANGED
therefore:
b31b... -> 3bfe4c... inspected active runtime path equivalence = PASS_TRANSITIVELY
```

This is a path-scoped conclusion, not a whole-repository equivalence claim.

## 4. Fresh live Attempt 3 observation

Qualifying bounded control:

```text
workflow = KGM Tailscale Ansible Control
run_number = 27
run_id = 34756351332
job_id = 103721264801
event = workflow_dispatch
repository_sha = 3bfe4c1021fe27a363463d3eb8ecc3018b0989a3
operation = health
observation_utc = 2026-09-13T12:10:51Z
deployed_sha = b31b2136b5fe982d0b63b0135479b1549041906c
service_before = active
service_after = active
runtime_db_read_as_kgmops = denied
arbitrary_root_escalation = denied
restart = skipped
ansible = ok=10 changed=0 unreachable=0 failed=0 skipped=1
KGM_TAILSCALE_ANSIBLE_CONTROL = PASS
P19_REAL_SOAK_OBSERVATION = PASS
```

This observation confirms that the selected Path A candidate remains deployed and healthy without restart or runtime mutation.

## 5. Fresh Attempt 3 soak audit

```text
workflow = P19 Owner-Local Soak Gate Audit
run_number = 47
run_id = 34756392146
job_id = 103721368877
baseline_utc = 2026-09-13T08:51:24Z
evaluated_at_utc = 2026-09-13T12:11:17Z
P19_CONTROL_COMPLETED_RUNS = 2
P19_CONTROL_FAILED_RUNS = 0
P19_QUALIFYING_HEALTH_OBSERVATIONS = 2
audit_status = PASS
continuity_status = PASS
current_max_gap_hours = 3.3241666666666667
max_allowed_gap_hours = 7.0
latest_observation_utc = 2026-09-13T12:10:51Z
24h = IN_PROGRESS
72h = IN_PROGRESS
7d = IN_PROGRESS
```

Preserved audit artifact:

```text
artifact_name = p19-owner-local-soak-gate-audit-34756392146
artifact_id = 10317692124
artifact_sha256 = 71b78216e7d629963931041c7e32973e7fb5f36ae80c62b10ff7872cdf9287fb
retention_days = 30
```

The audit is currently fail-closed healthy; no temporal milestone is promoted before its boundary and qualifying terminal observation.

## 6. Interpretation for Attempt 3

Path A was explicitly selected by the owner before the fresh Attempt 3 baseline. The candidate under soak is therefore unambiguous:

```text
P19_RUNTIME_CANDIDATE = b31b2136b5fe982d0b63b0135479b1549041906c
P19_ATTEMPT_3_BASELINE_UTC = 2026-09-13T08:51:24Z
P19_CONTINUITY_STATUS = PASS_AS_OF_2026-09-13T12:11:17Z
P19_24H_GATE = IN_PROGRESS
P19_72H_GATE = IN_PROGRESS
P19_7D_GATE = IN_PROGRESS
```

Later source modules present on current `main` but absent from `b31b...` are repository evolution and are not implicitly covered by the Path A soak. They require their own activation/deployment validation if selected for a later runtime.

## 7. Decision

No redeployment or restart is justified by repository SHA drift alone during active Attempt 3. A deployment would change the runtime candidate and invalidate the current candidate-specific elapsed soak unless a separately authorized transition establishes a new baseline.

Therefore:

```text
KEEP_DEPLOYED_PATH_A_CANDIDATE = YES
CONTINUE_ATTEMPT_3 = YES
DEPLOY = NO
RESTART = NO
BASELINE_CHANGE = NO
CADENCE_CHANGE = NO
EVALUATOR_CHANGE = NO
TAILSCALE_TRUST_CHANGE = NO
P20_LIVE_ACTIVATION = NO
MIGRATION_033 = NOT_CREATED_NOT_PREAUTHORIZED
```

## 8. Scope limitation

This audit does not prove:

- full repository equivalence;
- exact historical dependency-environment equivalence;
- activation of later canonical modules in the deployed service;
- successful completion of 24h, 72h, or 7d temporal gates;
- authorization for P20 live execution, shared runtime activation, paid resources, migration 033, deployment, restart, or control-plane changes.

It proves the narrower current operational conclusion required for Attempt 3: the explicitly selected deployed candidate remains healthy, continuity is currently within the 7-hour evidence-gap contract, and no inspected active runtime-path change requires a redeploy during the soak.
