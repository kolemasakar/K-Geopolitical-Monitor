# M9 Strategic Alerts and Continuous Monitoring Plan

Status: ACTIVE
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 6 - Strategic Alerts and Continuous Monitoring

## Goal

Add a deterministic project-local strategic alert layer on top of validated M8 operational findings while preserving explicit evidence, failure and storage boundaries.

M9 is an engineering baseline. It does not activate production notifications or unattended global monitoring.

## Mandatory Boundaries

- Runtime storage remains PROJECT_LOCAL_ONLY.
- Alerts must be derived from persisted project findings; no direct external-source bypass is allowed.
- Alert generation must be deterministic for the same inputs and configuration.
- Alert identity must support idempotent repeated monitoring cycles.
- External-source failures must remain visible and must not be converted into positive alerts.
- GDELT discovery metadata remains non-verifying evidence.
- No automatic VERIFIED status is introduced.
- No external notification provider is approved in M9 baseline.
- No cross-project runtime database or mixed storage is allowed.

## Alert Model Baseline

Strategic alerts require explicit persisted state:

- alert_id;
- watch_id;
- finding_id;
- trigger_type;
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

Implement deterministic trigger evaluation over M8 operational findings.

Initial trigger contract:

- evidence/verification support must satisfy the configured watch threshold;
- finding importance must satisfy the configured alert threshold;
- the trigger must retain finding and evidence traceability;
- repeated evaluation of the same qualifying finding must not create duplicate alerts.

Gate:
M9_1_TRIGGER_DETECTION_VALIDATED

## M9.2 Invalidation and Retraction

Implement explicit alert invalidation when the supporting finding is no longer eligible or when a persisted contradiction/invalidation condition is supplied by the monitoring layer.

Requirements:

- invalidation never deletes alert history;
- invalidation reason is mandatory;
- invalidated alerts remain queryable;
- repeated invalidation is idempotent;
- invalidation cannot silently become a new positive alert.

Gate:
M9_2_INVALIDATION_VALIDATED

## M9.3 Priority Watches and Cadence

Extend project-local watch configuration with deterministic alert priority and cadence semantics.

Requirements:

- watch priority influences scheduling eligibility, not evidence truth;
- priority must not increase verification confidence;
- cadence decisions must be deterministic from persisted watch state and current time;
- interrupted cycles remain recoverable through existing project-local run recovery;
- no background daemon is required for baseline validation.

Gate:
M9_3_PRIORITY_CADENCE_VALIDATED

## M9.4 End-to-End Alert Gate

Validate:

- finding -> trigger -> strategic alert persistence;
- duplicate suppression;
- priority assignment;
- alert update behavior;
- invalidation history;
- restart persistence;
- project-local isolation;
- deterministic full regression CI.

Gate:
M9_STRATEGIC_ALERT_BASELINE_PASS

## Completion Boundary

M9 is complete only when all gates pass and the full deterministic regression suite succeeds.

M9 completion may validate the Phase 6 engineering baseline but must not by itself set production/live operational status to OPERATIONAL. External notification delivery, unattended production scheduling and global coverage require separate explicit approval.
