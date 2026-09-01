# K-Geopolitical Monitor
Global geopolitical monitoring system.

Version: 3.0
Status: ACTIVE

## Purpose

K-Geopolitical Monitor is designed for discovery, verification, analysis, forecasting, reporting and operational coverage assessment of significant geopolitical developments.

## Documentation

- `PROJECT_CONCEPT_FOUNDATION.md` - approved product intent
- `ROADMAP.md` - approved development phases and current unnumbered post-Phase-11 workstreams
- `ARCHITECTURE.md` - approved architecture and truth/storage/security boundaries
- `PROJECT_HISTORY.md` - chronological canonical project record
- `PROJECT_DOCUMENTATION_GOVERNANCE.md` - documentation governance
- `docs/implementation/GPT_PRIVATE_PILOT_RESULT_LOG.md` - closed owner-only GPT pilot evidence
- `docs/implementation/POST_PRIVATE_GPT_PILOT_RETROSPECTIVE_AND_EXPANSION_PLAN.md` - post-pilot workstream plan
- `docs/implementation/E1_AUTOMATIC_TRANSLATION_FOUNDATION.md` - validated E1 translation foundation
- `docs/implementation/E2_SOURCE_REPUTATION_STATUS_HISTORY.md` - validated E2 source reputation/status history
- `docs/implementation/E3_PRIVATE_GPT_BACKEND_ACTION_API.md` - validated E3 owner-only read-only Action API foundation
- `docs/implementation/E4_FREE_UNATTENDED_RUNTIME_VALIDATION.md` - validated E4 unattended runtime deployment evidence
- `docs/implementation/E5_ADMIN_READ_ONLY_DASHBOARD.md` - validated E5 dashboard foundation
- `docs/implementation/E6_REPRODUCIBILITY_INSTRUMENTATION.md` - validated E6 reproducibility instrumentation
- `docs/implementation/E7_FORECAST_PROBABILITY_SEMANTICS.md` - validated E7 forecast semantics
- `docs/implementation/E8_CONTROLLED_EXTERNAL_SHARING_PREFLIGHT.md` - completed E8 architecture/security preflight
- `docs/implementation/E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING_PLAN.md` - completed E9A hardening plan
- `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md` - final E9A.6 validation evidence
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_E9A_RUNTIME_HARDENING_CANDIDATE_READY.md` - current canonical project checkpoint
- `BOOTSTRAP_PACKAGE_2026-08-29_K-GEOPOLITICAL-MONITOR_POST_E7_TRANSITION.md` - historical post-E7 recovery entry point

## Current State

- Product concept: APPROVED
- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- Owner-only private GPT pilot: SUCCESSFUL - 18/18 PASS
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- E2 Source Reputation and Status History: BASELINE_VALIDATED
- E3 Private GPT Backend Action API: BASELINE_VALIDATED
- E4 Free Unattended Runtime Deployment: REAL_HOST_VALIDATED_WITH_OWNER_SECURITY_EXCEPTIONS
- E5 Admin Read-Only Dashboard: BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED
- E6 Reproducibility Instrumentation: BASELINE_VALIDATED
- E7 Forecast Probability Semantics: BASELINE_VALIDATED
- E8 Controlled External Sharing / Public GPT: USER_DEFERRED_UNTIL_SEPARATE_REQUEST
- E9A Owner-Only Production Runtime Hardening: OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE
- E9 Shared Production Runtime: DEFERRED / NOT_APPROVED
- Intended users at current runtime gate: 1 / OWNER_ONLY
- Runtime storage: PROJECT_LOCAL_ONLY
- Production/live: NOT_OPERATIONAL
- Next numbered ROADMAP phase: NONE_APPROVED

## Canonical Validation Evidence

- Phase 11 Global Operational Coverage: 226 passed, run `33000478908`
- Owner-only GPT pilot: 18/18 PASS
- E1: 241 passed, run `33244484173`
- E2: 248 passed, run `33244795277`
- E3: 254 passed, run `33247311921`
- E4 real-host validation: run `33258520620`, SUCCESS
- E5 x64: 282 passed, run `33263584520`; native ARM64 run `33263584515`, SUCCESS
- E6 x64: 290 passed, run `33264133429`; native ARM64 run `33264133407`, SUCCESS
- E7 x64: 294 passed, run `33265984585`; native ARM64 run `33265984622`, SUCCESS
- E9A.6 real OCI state-preserving validation: run `33486944907`, SUCCESS
- E9A.6 rpcbind persistent closure: run `33488954688`, SUCCESS
- E9A final x64 canonical validation: 318 passed, 1 warning, run `33503085538`, SUCCESS
- E9A final native ARM64 canonical validation: 318 passed, 1 warning, run `33503085489`, SUCCESS

## Validated Truth and Coverage Boundaries

- Original publisher/underlying origin is the verification-independence unit.
- Same-origin duplication, syndication, reposting and translation do not create independent corroboration.
- Translated text is a derived representation stored separately from immutable original raw-item text.
- Official-source status does not automatically make the underlying event claim true.
- COMPROMISED source status does not mean IGNORE or automatic FALSE.
- Graph inference is analytical context and does not become source evidence.
- `raw_probability` and `calibrated_probability` are analytical scenario probabilities, not factual or verification confidence.
- `scenario_confidence` is confidence in the scenario assessment, not scenario probability.
- Forecast metrics cannot modify verification state, factual/evidence confidence or independent-origin count.
- Report presentation cannot strengthen upstream evidence or verification state.
- `coverage_ratio` and `coverage_confidence` do not modify geopolitical factual confidence.
- GLOBAL is an explicit scope key and is not proof of universal world completeness.
- Public-web research is not a substitute for persisted backend/runtime state.
- Missing exact tool/search history is never reconstructed and labeled exact.

## Architecture and Runtime State

- Shared infrastructure architecture: HYBRID
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending a new explicit architecture approval
- Controlled live integrations: Consilium RSS and GDELT DOC 2.0
- GDELT is discovery/index metadata only, not independent factual verification
- Owner-only unattended cloud runtime: `DEPLOYED_OWNER_ONLY_REAL_HOST_VALIDATED / OWNER_ONLY_PRODUCTION_CANDIDATE_READY / NOT_PRODUCTION`
- Owner-only read-only backend Action API foundation: VALIDATED
- Backend Action API deployment/HTTPS endpoint: NOT_DEPLOYED
- Private GPT backend Action connection: NOT_CONNECTED
- Admin dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`
- External translation/graph/forecast/reporting/coverage/notification providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Public GPT sharing: USER_DEFERRED_UNTIL_SEPARATE_REQUEST
- Public Action: NOT_APPROVED / NOT_DEPLOYED
- Shared production runtime: NOT_APPROVED
- Production/live operational status: NOT_OPERATIONAL

E9A removed unnecessary `rpcbind` exposure from the host and validated that TCP/UDP port 111 remains absent after physical reboot.

Explicit owner-approved candidate security exceptions remain:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

These remain documented exceptions and are not equivalent to final least-privilege production networking.

## Post-Pilot Workstream

Post-pilot workstreams are unnumbered and do not create ROADMAP Phase 12 or M14.

Execution state:
- E1 Automatic Translation Foundation - BASELINE_VALIDATED
- E2 Source Reputation and Status History - BASELINE_VALIDATED
- E3 Private GPT Backend Action API - BASELINE_VALIDATED
- E4 Free Unattended Runtime Deployment - REAL_HOST_VALIDATED_WITH_OWNER_SECURITY_EXCEPTIONS
- E5 Admin Read-Only Dashboard - BASELINE_VALIDATED / NOT_DEPLOYED
- E6 Reproducibility Instrumentation - BASELINE_VALIDATED
- E7 Forecast Probability Semantics - BASELINE_VALIDATED
- E8 Controlled External Sharing / Public GPT - USER_DEFERRED_UNTIL_SEPARATE_REQUEST
- E9A Owner-Only Production Runtime Hardening - OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE
- E9 Shared Production Runtime - DEFERRED / NOT_APPROVED

Current engineering activity: `NONE_APPROVED_AFTER_E9A_CLOSURE`.

No production launch, Business migration, public sharing, backend public exposure, or E9 shared runtime transition is implied by E9A completion.

Next numbered ROADMAP phase: NONE_APPROVED.
Production/live operational status: NOT_OPERATIONAL.