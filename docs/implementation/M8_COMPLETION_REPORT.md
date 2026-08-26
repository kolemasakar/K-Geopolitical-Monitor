# M8 Completion Report

Status: BASELINE_VALIDATED
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 5 - Controlled Pilot Monitoring

## Scope Completed

M8 connected approved live-source collection to project-local analysis and operational output.

Completed baseline capabilities:

- collection-scoped live analysis;
- deterministic claim grouping;
- raw-item and original-origin provenance;
- origin-based evidence independence;
- DETECTED and PARTLY_VERIFIED baseline states;
- confidence calculation using independent-origin support;
- operational finding projection;
- claim, raw-item and origin traceability;
- idempotent repeated processing;
- live source failure isolation.

## Evidence Rules Preserved

- Adapter count is not treated as source independence.
- GDELT is discovery/index metadata and does not independently verify publisher content.
- A single original origin remains DETECTED.
- Two distinct original origins are required for PARTLY_VERIFIED in this baseline.
- M8 never assigns VERIFIED automatically.

## Validation Results

Deterministic regression:

- GitHub Actions run: 32963096313
- Result: PASS
- Tests: 73 passed in 1.07s

Live end-to-end validation:

- GitHub Actions run: 32963354135
- Result: PASS
- Collection status: PARTIAL
- Successful sources: 1
- Failed sources: 1
- Collected items: 6
- Claims: 6
- Operational findings: 6
- Verification status: 6 DETECTED
- Runtime storage: PROJECT_LOCAL_ONLY

The passing live run recorded a GDELT TLS handshake timeout while the available Consilium source continued through collection, analysis and operational finding generation. This validates failure isolation without hiding the source failure.

## Phase 5 Result

ROADMAP Phase 5 - Controlled Pilot Monitoring engineering baseline is BASELINE_VALIDATED.

This result does not mean:

- production/global operation is approved;
- unattended continuous monitoring is approved;
- all source classes or regions are covered;
- automatic VERIFIED status is approved;
- shared or mixed runtime storage is approved.

## Next

Proceed to Phase 6 - Strategic Alerts and Continuous Monitoring preparation under the existing PROJECT_LOCAL_ONLY runtime boundary.
