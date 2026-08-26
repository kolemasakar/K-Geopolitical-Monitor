# M9 Strategic Alerts and Continuous Monitoring Plan

Status: COMPLETED
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 6 - Strategic Alerts and Continuous Monitoring

## Goal

Add a deterministic project-local strategic alert layer on top of validated M8 operational findings while preserving explicit evidence, failure and storage boundaries.

M9 is an engineering baseline. It does not activate production notifications or unattended global monitoring.

## Mandatory Boundaries

- Runtime storage remains PROJECT_LOCAL_ONLY.
- Alerts are derived from persisted project findings; no direct external-source bypass is allowed.
- Alert generation is deterministic for the same inputs and configuration.
- Alert identity supports idempotent repeated monitoring cycles.
- External-source failures remain visible and are not converted into positive alerts.
- GDELT discovery metadata remains non-verifying evidence.
- No automatic VERIFIED status is introduced.
- No external notification provider is approved in M9 baseline.
- No cross-project runtime database or mixed storage is allowed.

## Alert Model Baseline

Persisted strategic alert state includes:

- alert_id;
- watch_id;
- finding_id;
- trigger_type;
- dedup_key;
- priority;
- status;
- first_triggered_at;
- last_updated_at;
- evidence_refs;
- explanation;
- invalidation_reason when applicable.

Baseline statuses:

- OPEN;
- UPDATED;
- INVALIDATED;
- RESOLVED.

Baseline priorities:

- NORMAL;
- HIGH;
- CRITICAL.

## M9.1 Trigger Detection

Implemented and validated:

- watch-scoped alert policies;
- minimum importance threshold;
- minimum confidence threshold;
- minimum verification-rank threshold;
- M8 claim verification lookup through persisted evidence refs;
- stable normalized-title deduplication across monitoring cycles;
- traceable alert explanation and evidence refs.

Gate:
M9_1_TRIGGER_DETECTION_VALIDATED

## M9.2 Invalidation and Retraction

Implemented and validated:

- explicit invalidation with mandatory reason;
- retained alert and event history;
- idempotent repeated invalidation;
- invalidated alerts remain queryable;
- qualifying re-evaluation does not silently reopen INVALIDATED or RESOLVED alerts;
- explicit resolution state and history support.

Gate:
M9_2_INVALIDATION_VALIDATED

## M9.3 Priority Watches and Cadence

Implemented and validated:

- NORMAL/HIGH/CRITICAL project-local priority policy;
- priority ordering for watches already due under the existing cadence engine;
- priority does not modify evidence confidence or verification status;
- CRITICAL priority cannot bypass watch cadence;
- persisted policy survives runtime restart;
- no background daemon is required for baseline validation.

Gate:
M9_3_PRIORITY_CADENCE_VALIDATED

## M9.4 End-to-End Alert Gate

Validated:

- M8 finding -> trigger -> strategic alert persistence;
- duplicate suppression for repeated evaluation;
- same-title new-cycle finding updates an existing alert instead of duplicating it;
- priority assignment;
- invalidation history;
- restart persistence;
- project-local database reuse after restart;
- deterministic full regression CI.

Gate:
M9_STRATEGIC_ALERT_BASELINE_PASS

## Validation Evidence

Initial M9 implementation regression:

- GitHub Actions run 32965231876;
- 80 passed in 1.58s.

Hardened M9 acceptance regression:

- GitHub Actions run 32965387054;
- 82 passed in 1.71s;
- restart persistence: PASS;
- priority/cadence separation: PASS.

## Completion Boundary

All M9 engineering gates passed.

ROADMAP Phase 6 - Strategic Alerts and Continuous Monitoring engineering baseline is BASELINE_VALIDATED.

This completion does not approve external notification delivery, unattended production scheduling, global coverage, mixed/shared runtime storage or production/live OPERATIONAL status.
