# M7 Live Public-Source Pilot Plan

Status: ACTIVE
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

2. GDELT DOC 2.0 API
   - source class: Structured data
   - access: public read-only HTTPS API
   - authentication: none
   - role: discovery/index metadata, not canonical evidence for the content of linked publisher articles

## Governing Constraints

- Runtime storage remains PROJECT_LOCAL_ONLY.
- External sources are read-only.
- No cross-project runtime resource is used.
- CI contract tests use deterministic recorded payloads and do not depend on external network availability.
- Live network validation runs in a separate smoke gate.
- Source failures are fail-closed and isolated from other source adapters.
- GDELT metadata does not replace verification against the original publisher or primary source.
- No live source is promoted to production operation by this milestone alone.

## Work Packages

### M7.1 Integration Records

Create explicit integration records covering provider, data exchanged, classification, authentication, Source of Truth, fallback, failure isolation and approval boundary.

Gate:
M7_1_INTEGRATION_RECORDS_COMPLETE

### M7.2 Live Source Adapter Contracts

Implement:

- standard-library HTTPS transport;
- source-specific parsing for Consilium RSS and GDELT DOC 2.0 JSON;
- deterministic source and raw-item identities;
- project-local provenance persistence;
- fail-closed parsing and HTTP error handling.

Gate:
M7_2_SOURCE_ADAPTER_CONTRACTS_VALIDATED

### M7.3 Collection Audit and Failure Isolation

Implement:

- collection-run audit records;
- source success/failure accounting;
- PARTIAL status when one source fails and another succeeds;
- original URL and metadata linkage to canonical raw items.

Gate:
M7_3_COLLECTION_AUDIT_VALIDATED

### M7.4 Live Smoke Validation

Execute a separate live-source smoke workflow against the documented public endpoints.

Gate:
M7_LIVE_SOURCE_SMOKE_PASS

### M7.5 Full Regression Gate

Run the complete deterministic repository test suite after live-source adapter implementation.

Gate:
M7_LIVE_PUBLIC_SOURCE_PILOT_PASS

## Completion Boundary

M7 is complete only when M7.1-M7.5 pass.

M7 completion does not authorize shared runtime storage, cross-project writes or global production operation.
