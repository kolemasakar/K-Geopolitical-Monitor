# Phase 19 — `b31b2136...` Owner-Local Runtime Path Blob Equivalence

Date: 2026-09-11
Status: `PASS_FOR_INSPECTED_ACTIVE_PATH / FULL_REPOSITORY_EQUIVALENCE_NO`

## Purpose

Strengthen the Path A decision with a structural blob-level comparison between the actually deployed candidate `b31b2136b5fe982d0b63b0135479b1549041906c` and canonical repository state `5714a76aaf12c77993ed5a02165c02a48d953758`.

This is read-only evidence. It does not deploy, restart, change the P19 baseline, mutate workflows, or alter the Tailscale trust path.

## Inspected active owner-local application path

The following files have the same Git blob SHA in `b31b...` and `5714a76...`:

| Path | Git blob SHA | Result |
| --- | --- | --- |
| `src/kgeopolitical_monitor/unattended_runner.py` | `2cf9a4a996eb15f1574f1eff513d17e7d2590c49` | IDENTICAL |
| `src/kgeopolitical_monitor/unattended_service.py` | `670ad40c02818fdf3943bee0ec9bc599143228b4` | IDENTICAL |
| `src/kgeopolitical_monitor/runtime_health.py` | `f4bf3bf67ad826a883f3545fc4f392306185d022` | IDENTICAL |
| `src/kgeopolitical_monitor/monitoring_cycle.py` | `6a512925596cf10d8d04562988fb1880651290b7` | IDENTICAL |
| `src/kgeopolitical_monitor/operational_monitoring.py` | `1d7f60d7a0cced43f423325f37bcb0680f3d2ea6` | IDENTICAL |
| `src/kgeopolitical_monitor/live_operational_cycle.py` | `b18e43e142c9ba2fff59711f16025130c5207355` | IDENTICAL |
| `src/kgeopolitical_monitor/live_end_to_end.py` | `4a7d82f6c2a43e88cb6f5c1d2917ae6a00f218ca` | IDENTICAL |
| `src/kgeopolitical_monitor/live_sources.py` | `b6c001ead8c3dea6227d519c843246c45846fb6b` | IDENTICAL |
| `src/kgeopolitical_monitor/database.py` | `bf46459292ea44dc6caa6dc313b75ad98d161c29` | IDENTICAL |
| `src/kgeopolitical_monitor/runtime_lease.py` | `6d7fdf83d1d735ff1933558f4cbc422bb7066f08` | IDENTICAL |
| `src/kgeopolitical_monitor/runtime_storage.py` | `3c5f596afa9aa47afae4094e746bf6e76bcd8d73` | IDENTICAL |
| `src/kgeopolitical_monitor/reproducibility.py` | `7554f556cb0029c28588133df59bf7e57321a7c1` | IDENTICAL |
| `src/kgeopolitical_monitor/operational_output.py` | `234d7252380d330984549bb94bc0dd50e3af9c48` | IDENTICAL |
| `src/kgeopolitical_monitor/controlled_pilot.py` | `f6011f72a489a8f7cd5cb89d7ff785db4c1d9ef8` | IDENTICAL |
| `src/kgeopolitical_monitor/confidence_engine.py` | `254cdd874123177740902a4492b20eef7b1a027f` | IDENTICAL |

The systemd unit used to execute this stack is also blob-identical:

```text
deployment/systemd/kgm-monitor.service
blob = 0ec08257ba49fdc28f2fd96f95baac93cab63fe9
result = IDENTICAL
```

The unit starts `python -m kgeopolitical_monitor.unattended_runner` from `/opt/k-geopolitical-monitor` with project-local runtime storage and the hardened service boundary.

## Important non-equivalence

The repository as a whole is **not** equivalent. At the pre-sync snapshot, canonical `5714a76...` was 522 commits ahead of deployed `b31b...`, with material additions across later phases, workflows, tests, documentation, dependency policy and other infrastructure.

A concrete deployment-layer difference is already present:

```text
b31b deployment/scripts/e4_bootstrap_ubuntu_arm64.sh
blob = 7231584fe80999681ccb9bfc3ae878c3eee76d29

5714a76 deployment/scripts/e4_bootstrap_ubuntu_arm64.sh
blob = c33aa51c70e79e6c8aa66335c0937bc0371d3b81

result = DIFFERENT
```

Current dependency policy also differs materially from the candidate-era environment, and exact historical dependency reconstruction is not proven.

## Interpretation

This evidence substantially narrows the meaning of the large repository drift:

- the inspected active owner-local application execution path is blob-identical;
- the service unit that invokes that path is blob-identical;
- the full repository/deployment/bootstrap/dependency environment is not identical;
- current-main features outside the inspected active path are not demonstrated as deployed;
- no claim is made that canonical `main` as a whole was soak-tested.

Therefore the correct semantic result is:

```text
OWNER_LOCAL_ACTIVE_RUNTIME_CODE_PATH_EQUIVALENCE = PASS_FOR_INSPECTED_BLOBS
OWNER_LOCAL_SYSTEMD_EXECUTION_CONTRACT_EQUIVALENCE = PASS
FULL_REPOSITORY_EQUIVALENCE = NO
FULL_DEPLOYMENT_TOOLING_EQUIVALENCE = NO
EXACT_DEPENDENCY_ENVIRONMENT_EQUIVALENCE = NOT_PROVEN
CURRENT_MAIN_RUNTIME_EQUIVALENCE = NOT_CLAIMED
```

## Effect on Path A

Combined with:

- historical exact-candidate CI PASS;
- historical exact-candidate real-host validation PASS;
- contemporary exact-source replay PASS (`317 passed`);
- no candidate-relevant blocker found in the targeted post-candidate regression screening;
- active Attempt 2 temporal evidence for the deployed build;

this makes Path A the preferred low-disruption closure route, subject to the remaining fail-closed requirements:

```text
PATH_A_READINESS = CONDITIONAL_PREFERRED / EVIDENCE_STRENGTHENED
PATH_A_AUTHORIZED = NO
DEPLOYED_SHA_REVERIFY_AT_MILESTONES = REQUIRED
24H_72H_7D_TEMPORAL_GATES = IN_PROGRESS
EXHAUSTIVE_OR_OWNER_ACCEPTED_BOUNDED_REGRESSION_REVIEW = REQUIRED_FOR_FINAL_DECISION
```
