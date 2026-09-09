# Phase 18 Activation Strategy — Beta Single-Owner Boundary

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `APPROVED`
Decision class: strategy / activation boundary / beta operation
Canonical base at approval: `445070a270cfd7a9b926291a02caff2ed06c29ad`

## Decision

The owner approves the post-A1 activation strategy and the A2–A5 implementation sequence.

Until beta testing is formally completed, K-Geopolitical Monitor is operated for exactly one user: the owner.

During this beta period:

- multi-user/team operation is out of scope;
- shared/team runtime activation is not required for beta completion;
- paid infrastructure/providers/resources are not considered and are not authorized;
- free or already-authorized disposable non-production resources may be used only for validation evidence;
- owner-local runtime remains canonical and independently operable;
- no external candidate may auto-promote to canonical runtime;
- no canonical data cutover is authorized;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

## Approved Strategy

The project must not rush activation. The activation workstream remains evidence-driven:

`A1 VALIDATED -> A2 LIVE CONTROLS -> A3 SHADOW/RECONCILIATION -> A4 FRESH LAUNCH EVIDENCE -> A5 EXPLICIT OWNER ACTIVATION DECISION`

A2–A4 are readiness/proof stages. Their success does not itself activate shared runtime or production operation.

A5 remains the only stage at which an activation/cutover decision may be authorized.

## Beta-Specific Interpretation

Because the system is single-owner until the end of beta, the immediate objective is not to move the canonical runtime into shared/team infrastructure. The objective is to prove that the architecture can safely support such a move later without compromising the current owner-local canonical path.

Accordingly, Phase 18 activation readiness may reach `ACTIVATION_READY / NOT_ACTIVATED` and remain there through beta completion.

## Cost Boundary

`BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`

No paid provider, paid plan, paid database, paid networking feature, paid backup/PITR feature, or other recurring paid infrastructure may be introduced during beta under this decision.

If a required validation cannot be completed on a free/no-charge path, that validation must remain blocked or be redesigned for a no-charge path rather than silently escalating cost.

## State Synchronization

This approval does not change the strategic machine-state synchronization by itself.

`docs/state/CURRENT_PROJECT_STATE.json` remains at:

- `state_sync_version = 4.34`;
- `current_position = PHASE_18_P18_9_VALIDATED_ACTIVATION_OWNER_GATE`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`.

A later formal synchronization gate may update machine-readable state when the activation workstream explicitly reaches such a gate.
