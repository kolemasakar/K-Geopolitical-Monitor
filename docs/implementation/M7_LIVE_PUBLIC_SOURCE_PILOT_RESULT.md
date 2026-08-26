# M7 Live Public-Source Pilot Result

Status: PASS
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Deterministic Regression Evidence

Validation checkpoint: 7cc9bae7d2244a373522041a8b174c724971a263
Workflow: CI
Run: 32962379499
Python: 3.11.16
Result: 68 passed in 0.77s
Conclusion: success

## Live Network Smoke Evidence

Workflow: Live Source Smoke
Run: 32962576874
Job: 98157971775
Commit: dcea5ab9162a6a64eff1129a769cf4309dc76db8
Conclusion: success

Observed live parsing result:

- Consilium press-release RSS: success; 7 parsed items for query Ukraine.
- GDELT DOC 2.0: success; 5 parsed items for query Ukraine.

The smoke workflow was returned to workflow_dispatch-only mode after the one-time validation run so external network availability does not become part of the normal deterministic CI gate.

## Validated Capabilities

- explicit controlled-pilot integration records;
- public read-only HTTPS access without credentials;
- Consilium RSS parsing and watch filtering;
- GDELT DOC 2.0 JSON discovery parsing;
- GDELT discovery metadata kept separate from publisher factual evidence;
- deterministic live-source item identities;
- canonical project-local source/raw-item persistence;
- per-collection provenance records with original URLs and metadata;
- collection audit records;
- per-source success/failure accounting;
- PARTIAL collection status when one adapter fails;
- fail-closed malformed-response handling;
- HTTPS-only runtime transport;
- repeated collection without duplicate canonical raw items;
- full M0-M7 deterministic regression suite.

## Gate Result

M7_1_INTEGRATION_RECORDS_COMPLETE: PASS
M7_2_SOURCE_ADAPTER_CONTRACTS_VALIDATED: PASS
M7_3_COLLECTION_AUDIT_VALIDATED: PASS
M7_LIVE_SOURCE_SMOKE_PASS: PASS
M7_LIVE_PUBLIC_SOURCE_PILOT_PASS: PASS

## Architecture Boundary

Runtime storage remains PROJECT_LOCAL_ONLY.

No shared runtime database, cross-project write, credentialed provider or implicit external store is part of the validated M7 implementation.

The two integrations are approved for controlled pilot use only. Production/global operational approval is not granted.

## Next Gate

M8 should validate live end-to-end controlled pilot processing from approved live-source collection through project-local verification/analysis and operational output.

ROADMAP Phase 5 Controlled Pilot Monitoring remains active until that live end-to-end gate is completed.
