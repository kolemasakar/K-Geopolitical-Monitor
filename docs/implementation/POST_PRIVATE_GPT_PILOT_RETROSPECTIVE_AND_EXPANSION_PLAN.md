# Post-Private-GPT Pilot Retrospective and Expansion Plan

Status: ACTIVE_POST_PILOT_ENGINEERING
Date: 2026-08-27
Last synchronized: 2026-08-29
Project: K-Geopolitical Monitor

This document is an unnumbered post-Phase-11 planning and execution artifact.
It does not create ROADMAP Phase 12 or M14.
Production/live remains NOT_OPERATIONAL.

## 1. Pilot Outcome

Owner-only private GPT matrix:
- 18/18 PASS
- 0 FAIL
- 0 BLOCKED
- 0 critical truth-boundary violations
- 0 hallucinated/untraceable source failures
- 0 source-status visibility failures
- 0 verification-boundary failures
- 0 coverage-boundary failures
- 0 backend-access hallucination failures

Validated user-facing behaviors:
- current geopolitical research;
- local and local-language source search;
- social-post provenance tracing;
- same-origin deduplication;
- conflicting-source handling;
- compromised-source handling;
- official-source limitation handling;
- graph-inference separation;
- forecast/fact separation;
- global-coverage limitation handling;
- backend/persistent-state fail-closed behavior;
- report-presentation truth preservation;
- research reproducibility.

Conclusion:
- analytical GPT behavior is stable enough for continued owner-only use;
- the remaining product limitations include backend connectivity, durable operational deployment, external translation capability, source-reputation persistence and reproducibility instrumentation;
- no evidence supports declaring production readiness.

## 2. Low-Severity Refinements From Testing

Carry forward:
- prefer direct originating government/local sources over relays when available;
- distinguish publisher self-description from independent reputation assessment;
- avoid overstating finality of preliminary agreements/frameworks;
- normalize scenario central probabilities or label ranges as non-additive;
- distinguish social-account role claims from legal/beneficial ownership;
- label numerical forecast probabilities as heuristic unless calibration exists;
- prefer exact social-message URLs/message IDs and retrieval timestamps;
- distinguish exact logged search queries from reconstructed query equivalents.

These are improvements, not pilot-blocking defects.

## 3. Expansion Principles

All post-pilot work must preserve:
- runtime storage: PROJECT_LOCAL_ONLY;
- no shared runtime DB;
- no implicit mixed storage;
- no translation-based source independence;
- no graph-based source independence;
- no forecast-to-fact promotion;
- no coverage-to-verification promotion;
- no report-presentation truth inflation;
- no public-web substitution for persisted backend state;
- no external provider activation without explicit approval.

## 4. Expansion Workstream Priority

### E1 - Automatic Translation Foundation - BASELINE VALIDATED

Priority: P0
State: BASELINE_VALIDATED
External translation provider: NONE_APPROVED

Goal achieved:
- add durable provider-neutral translation handling while preserving original-language provenance and source-independence rules.

Implemented:
- migration 018 raw_item_translations;
- separately persisted original and translated text;
- source/target language metadata;
- translation method/provider/version metadata;
- versioned retranslation history;
- statuses SUCCESS, FAILED, UNAVAILABLE, UNSUPPORTED and AMBIGUOUS;
- explicit uncertainty and failure state;
- inherited underlying origin identity;
- provider-neutral TranslationAdapter contract;
- local deterministic validation adapter;
- restart-persistent translation history.

Truth/isolation rules validated:
- translated copy keeps the same underlying origin;
- translation does not increase independent-source count;
- original raw item is not rewritten;
- M8 verification state is unchanged by translation;
- no external provider was activated.

Canonical implementation record:
- docs/implementation/E1_AUTOMATIC_TRANSLATION_FOUNDATION.md

Canonical code regression:
- GitHub Actions run 33244484173;
- job 99079456390;
- 241 passed in 37.10s;
- result SUCCESS.

E1 gate:
- E1_AUTOMATIC_TRANSLATION_FOUNDATION_BASELINE_PASS.

### E2 - Source Reputation and Status History

Priority: P0
State: APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION

Current schema limitation:
- sources currently contain only id, name, source_class, reliability.

Required additive model:
- source reputation history;
- source status history;
- reason/evidence for status changes;
- review timestamps;
- policy/version used for assessment;
- reversible restoration state.

Target statuses:
- ACTIVE
- WATCH
- COMPROMISED
- RESTRICTED
- SUSPENDED
- RESTORED
- RETIRED

Truth rule:
- COMPROMISED affects verification burden but is not an automatic FALSE operator;
- compromised sources may remain useful as evidence of claim, narrative or information operation;
- reputation restoration requires reviewable evidence and must preserve history.

### E3 - Private GPT Backend Action API

Priority: P0
State: APPROVED_FOR_DESIGN

Pilot evidence:
- GPT-12 and GPT-13 correctly failed closed because no Action/API was connected;
- this is correct behavior but a major functional limitation for persisted monitoring state.

Goal:
- allow the private GPT to read actual K-Geopolitical Monitor persisted state without hallucination or web substitution.

Initial API scope should be read-only:
- recent alerts;
- alert details;
- active monitoring watches;
- monitoring runs;
- source collection attempts;
- unavailable/stale source state;
- coverage_ratio;
- coverage_confidence;
- last unattended cycle timestamp.

Architecture:
- FastAPI or equivalent project-local API layer;
- explicit OpenAPI schema;
- authenticated owner-only access;
- HTTPS required before GPT Action connection;
- SQLite remains under project root data/;
- no direct database exposure;
- no public write endpoints in initial Action scope.

Fail-closed rule:
- unavailable backend -> explicit unavailable state;
- never substitute fresh web search for persisted runtime state.

### E4 - Free Unattended Runtime Deployment

Priority: P0
State: APPROVED_FOR_VALIDATION

Primary target:
- Oracle OCI Always Free A1, subject to current account/capacity availability.

Fallback:
- Google Cloud e2-micro if Oracle capacity/account path is unavailable.

Required validation before deployment claim:
- ARM64 compatibility test;
- Python/runtime dependency compatibility;
- systemd service start/restart;
- reboot recovery;
- missed-watch recovery;
- source failure/retry persistence;
- PROJECT_LOCAL_ONLY path policy;
- SQLite restart persistence;
- no open database ports.

Initial network policy:
- SSH restricted where practical;
- HTTP/HTTPS closed until API/dashboard gate;
- database ports closed;
- outbound HTTPS only for approved adapters.

### E5 - Admin Read-Only Dashboard

Priority: P1
State: PLANNED

Initial dashboard must be owner/admin only and read-only.

Panels:
- system uptime / last cycle / current errors;
- watches due/running/failed;
- source states ACTIVE/WATCH/COMPROMISED/unavailable;
- coverage ratio/confidence and GAP/STALE/UNKNOWN;
- findings/alerts/forecasts;
- recent source collection attempts.

Preferred initial exposure:
- localhost or protected endpoint;
- no public unauthenticated dashboard.

### E6 - Reproducibility Instrumentation

Priority: P1
State: PLANNED

Pilot finding:
- GPT-18 was reproducible, but social feed URLs and reconstructed search queries remain weaker than durable machine-captured audit records.

Additive metadata to evaluate:
- exact source URL/message ID;
- retrieval timestamp;
- content hash where legally/operationally appropriate;
- exact query log for backend-run searches;
- adapter identity/version;
- origin ID;
- duplicate/syndication classification;
- research cut-off;
- claim-to-evidence references.

Rule:
- never fabricate browser/search history that was not instrumented.

### E7 - Forecast Probability Semantics

Priority: P1
State: PLANNED

Pilot finding:
- forecast separation was correct, but numerical ranges can look more calibrated than they are.

Required improvement:
- label probabilities HEURISTIC unless a calibrated method exists;
- central scenario values should sum to 100 percent when mutually exclusive;
- uncertainty bands may overlap only when explicitly labeled non-additive;
- forecast confidence remains separate from factual verification confidence.

### E8 - Controlled External Sharing / Public GPT

Priority: DEFERRED
State: NOT_APPROVED

No action until:
- owner-only post-pilot expansion is stable;
- current OpenAI sharing/publication eligibility is rechecked;
- a paid eligible workspace/account is justified and approved;
- backend Action authentication/privacy requirements are satisfied;
- controlled external cohort is approved.

Public GPT Store exposure remains deferred.

### E9 - Shared Production Runtime

Priority: DEFERRED
State: NOT_APPROVED

No shared/mixed production runtime before:
- successful unattended deployment tests;
- explicit storage/isolation architecture approval;
- explicit launch gate approval.

## 5. Recommended Execution Order

Execution sequence:
- E1 automatic translation foundation - BASELINE_VALIDATED;
- E2 source reputation/status history - CURRENT;
- E3 read-only backend Action API;
- E4 free unattended deployment validation;
- E5 admin dashboard;
- E6 reproducibility instrumentation;
- E7 forecast probability semantics;
- E8 controlled external sharing only after separate approval;
- E9 shared production runtime only after separate approval.

E1-E7 are post-pilot engineering/planning workstreams, not a new numbered ROADMAP phase.

## 6. Launch Gate Remains Closed

Current state:
- analytical baseline through Phase 11: BASELINE_VALIDATED;
- private GPT owner-only pilot: SUCCESSFUL;
- E1 Automatic Translation Foundation: BASELINE_VALIDATED;
- runtime storage: PROJECT_LOCAL_ONLY;
- private GPT backend Action/API: NOT_CONNECTED;
- unattended cloud runtime: NOT_DEPLOYED;
- public sharing: DEFERRED;
- external delivery/publishing: NOT_APPROVED;
- external translation provider: NONE_APPROVED;
- shared production runtime: NOT_APPROVED;
- production/live: NOT_OPERATIONAL;
- next ROADMAP phase: NOT_APPROVED.

The next engineering action is E2 Source Reputation and Status History design and local implementation while preserving all existing truth and storage invariants.
