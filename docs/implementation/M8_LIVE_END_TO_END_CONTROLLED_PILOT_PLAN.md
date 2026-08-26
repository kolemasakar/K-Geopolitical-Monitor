# M8 Live End-to-End Controlled Pilot Processing Plan

Status: ACTIVE
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Goal

Connect approved M7 live-source collection to project-local claim grouping, evidence independence checks, verification status, confidence calculation and operational findings.

M8 remains within ROADMAP Phase 5 - Controlled Pilot Monitoring.

## Safety and Evidence Rules

- Runtime storage remains PROJECT_LOCAL_ONLY.
- M8 consumes only collection records already persisted by approved M7 adapters.
- A GDELT observation is discovery metadata, not an independent factual source.
- Evidence independence is evaluated by original publisher/origin host, not by adapter identity.
- Claims are grouped only by strict deterministic normalized-title equality in the M8 baseline; no semantic/fuzzy merge is permitted.
- A single independent origin remains DETECTED.
- At least two distinct original origins are required for PARTLY_VERIFIED in the M8 baseline.
- M8 does not introduce VERIFIED automatically; stronger verification requires a future explicit rule with primary-source and contradiction handling.
- Operational findings must retain claim and raw-item traceability.

## Work Packages

### M8.1 Collection-to-Claim Projection

Implement:

- collection-scoped analysis runs;
- strict normalized-title claim keys;
- raw-item evidence linkage;
- original-origin extraction from provenance URLs;
- idempotent analysis-run persistence.

Gate:
M8_1_CLAIM_PROJECTION_VALIDATED

### M8.2 Independence-Aware Verification

Implement:

- distinct origin counting;
- source-class counting;
- DETECTED/PARTLY_VERIFIED baseline status;
- confidence calculation using existing project confidence engine with origin-based independence;
- explicit prevention of GDELT adapter identity being counted as an independent publisher.

Gate:
M8_2_VERIFICATION_VALIDATED

### M8.3 Operational Finding Projection

Implement:

- project-local operational findings for analyzed claims;
- deterministic importance baseline derived from verification support, not source popularity;
- claim, raw-item and original-origin evidence references;
- explanation containing verification status and independence count.

Gate:
M8_3_OPERATIONAL_PROJECTION_VALIDATED

### M8.4 End-to-End Controlled Pilot Gate

Validate:

- live-collection records -> analysis -> operational finding flow;
- single-origin DETECTED behavior;
- two-origin PARTLY_VERIFIED behavior;
- same-origin duplicate observations do not inflate independence;
- deterministic repeated processing;
- project-local persistence and full regression CI.

Gate:
M8_LIVE_END_TO_END_PILOT_PASS

## Completion Boundary

M8 is complete only when all gates pass and final deterministic CI succeeds.

Completion of M8 may close the engineering baseline for ROADMAP Phase 5 Controlled Pilot Monitoring, but production/live operational status must remain a separate approval decision.
