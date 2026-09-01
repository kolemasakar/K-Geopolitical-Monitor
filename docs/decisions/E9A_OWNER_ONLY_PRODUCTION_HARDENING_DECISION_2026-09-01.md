# E9A Owner-Only Production Runtime Hardening Decision

Status: APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION
Date: 2026-09-01
Project: K-Geopolitical Monitor
Decision scope: unnumbered post-Phase-11 owner-only engineering workstream

## Owner Direction

On 2026-09-01 the owner directed that ChatGPT Business migration and any broader/public publication or sharing be skipped until a separate explicit request, while internal project engineering continues.

Accordingly:
- ChatGPT Business migration: USER_DEFERRED_UNTIL_SEPARATE_REQUEST;
- GPT public/broader sharing: USER_DEFERRED_UNTIL_SEPARATE_REQUEST;
- E8 Controlled External Sharing / Public GPT: DEFERRED;
- E9 Shared Production Runtime: NOT_APPROVED;
- next internal engineering workstream: E9A Owner-Only Production Runtime Hardening.

This decision does not create ROADMAP Phase 12 or M14.

## Approved E9A Scope

E9A may design, implement and validate owner-only runtime hardening around the already validated OCI unattended runtime while preserving one K-Geopolitical Monitor canonical project-local store.

Approved engineering scope:
- single-instance/single-writer runtime lease and duplicate-supervisor fail-closed behavior;
- explicit SQLite durability/concurrency profile and validation;
- backup, restore and disaster-recovery hardening;
- owner-only runtime heartbeat/health/observability instrumentation;
- deployment and secret/logging hardening;
- x64, native ARM64 and real-host validation;
- controlled soak/reboot/recovery evidence where practical.

## Mandatory Architecture Boundaries

Throughout E9A:
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- canonical KGM runtime state remains in the K-Geopolitical Monitor project-local data directory;
- no shared runtime database is approved;
- no implicit mixed storage is approved;
- no direct writes to another project's canonical store are approved;
- cross-project data exchange, if later needed, must use an explicitly approved versioned contract/export/API and remain read-only by default;
- no new external provider may be activated without separate approval;
- E3 owner backend Action remains NOT_CONNECTED;
- backend HTTPS remains NOT_DEPLOYED unless separately approved;
- E5 dashboard remains LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED;
- public API/dashboard exposure is not approved;
- public GPT sharing is not approved;
- E9 shared production runtime is not approved.

## Production Boundary

E9A implementation and validation may establish an `OWNER_ONLY_PRODUCTION_CANDIDATE_READY` engineering gate only.

It must not declare:
- production/live OPERATIONAL;
- public service availability;
- shared production runtime;
- broader GPT sharing/publication;
- complete global operational coverage.

A later transition from candidate-ready to production/live requires a separate explicit owner launch decision after E9A validation evidence is complete.

## Existing Security Exception

The existing owner-approved development exception remains unchanged during E9A implementation unless explicitly revised:
- public SSH TCP/22 from `0.0.0.0/0` may remain temporarily enabled during active development;
- broad egress may remain temporarily enabled during active development;
- least-privilege SSH/Bastion/private administration and egress hardening must be revisited as an E9A final-security gate before any production/live launch approval.

## Decision Result

`E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING = APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION`

`E8_PUBLICATION = USER_DEFERRED`

`E9_SHARED_RUNTIME = NOT_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`
