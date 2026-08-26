# M7 Live Public-Source Pilot Plan

Status: COMPLETE
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Goal

Extend the validated M6 controlled-source baseline to a small live read-only public-source pilot without changing the PROJECT_LOCAL_ONLY runtime-storage boundary.

M7 remains within ROADMAP Phase 5 - Controlled Pilot Monitoring.

## Selected Pilot Integrations

1. Council of the European Union / European Council press-release RSS
   - source class: Official sources
   - access: public read-only RSS
   - authentication: none
   - controlled-pilot validation: PASS

2. GDELT DOC 2.0 API
   - source class: Structured data
   - access: public read-only HTTPS API
   - authentication: none
   - role: discovery/index metadata, not canonical evidence for the content of linked publisher articles
   - controlled-pilot validation: PASS

## Governing Constraints

- Runtime storage remains PROJECT_LOCAL_ONLY.
- External sources are read-only.
- No cross-project runtime resource is used.
- CI contract tests use deterministic recorded payloads and do not depend on external network availability.
- Live network validation runs in a separate manual smoke gate.
- Source failures are fail-closed and isolated from other source adapters.
- GDELT metadata does not replace verification against the original publisher or primary source.
- No live source is promoted to production operation by this milestone alone.

## Gate Results

M7_1_INTEGRATION_RECORDS_COMPLETE: PASS
M7_2_SOURCE_ADAPTER_CONTRACTS_VALIDATED: PASS
M7_3_COLLECTION_AUDIT_VALIDATED: PASS
M7_LIVE_SOURCE_SMOKE_PASS: PASS
M7_LIVE_PUBLIC_SOURCE_PILOT_PASS: PASS

## Evidence

Deterministic regression:
- GitHub Actions run: 32962379499
- result: 68 passed in 0.77s

Live smoke:
- GitHub Actions run: 32962576874
- Consilium RSS: success; 7 parsed items for query Ukraine
- GDELT DOC 2.0: success; 5 parsed items for query Ukraine

Detailed result:
- docs/implementation/M7_LIVE_PUBLIC_SOURCE_PILOT_RESULT.md

## Completion Boundary

M7 is COMPLETE and BASELINE_VALIDATED.

M7 completion does not authorize shared runtime storage, cross-project writes or global production operation.

ROADMAP Phase 5 remains active. The next engineering milestone is M8 Live End-to-End Controlled Pilot Processing, which must connect approved live-source collection to project-local verification/analysis and operational output.
