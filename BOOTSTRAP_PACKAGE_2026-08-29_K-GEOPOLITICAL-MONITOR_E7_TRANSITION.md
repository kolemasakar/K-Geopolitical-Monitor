# BOOTSTRAP PACKAGE — K-GEOPOLITICAL MONITOR — E7 TRANSITION

## Recommended Filename

`BOOTSTRAP_PACKAGE_2026-08-29_K-GEOPOLITICAL-MONITOR_E7_TRANSITION.md`

## Recovery Instructions

Recovery Instructions

This Bootstrap Package shall be processed as follows.

1. Read the entire Bootstrap Package.

2. Treat this Bootstrap Package as the authoritative entry point for project recovery.

3. Do not reconstruct previous chat history.

4. Do not make architectural assumptions.

5. Inspect the Repository and Repository Access sections.

6. Check whether the required repository connector, repository tool or repository workspace is available in the current AI session.

7. If repository access is available:

   - locate the repository specified in the Bootstrap Package;
   - verify the repository provider;
   - verify the repository owner;
   - verify the repository name;
   - verify the repository full name;
   - verify the default branch or active recovery branch;
   - stop repository recovery if the repository identity does not match the Bootstrap Package;
   - inform the user that repository access was found;
   - inform the user which repository and branch were verified;
   - read only the Required Repository Documents directly from the repository;
   - inform the user exactly which Required Repository Documents were successfully read;
   - do not ask the user to upload repository documents that were successfully read.

8. If repository access is unavailable, denied, incomplete, or the repository cannot be identified:

   - inform the user of the specific limitation;
   - request only the minimum action required to restore repository access;
   - request file uploads only as a fallback.

9. Treat the repository as the Single Source of Truth.

10. Recover only the engineering context required for the Next Task.

11. Recovery shall be read-only.

12. Do not create, update, delete, commit, push, merge, branch or otherwise modify repository contents during recovery unless the user explicitly authorizes a write operation.

13. After reading the Required Repository Documents, report:

   - repository access status;
   - verified repository identity;
   - verified branch;
   - documents successfully read;
   - documents unavailable, if any;
   - repository verification result;
   - recovery completion status.

14. Continue engineering work from the Next Task only after repository verification is complete.

## Project

K-Geopolitical Monitor

## Current Phase

E6 Reproducibility Instrumentation — COMPLETE / BASELINE_VALIDATED

## Current Objective

Recover the validated post-E6 engineering baseline deterministically, preserve all truth/storage/security boundaries, and begin E7 Forecast Probability Semantics only after read-only repository verification is complete.

## Repository

- Provider: GitHub
- Owner: `kolemasakar`
- Repository: `K-Geopolitical-Monitor`
- Repository Full Name: `kolemasakar/K-Geopolitical-Monitor`
- Default Branch: `main`
- Repository URL: `https://github.com/kolemasakar/K-Geopolitical-Monitor`

## Repository Access

- Access Method: GitHub repository connector/tools in the source session
- Source Session Verification Status: VERIFIED in this source session by successful repository reads and writes
- Read Capability: VERIFIED in this source session
- Write Capability: VERIFIED in this source session
- Notes: Access must be re-checked in the new session. Do not assume the source-session connector state persists. No credentials, tokens, private keys or secret values are included in this package. Recovery must remain read-only until repository identity and required documents are verified.

## Current Status

- E6 canonical engineering baseline is validated at SHA `af4444098ff4e1541ddaa2323c0fed723eeb3d65`.
- ROADMAP v2.7 records E6 as `BASELINE_VALIDATED` and E7 as `NEXT`; E7 implementation has not started.
- Runtime storage remains `PROJECT_LOCAL_ONLY`; shared/mixed runtime storage remains blocked pending explicit architecture approval.
- OCI owner-only ARM64 unattended runtime remains real-host validated but `NOT_PRODUCTION`.
- Production/live operational status remains `NOT_OPERATIONAL`; backend HTTPS, private GPT Action connection and admin dashboard deployment remain not deployed/not connected.
- Owner-approved development security exception remains active: public SSH TCP/22 from `0.0.0.0/0` and broad egress remain temporarily unchanged until final project security hardening.

## Completed Work

- ROADMAP Phases 0-11 engineering baseline validated; no ROADMAP Phase 12 and no M14 approved.
- Owner-only private GPT pilot completed successfully: 18/18 PASS with truth/coverage/backend-access boundaries preserved.
- E1 Automatic Translation Foundation: `BASELINE_VALIDATED`.
- E2 Source Reputation and Status History: `BASELINE_VALIDATED`.
- E3 Private GPT Backend Action API local read-only foundation: `BASELINE_VALIDATED`; GPT Action remains `NOT_CONNECTED`, HTTPS backend remains `NOT_DEPLOYED`.
- E4 Free Unattended Runtime Deployment: `BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION`; real OCI Ubuntu 24.04 ARM64 reboot/recovery/live collection validation succeeded.
- E5 Admin Read-Only Dashboard: `BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`.
- E6 Reproducibility Instrumentation: `BASELINE_VALIDATED`.
- E6 migration `020_reproducibility_instrumentation.sql` adds additive project-local research audit, query execution, artifact hash and explicit provenance-annotation projections without creating a parallel truth store.
- E6 exact query snapshot, timezone-aware research cut-off, instrumentation version, adapter identity/version fingerprint and canonical source-attempt linkage are persisted for instrumented live collections.
- E6 deterministic SHA-256 hashing covers the persisted parsed live artifact using hash basis `KGM_PERSISTED_LIVE_ITEM_V1`; it does not claim preservation of unretained raw remote HTTP bytes.
- Missing request locators remain explicitly `NOT_INSTRUMENTED`; unavailable browser/search history is not reconstructed.
- E6 keeps audit status separate from source collection status; a failed collection may still have successfully captured audit metadata.
- Provenance classes are written only when explicitly classified with evidence/basis; URL/domain counts do not fabricate origin, syndication, repost, translation, citation or duplicate state.
- Reproducibility annotations do not change verification status, confidence or independent-origin count.
- Uninstrumented collections do not fabricate historical research audit records.
- Instrumentation finalization fails closed on adapter/source-attempt mismatch.
- Canonical unattended runtime now uses `ReproducibilityInstrumentedCollector` around the existing live collector while canonical provenance/analysis/findings/coverage remain in their existing stores.
- E6 x64 validation: workflow run `33264133429`, job `99131026905`, `290 passed, 1 warning in 27.77s`, SUCCESS.
- E6 native ARM64 validation: workflow run `33264133407`, job `99131026851`, architecture `aarch64`, `290 passed, 1 warning in 29.53s`, bootstrap-shell/one-tick smoke/systemd contract PASS, SUCCESS.
- E6 implementation record created: `docs/implementation/E6_REPRODUCIBILITY_INSTRUMENTATION.md`.
- E6 transition checkpoint created: `docs/checkpoints/PROJECT_CHECKPOINT_2026-08-29_E6_REPRODUCIBILITY_VALIDATED.md`.
- ROADMAP updated to version 2.7 with E6 validated and E7 designated as the deterministic next workstream.

Truth and architecture boundaries already established and still mandatory:

- publisher is not automatically the underlying origin;
- same-origin duplication is not independent corroboration;
- syndication/repost/translation do not create source independence;
- official-source status does not make the substantive claim automatically VERIFIED;
- COMPROMISED does not mean automatic FALSE or IGNORE;
- graph relations/scores/degrees are analytical context, not independent evidence;
- forecast probability is analytical and must not be presented as factual confidence;
- report wording cannot strengthen evidence;
- coverage confidence cannot strengthen verification confidence;
- GLOBAL scope does not prove universal completeness;
- absence of evidence does not prove universal absence;
- public web cannot substitute persisted backend state;
- backend/database/monitoring state must never be fabricated;
- no shared runtime database or implicit mixed storage;
- no external provider activation without explicit approval;
- controlled live integrations remain Consilium RSS and GDELT DOC 2.0 only, with GDELT used as discovery/index metadata rather than independent substantive verification by itself.

## Next Task

Perform the E7 Forecast Probability Semantics delta-audit against the existing M12 forecasting implementation and reporting surfaces, then define the minimum additive changes required to guarantee that forecast/scenario probabilities, calibrated probabilities, factual confidence, verification state and report wording remain semantically separated across persisted state, API/dashboard/report outputs and tests.

Do not implement E7 until repository recovery and verification are complete.

## Required Repository Documents

- `ROADMAP.md`
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-08-29_E6_REPRODUCIBILITY_VALIDATED.md`
- `docs/implementation/E6_REPRODUCIBILITY_INSTRUMENTATION.md`
- `FORECASTING_MODEL.md`
- `docs/implementation/M12_ADVANCED_FORECASTING_AUDIT.md`
- `docs/implementation/M12_ADVANCED_FORECASTING_PLAN.md`
- `docs/implementation/M12_VALIDATION_RESULT.md`
- `src/kgeopolitical_monitor/advanced_forecasting.py`
- `src/kgeopolitical_monitor/forecast_inputs.py`
- `src/kgeopolitical_monitor/forecast_query.py`
- `src/kgeopolitical_monitor/report_forecasts.py`
- `src/kgeopolitical_monitor/report_assembly.py`
- `src/kgeopolitical_monitor/backend_action_api.py`
- `src/kgeopolitical_monitor/admin_dashboard.py`
- `tests/test_advanced_forecasting.py`
- `tests/test_forecast_query.py`
- `tests/test_report_forecasts.py`

## Recovery Status

[ ] Bootstrap Loaded
[ ] Recovery Instructions Processed
[ ] Repository Access Checked
[ ] Repository Identity Verified
[ ] Repository Documents Loaded
[ ] Repository Verification Reported
[ ] Recovery Complete