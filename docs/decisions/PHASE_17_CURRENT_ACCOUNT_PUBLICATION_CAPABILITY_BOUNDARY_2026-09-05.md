# Phase 17 — Current Account Publication Capability Boundary

Date: 2026-09-05
Project: K-Geopolitical Monitor
Decision status: `ACTIVE_CONSTRAINT`
Phase 17 readiness: `VALIDATED_READY / NOT_ACTIVATED`
Current account publication capability: `UNAVAILABLE`
Capability gate: `PHASE_17_EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`
Owner activation gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

## Decision

The project owner has established that actual external publication is not available for the current account.

This constraint is authoritative for current project planning and operation. It is an account/platform capability boundary, not a failure of the validated Phase 17 engineering-readiness layer.

## Operational Consequence

No Phase 17 workflow may attempt real external publication while the current-account capability remains unavailable.

An owner approval by itself is insufficient to activate publication under the current constraint. Actual publication requires both:

1. a future account/platform state in which the required external-publication capability is available; and
2. a separate explicit owner activation decision under `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`.

After both conditions exist, launch-time platform, security, privacy, exposure and rollback requirements must be revalidated before any real target is enabled.

## Preserved State

Unchanged:

- Phase 17 engineering readiness remains `VALIDATED_READY / NOT_ACTIVATED`;
- public sharing remains `NOT_ACTIVE`;
- external publication targets remain `NOT_ACTIVATED`;
- public ingress remains `NOT_APPROVED_NOT_DEPLOYED`;
- public GPT Action remains `NOT_CONNECTED_NOT_APPROVED`;
- backend HTTPS remains `NOT_DEPLOYED`;
- owner execution remains `DISABLED` / separately gated;
- paid providers remain `NONE_APPROVED`;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

No account upgrade, paid plan, provider purchase or alternative publication channel is implied or approved by this decision.

## Reopen Condition

This boundary may be reconsidered only after the owner establishes that the relevant account/platform publication capability has changed. Until then, the project state is:

`VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`
