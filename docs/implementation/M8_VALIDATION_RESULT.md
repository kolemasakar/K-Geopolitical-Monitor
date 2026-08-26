# M8 Validation Result

Status: PASS
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Gate Results

- M8_1_CLAIM_PROJECTION_VALIDATED: PASS
- M8_2_VERIFICATION_VALIDATED: PASS
- M8_3_OPERATIONAL_PROJECTION_VALIDATED: PASS
- M8_LIVE_END_TO_END_PILOT_PASS: PASS

## Deterministic Validation

GitHub Actions run 32963096313:

- 73 passed in 1.07s;
- collection-to-claim projection validated;
- same-origin observations do not inflate source independence;
- two distinct origins can reach PARTLY_VERIFIED;
- single-origin evidence remains DETECTED;
- operational findings retain claim/raw-item/origin evidence references;
- repeated processing remains deterministic and project-local.

## Live Validation

Initial live E2E smoke identified a GDELT HTTP 429 response. The live gate was aligned with the already approved per-source failure-isolation contract rather than requiring all external sources to succeed simultaneously.

GitHub Actions run 32963354135 then passed with:

- collection_status: PARTIAL;
- source_success_count: 1;
- source_failure_count: 1;
- collected_items: 6;
- claims: 6;
- findings: 6;
- verification_statuses: DETECTED=6;
- runtime_storage: PROJECT_LOCAL_ONLY.

The failed source was explicitly recorded as GDELT with a TLS handshake timeout. The available Consilium source completed the end-to-end processing path.

## Validation Conclusion

PASS.

M8 is BASELINE_VALIDATED and closes the engineering baseline for ROADMAP Phase 5 - Controlled Pilot Monitoring.

Production/live operational status remains NOT_OPERATIONAL pending a separate Phase 6 operational approval path.
