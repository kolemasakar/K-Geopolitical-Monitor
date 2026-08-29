# E8 Controlled External Sharing / Public GPT — Preflight and Delta Audit

Status: PREFLIGHT_COMPLETE / IMPLEMENTATION_NOT_APPROVED
Date: 2026-08-29
Project: K-Geopolitical Monitor
Workstream: E8 — unnumbered post-Phase-11 expansion
Repository baseline inspected: `e6768062a28670088bfc5bc396bf28d20def8821`

This record completes an architecture/security preflight only. It does not activate external sharing, deploy a backend API, open network ingress, publish a GPT, approve a controlled cohort, or approve E9 shared production runtime.

## 1. Objective

Determine the smallest safe path from the validated owner-only K-Geopolitical Monitor to controlled external use while preserving:
- project-local canonical storage;
- evidence/verification boundaries;
- graph/forecast/coverage/report semantic isolation;
- persisted-state fail-closed behavior;
- owner/admin operational-state confidentiality;
- explicit launch and rollback gates.

## 2. Repository-Derived Current State

Validated foundation:
- owner-only GPT pilot: 18/18 PASS;
- E3 owner-only read-only FastAPI Action API: BASELINE_VALIDATED;
- E4 real OCI ARM64 unattended monitoring host: BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION;
- E5 owner/admin dashboard: BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED;
- E6 reproducibility instrumentation: BASELINE_VALIDATED;
- E7 forecast probability semantics: BASELINE_VALIDATED;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- backend HTTPS: NOT_DEPLOYED;
- GPT Action connection: NOT_CONNECTED;
- public sharing: NOT_ACTIVE;
- production/live: NOT_OPERATIONAL.

Current E4 network state:
- public SSH TCP/22 from `0.0.0.0/0`: owner-approved temporary development exception;
- public TCP 80: absent;
- public TCP 443: absent;
- database/API ingress: absent;
- broad egress remains temporarily allowed by owner decision.

The monitoring systemd unit starts only the unattended monitoring runtime and no API/dashboard listener.

## 3. Current Owner API Exposure Is Not a Public Contract

`src/kgeopolitical_monitor/backend_action_api.py` is an owner-only persisted-state facade. It exposes protected operations for:
- state summary;
- alerts and alert detail;
- active monitoring watches;
- monitoring runs;
- source collection attempts;
- degraded source state;
- coverage snapshots;
- active forecasts.

The data surface includes internal operational metadata such as watch IDs/queries/cadence, run IDs/status/errors/retry state, collection-attempt state and source operational errors. These are useful for owner administration but are not an approved public data contract.

Decision:
**E8 must not make the existing owner Action API or admin dashboard directly public.**

The owner bearer token must never be reused as a controlled-external/public credential.

## 4. Security/Exposure Gaps Confirmed by Audit

The repository currently has no approved public API deployment layer.

Preflight found no implemented contract for:
- public/external endpoint allowlisting and response minimization;
- separate public/service credential;
- rate limiting or abuse throttling;
- reverse-proxy/TLS deployment;
- Trusted Host enforcement for an exposed Action API;
- public API request-size/concurrency controls;
- public privacy-policy artifact/URL;
- external API logging/redaction/retention policy;
- external kill switch/credential-revocation runbook;
- public/cohort data-classification contract.

FastAPI itself is already a dependency, so an E8 public facade does not require a new application framework.

## 5. Current OpenAI Platform Constraints — External Fact, Not KGM State

Official OpenAI help material was rechecked on 2026-08-29.

Current constraints relevant to E8:
- personal ChatGPT accounts, including Free, Go, Plus and Pro, cannot create or publish new GPTs;
- existing GPTs may remain usable/editable subject to current plan/permission rules;
- managed Business/Enterprise/Edu workspace sharing/publishing depends on workspace settings and role permissions;
- if a GPT uses Actions and is shared publicly/published, each public Action requires a valid Privacy Policy URL;
- GPT Actions support None, API Key and OAuth authentication; API Key is the documented server-to-server pattern;
- public builder-profile website use may require a verified domain;
- domain verification does not itself grant a personal account permission to create/publish new GPTs.

Official references:
- https://help.openai.com/en/articles/8798878-sharing-and-publishing-gpts
- https://help.openai.com/en/articles/9442513-configuring-actions-in-gpts
- https://help.openai.com/en/articles/8871611-domain-verification
- https://help.openai.com/en/articles/11325361

Because platform eligibility can change, it must be rechecked again at any actual sharing/publication gate.

## 6. Recommended Two-Stage E8 Architecture

### E8A — Controlled External Cohort Without Persisted-State Action

Preferred first external gate.

Purpose:
- validate user-facing geopolitical research behavior outside the owner-only context;
- exercise truth, provenance, uncertainty, coverage and forecast boundaries under broader prompts;
- avoid exposing OCI/backend state while the external API contract is not yet hardened.

Properties:
- no KGM backend Action connection;
- no OCI 443 ingress change;
- no public API service;
- no database/network exposure;
- current web-research behavior only;
- existing fail-closed rule remains: the GPT must not claim persisted backend access.

Blockers before activation:
- confirm the actual ChatGPT account/workspace offers an allowed external sharing mode for the existing GPT;
- explicit owner approval of the external cohort and sharing mode;
- review public-facing name/description/instructions/conversation starters;
- execute a controlled adversarial external-use test matrix;
- define revocation/rollback procedure.

### E8B — Controlled External Cohort With Sanitized Persisted-State Action

Must be a later, separately approved gate.

Architecture recommendation:
- create a **separate external read-only facade**, not a public mode in the owner/admin API;
- separate credential from owner/admin bearer token;
- bind the application service to loopback/private interface behind a TLS reverse proxy;
- public ingress limited to HTTPS 443 for the external facade only;
- monitoring service, dashboard and database remain non-public;
- use existing project-local read-only/query-only SQLite access;
- no write endpoints.

Candidate public allowlist:
- sanitized recent strategic alerts;
- sanitized active forecast summaries with `KGM_FORECAST_SEMANTICS_V1`;
- sanitized aggregate coverage summaries;
- optionally curated persisted report/brief projections.

Explicit denylist for first E8B version:
- monitoring watch queries/cadence/internal IDs where not required;
- monitoring-run internals and retry/error state;
- source collection attempt internals;
- admin dashboard endpoints;
- direct database access/path details;
- owner-only source operational diagnostics;
- raw internal evidence references unless specifically reviewed for disclosure;
- any state-changing operation.

## 7. Minimum E8B Implementation Delta

If E8B is later approved, minimum engineering delta should include:

1. **External projection contract**
   - versioned schema;
   - explicit allowlisted fields;
   - data classification for every field;
   - no generic pass-through of owner API responses.

2. **Separate FastAPI application**
   - separate module/app factory;
   - separate API version and OpenAPI schema;
   - docs/redoc disabled unless explicitly required;
   - only allowlisted GET operations.

3. **Authentication and secret isolation**
   - dedicated external service credential;
   - owner token rejected/not reused;
   - runtime-only secret injection;
   - rotation/revocation procedure;
   - Authorization secrets excluded from logs/errors.

4. **Exposure controls**
   - HTTPS with valid certificate and domain;
   - trusted host/domain enforcement;
   - request/response size and pagination bounds;
   - timeouts and concurrency limits;
   - rate limiting/abuse controls;
   - explicit method/path allowlist;
   - no dashboard/database/monitoring-service exposure.

5. **Privacy and publication artifacts**
   - valid public Privacy Policy URL for any public Action;
   - data-use/log-retention statement;
   - builder/domain verification if required by the selected ChatGPT publishing path.

6. **Operational isolation**
   - separate systemd service from `kgm-monitor.service`;
   - public service failure must not stop unattended monitoring;
   - read-only `PROJECT_LOCAL_ONLY` DB access only;
   - public API must not create a parallel canonical store.

7. **Kill switch / rollback**
   - revoke external credential;
   - stop/disable external service;
   - close public 443 exposure;
   - remove Action from GPT or return GPT to non-action/private state;
   - monitoring runtime continues independently.

## 8. Required E8B Regression/Security Gates

Before external activation:
- missing/invalid external credential -> fail closed;
- owner/admin token is not exposed and is not the external credential;
- every non-allowlisted endpoint -> unavailable/404;
- response contract contains no watch/run/attempt/admin-only fields;
- GET sweep does not mutate project DB;
- runtime DB remains `PROJECT_LOCAL_ONLY` and query-only;
- public API failure does not stop monitoring service;
- request limits/rate limits are enforced;
- secrets do not appear in logs or responses;
- HTTPS/trusted-host/reverse-proxy contract passes;
- dashboard remains inaccessible from the public facade;
- high forecast probability still cannot promote verification/factual confidence;
- coverage confidence still cannot promote verification confidence;
- source/provenance independence rules remain unchanged;
- no public-web substitution for missing persisted backend state;
- x64 full regression green;
- native ARM64 regression/deployment contract green;
- manual real-host HTTPS/exposure/security-list evidence captured;
- controlled external cohort test matrix passes before any broader publication.

## 9. E8 Approval Gates

Preflight completion does **not** open the implementation gate.

Current gate state:
- `E8_PREFLIGHT = COMPLETE`;
- `E8_IMPLEMENTATION = NOT_APPROVED`;
- `E8_EXTERNAL_SHARING = NOT_ACTIVE`;
- `E8_PUBLIC_BACKEND = NOT_DEPLOYED`;
- `E8_PUBLIC_GPT = NOT_PUBLISHED`;
- `E9_SHARED_PRODUCTION_RUNTIME = NOT_APPROVED`.

Next owner decision should select one of:
- approve E8A controlled external cohort preparation/validation without backend Action;
- approve E8B engineering implementation only (still no external activation until its gates pass);
- keep E8 deferred.

## 10. No E9 Implication

Nothing in E8 preflight approves shared/mixed storage. E9 remains a separate architecture decision because current canonical runtime storage is `PROJECT_LOCAL_ONLY` and shared/mixed runtime truth storage remains blocked.

Preflight result:
`E8_CONTROLLED_EXTERNAL_SHARING_PREFLIGHT = COMPLETE / IMPLEMENTATION_APPROVAL_REQUIRED`
