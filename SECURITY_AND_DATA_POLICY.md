# SECURITY_AND_DATA_POLICY

Version: 0.3
Status: E9A_OWNER_ONLY_CANDIDATE_BASELINE_DEFINED

## Purpose

Define security and data governance principles for K-Geopolitical Monitor.

## Principles

- Data provenance must be preserved.
- Access must follow least privilege.
- Sensitive user-provided information requires explicit handling rules.
- External data usage must respect applicable restrictions.
- Auditability is required for important analytical outputs.
- Operational claims must be supported by reproducible evidence.
- Security exceptions must remain explicit and must not be converted into production acceptance by wording alone.

## Data Categories

- public information
- user-provided information
- derived analytical data
- operational metadata

## Canonical Storage and Integration Boundaries

- Public-source monitoring is the default data mode for the current baseline.
- Runtime storage remains `PROJECT_LOCAL_ONLY`.
- Shared/mixed canonical runtime storage is not approved.
- Cross-project repositories, stores, indexes, graphs, caches or datasets must not be consumed implicitly.
- Any cross-project resource is treated as an external integration until an explicit architecture decision defines it as shared infrastructure.
- Shared resources require an explicit owner, Source of Truth, data contract, access mode, failure boundary and lifecycle rule.
- One project must not silently mutate another project's canonical data.

## Secret and Logging Policy

- Secrets, tokens, credentials and private keys must not be stored in repository files.
- External credentials must be supplied through environment or platform secret storage.
- Local `.env`, SSH/private-key material and project-local runtime databases must remain excluded from Git tracking.
- Authorization headers, private keys, environment dumps and secret-bearing URLs/commands must not be emitted to routine logs or validation artifacts.
- Repository keyword scans are supporting evidence only; they do not prove exhaustive absence of historical, encoded or otherwise undetected secrets.

## Owner-Only Runtime Security Baseline

The E9A owner-only runtime baseline requires:
- dedicated non-login `kgm` service identity;
- root-owned deployed code;
- service write access limited to `/opt/k-geopolitical-monitor/data`;
- restrictive runtime file creation mask;
- systemd least-privilege sandboxing and no service capabilities;
- no monitoring-service public API/dashboard/database listener;
- explicit failure isolation and bounded restart behavior;
- fail-closed project-local runtime storage.

Current development exceptions remain explicit:
- public SSH TCP/22 from `0.0.0.0/0` during active development/real-host validation;
- broad outbound egress during active development.

These exceptions are not final production acceptance. SSH/private-admin alternatives and outbound least privilege remain E9A.6 candidate-gate evidence items.

## External Operator Tools

External operator/navigation tools are non-canonical unless separately approved by architecture decision.

Start.me owner policy:
`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`

Permitted Start.me content is limited to public, non-sensitive navigation material such as public URLs, RSS feeds, source names, classifications and public analytical resources.

Start.me must not hold:
- credentials, tokens, private keys or passwords;
- private backend endpoints or secret-bearing URLs;
- canonical monitoring/runtime state;
- private findings/alerts or non-public project documents;
- personal or other sensitive information.

Start.me must not become a KGM evidence store, provenance store, runtime dependency, canonical source registry or coverage authority.

## Provenance and Analytical Boundaries

- Provenance must retain enough information to identify the originating source and collection context.
- Derived conclusions must remain distinguishable from source evidence.
- External operator-tool availability cannot strengthen verification, provenance independence, coverage confidence or factual confidence.
- Public-web research must not substitute for unavailable persisted backend state.

## Current State

Baseline boundaries: DOCUMENTED
E9A owner-only deployment/security baseline: DEFINED
E9A.5 implementation/regression validation: IN_PROGRESS
Real-host/network candidate evidence: PENDING_E9A_6
Shared production runtime: NOT_APPROVED
Public API/dashboard: NOT_APPROVED / NOT_DEPLOYED
Production/live: NOT_OPERATIONAL
