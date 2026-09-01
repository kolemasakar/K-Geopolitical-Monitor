# SECURITY_AND_DATA_POLICY

Version: 0.5
Status: APPROVED / E9A_OWNER_ONLY_CANDIDATE_EVIDENCE_COMPLETE / P12_0_VALIDATED

## Purpose

Define security and data governance principles for K-Geopolitical Monitor.

## Principles

- Data provenance must be preserved.
- Access follows least privilege unless an explicit owner-approved exception is recorded.
- Sensitive user-provided information requires explicit handling rules.
- External data usage must respect applicable restrictions.
- Auditability is required for important analytical and operational outputs.
- Operational/security claims require reproducible evidence.
- Security exceptions remain explicit and do not become production acceptance by wording alone.

## Data / Storage Boundary

Data categories include public information, user-provided information, derived analytical data and operational metadata.

- Runtime storage remains `PROJECT_LOCAL_ONLY`.
- Shared/mixed canonical runtime storage is not approved.
- Cross-project resources are external integrations unless explicitly approved as shared infrastructure.
- One project must not silently mutate another project's canonical data.
- Shared resources require explicit owner, Source of Truth, contract, access mode, failure boundary and lifecycle rule.

## Secret / Logging Policy

- Secrets, tokens, credentials and private keys must not be stored in repository files.
- External credentials must use environment/platform secret storage.
- Local `.env`, SSH/private-key material and runtime databases remain excluded from Git tracking.
- Authorization headers, private keys, environment dumps and secret-bearing URLs/commands must not enter routine logs or validation artifacts.
- Repository keyword scans are supporting evidence only, not proof of exhaustive historical secret absence.

## Owner-Only Runtime Security Baseline

E9A is `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

Validated evidence includes dedicated non-login `kgm`, root-owned deployed code/service definition, service write access limited to `/opt/k-geopolitical-monitor/data`, restrictive file-creation mask, hardened systemd/no service capabilities, no KGM public API/dashboard/database listener, fail-closed project-local storage, second-instance rejection, restart/reboot recovery, interrupted-run recovery, due-watch resumption, clean project-local backup/restore, emergency stop/re-enable recovery, zero detected secret-pattern hits in the validated journal drill, and persistent removal of rpcbind TCP/UDP port 111.

Canonical E9A evidence: `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`.

## Remaining Explicit Security Exceptions

Owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

They are not final least-privilege production networking. Port 111 is not an exception; its removal was validated.

P12.5 must build the actual source/service outbound destination/protocol inventory before any egress allowlist change is proposed. Private-admin/SSH final disposition belongs to later owner operational activation unless separately requested.

## Backup Boundary

The E9A clean-project-root drill validated project-local backup/restore engineering objectives for that drill; it is not an operational SLA. No off-host backup provider is active.

## Public Ingress / Exposure Boundary

- public KGM HTTP/HTTPS/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- backend HTTPS: `NOT_DEPLOYED`;
- private GPT backend Action: `NOT_CONNECTED`;
- Business migration: not activated;
- GPT public sharing: user-deferred;
- shared/team production runtime: not approved;
- production/live: `NOT_OPERATIONAL`.

ROADMAP v4 and Phase 12 do not alter these states.

## External Integration Security

- Prefer public/free read-only sources first.
- Every source/integration requires an explicit record with data classification, access/authentication mode, failure boundary and required egress.
- Credentials are not introduced merely to increase source count.
- Adapter/source/domain identity does not establish evidentiary independence.
- Source failures fail closed and remain visible.
- Deterministic CI must not require live network access.
- No paid provider is approved by Phase 12 alone.

P12.0 activated no new source or credential. P12.1 is `NEXT / NOT_STARTED`.

## External Operator Tools

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me is non-canonical. It may contain public URLs, RSS feeds, public source names/classes and public analytical/navigation resources only. It must not contain credentials, private endpoints, canonical runtime/monitoring state, private findings/alerts, non-public project documents, personal/sensitive information or canonical evidence/provenance/coverage authority.

## Provenance / Analytical Boundary

External-tool availability cannot strengthen verification, provenance independence, coverage confidence or factual confidence. Public-web research cannot substitute for unavailable persisted backend state. Runtime-health data cannot imply unavailable coverage, source health, uptime, verification or production status.

## Current State

- baseline security/data boundaries: `APPROVED`;
- E9A hardening: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- E9A.6 real-host/network evidence: `VALIDATED`;
- P12.0 convergence: `VALIDATED`;
- remaining candidate exceptions: public SSH TCP/22 from `0.0.0.0`; broad outbound egress;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- shared production runtime: `NOT_APPROVED`;
- public API/dashboard: `NOT_APPROVED / NOT_DEPLOYED`;
- next engineering activity: `PHASE_12 / P12.1_SOURCE_PORTFOLIO_CONTRACT_AND_GOVERNANCE / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.
