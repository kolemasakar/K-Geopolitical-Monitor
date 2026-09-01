# SECURITY_AND_DATA_POLICY

Version: 0.4
Status: APPROVED / E9A_OWNER_ONLY_CANDIDATE_EVIDENCE_COMPLETE

## Purpose

Define security and data governance principles for K-Geopolitical Monitor.

## Principles

- Data provenance must be preserved.
- Access follows least privilege unless an explicit owner-approved exception is recorded.
- Sensitive user-provided information requires explicit handling rules.
- External data usage must respect applicable restrictions.
- Auditability is required for important analytical and operational outputs.
- Operational/security claims must be supported by reproducible evidence.
- Security exceptions remain explicit and cannot be converted into production acceptance by wording alone.

## Data Categories

- public information;
- user-provided information;
- derived analytical data;
- operational metadata.

## Canonical Storage and Cross-Project Boundary

- Public-source monitoring is the default current data mode.
- Runtime storage remains `PROJECT_LOCAL_ONLY`.
- Shared/mixed canonical runtime storage is not approved.
- Cross-project repositories, stores, indexes, graphs, caches or datasets are external integrations unless explicitly approved as shared infrastructure.
- Shared resources require explicit owner, Source of Truth, data contract, access mode, failure boundary and lifecycle rule.
- One project must not silently mutate another project's canonical data.

## Secret and Logging Policy

- Secrets, tokens, credentials and private keys must not be stored in repository files.
- External credentials must be supplied through environment/platform secret storage.
- Local `.env`, SSH/private-key material and project-local runtime databases remain excluded from Git tracking.
- Authorization headers, private keys, environment dumps and secret-bearing URLs/commands must not be emitted to routine logs or validation artifacts.
- Repository keyword scans are supporting evidence only; they do not prove exhaustive absence of historical, encoded or otherwise undetected secrets.

## Owner-Only Runtime Security Baseline

E9A owner-only runtime hardening is complete at the production-candidate engineering gate.

Validated requirements/evidence include:
- dedicated non-login `kgm` service identity;
- root-owned deployed code and service definition;
- service write access limited to `/opt/k-geopolitical-monitor/data`;
- restrictive runtime file-creation mask;
- systemd least-privilege sandboxing and no service capabilities;
- no KGM public API/dashboard/database listener;
- explicit failure isolation and bounded restart behavior;
- fail-closed project-local runtime storage;
- second-instance lease rejection;
- normal restart and physical reboot recovery;
- interrupted-run recovery and due-watch resumption;
- clean project-local backup/restore drill;
- emergency stop/disable/re-enable recovery;
- journal secret-pattern review with `0` detected hits in the validated real-host drill;
- rpcbind TCP/UDP port 111 removed and closure preserved across physical reboot.

Canonical evidence: `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`.

## Remaining Explicit Security Exceptions

The only retained owner-approved candidate networking exceptions are:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

They are not final least-privilege production networking.

Port 111 is not an exception; its removal was validated after reboot.

Phase 12 P12.5 must build the actual approved source/service outbound destination/protocol inventory before any egress allowlist restriction is proposed. Private-admin/SSH final disposition belongs to the later owner operational activation gate unless separately requested.

## Backup Boundary

The E9A clean-project-root restore drill validated the project-local backup/restore mechanism and engineering RPO/RTO objectives for that drill. Those measurements are not an operational SLA or guarantee.

No off-host backup provider is active. Evaluation of encrypted off-host backup belongs to later owner operationalization unless separately approved.

## Public Ingress / Exposure Boundary

Current state:
- public KGM HTTP/HTTPS/API/dashboard ingress: not approved/not deployed;
- backend HTTPS: not deployed;
- private GPT backend Action connection: not connected;
- Business migration: not activated;
- GPT publication/public sharing: user-deferred;
- shared/team production runtime: not approved;
- production/live: `NOT_OPERATIONAL`.

ROADMAP v4 and Phase 12 do not alter these states.

## External Integration Security

- Prefer public/free read-only sources first.
- Every new external source/integration requires an explicit record with data classification, access mode, authentication, failure boundary and required egress.
- Credentials must not be introduced merely to increase source count.
- Adapter/source/domain identity does not establish evidentiary independence.
- Source failures fail closed and remain visible.
- Deterministic CI must not require live network access.
- No paid provider is approved by Phase 12 alone.

## External Operator Tools

External navigation/operator tools are non-canonical unless a separate architecture decision says otherwise.

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Permitted Start.me content is limited to public, non-sensitive navigation material such as public URLs, RSS feeds, source names/classes and public analytical resources.

Start.me must not hold:
- credentials, tokens, private keys or passwords;
- private backend endpoints or secret-bearing URLs;
- canonical monitoring/runtime state;
- private findings/alerts or non-public project documents;
- personal or other sensitive information;
- canonical evidence, provenance or coverage authority.

## Provenance and Analytical Boundaries

- Provenance retains enough information to identify source/origin and collection context.
- Derived conclusions remain distinguishable from source evidence.
- External-tool availability cannot strengthen verification, provenance independence, coverage confidence or factual confidence.
- Public-web research cannot substitute for unavailable persisted backend state.
- Runtime-health data cannot imply unavailable coverage, source health, uptime, verification or production status.

## Current State

- Baseline security/data boundaries: `APPROVED`;
- E9A owner-only deployment/security hardening: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- E9A.6 real-host/network candidate evidence: `VALIDATED`;
- remaining owner-approved candidate exceptions: public SSH TCP/22 from `0.0.0.0/0`; broad outbound egress;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- shared production runtime: `NOT_APPROVED`;
- public API/dashboard: `NOT_APPROVED / NOT_DEPLOYED`;
- current engineering activity: `PHASE_12 / P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`;
- production/live: `NOT_OPERATIONAL`.
