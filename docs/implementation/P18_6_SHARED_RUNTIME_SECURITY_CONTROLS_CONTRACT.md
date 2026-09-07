# P18.6 — Shared Runtime Security and Secrets Controls Contract

Status: `IMPLEMENTATION_IN_PROGRESS / VALIDATION_REQUIRED`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Target gate: `P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED`

## 1. Purpose

P18.6 defines provider-neutral shared-runtime security and secrets controls before
any shared datastore, public/shared ingress, provider commitment, migration
`033`, canonical cutover, or shared-runtime activation is allowed.

This contract is implementation evidence only until exact-head validation and
formal closure are complete.

## 2. Preserved Boundaries

P18.6 MUST preserve:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite remains canonical and independently operable;
- mixed/shared canonical runtime: `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- production/live: `NOT_OPERATIONAL`;
- public/shared ingress: `NOT_ACTIVE`;
- canonical factual verification authority: P13.5/P13.6.

No P18.6 contract assertion is evidence that a real shared datastore or network
boundary has already been deployed or externally probed.

## 3. Security Boundary Model

A future shared candidate MUST satisfy all of the following:

- the application/API boundary is HTTPS-only;
- application boundary URLs MUST NOT embed credentials;
- canonical datastore public ingress is forbidden;
- datastore transport encryption is mandatory;
- unrestricted public administrative ingress is forbidden;
- outbound integration targets are explicit allowlist entries and HTTPS-only;
- concrete egress adapters MUST resolve hostnames and re-check every resolved
  address against private, loopback, link-local, multicast and other non-global
  address classes at connection time to prevent DNS rebinding;
- provider-specific firewall, private-network, TLS-certificate and reachability
  evidence is deferred to the P18.8 non-production candidate and P18.9 final
  readiness validation.

P18.6 therefore validates the configuration/security contract, not observed
Internet reachability of infrastructure that does not yet exist.

## 4. Identity, Session and Authorization Hardening

Shared security identity is issuer-scoped:

`issuer + identity_kind + principal_id`

P18.6 introduces issuer-bound adapters around the existing P18.1 membership and
P18.2 RBAC values. This preserves historical owner-local compatibility while
requiring the future shared profile to fail closed when the same subject/service
identifier exists under another issuer.

The shared security profile MUST:

- resolve membership and RBAC through issuer-bound server-side resolvers;
- never accept role/membership authority from request or token role claims;
- keep human/service identities separate;
- preserve owner-only strategic gates;
- bind one authenticated session identifier to stable non-secret credential
  fingerprint evidence and reject rebinding to different credential evidence;
- preserve short-lived/expiry/revocation validation from P18.1;
- treat session/token misuse as a security event.

### P18.5 retry-identity hardening

P18.5 historically binds idempotent mutation replay identity to actor kind and
principal identifier, but not issuer. A federated/shared identity system can
legitimately contain the same subject identifier under different issuers.

P18.6 therefore provides an issuer-aware audited/outbox repository security
wrapper whose retry identity includes the issuer-scoped actor security key.
A retry under another issuer MUST fail with an idempotency conflict even when
the subject identifier, tenant, command and action are otherwise identical.

The P18.5 legacy contract harness remains provider-neutral and non-deployed; the
future shared profile MUST use the P18.6 issuer-aware security boundary.

## 5. Request Threat Controls

### IDOR / broken object authorization

A request object reference MUST carry explicit workspace/project scope and match
the authenticated server-derived `TenantContext`. Object identifiers alone
never establish authority.

### Injection

Shared query/filter contracts MUST be structured and field-allowlisted.
Provider-neutral service contracts MUST NOT accept raw SQL or equivalent raw
backend query expressions from request input.

Concrete datastore adapters remain responsible for parameterized statements and
safe query construction.

### SSRF

Outbound integration URLs MUST:

- use HTTPS;
- contain no embedded credentials;
- use an explicit allowlisted host;
- use the approved HTTPS port;
- reject literal non-global targets;
- be re-resolved/revalidated by the concrete network adapter at connection time.

### CSRF where applicable

Header-bearer APIs are not treated as browser ambient-authority cookie sessions.
If a browser cookie-session model is later selected, P18.6 requires:

- explicit HTTPS origin allowlist;
- CSRF cookie/header token pair;
- constant-time token comparison;
- fail-closed origin/token mismatch.

### Privilege escalation

All privileged operations remain deny-by-default under P18.2 authorization.
Denied privilege-escalation attempts map to security-event audit actions and do
not acquire canonical mutation authority.

## 6. Secrets and Private Surface Controls

Secrets MUST remain outside:

- source code;
- canonical analytical rows;
- public artifacts;
- public/non-sensitive navigation surfaces;
- ordinary logs;
- exports unless an explicitly private encrypted contract later requires them.

P18.6 uses opaque `SecretReference` values (`env://` or provider-neutral
`secret_store://`) rather than embedding secret material.

Security/log/public projection contracts MUST recursively redact:

- authorization values;
- passwords;
- tokens;
- API keys;
- private keys;
- cookies;
- credential fields;
- explicitly registered runtime secret values.

A separate fail-closed surface validator rejects secret-bearing structures before
canonical analytical, public, export or backup metadata surfaces. Actual backup
encryption/restore is P18.7.

## 7. Rate and Resource Abuse Controls

The shared security contract includes:

- maximum request byte size;
- maximum page size;
- deterministic per-workspace/project request windows;
- independent tenant accounting so one tenant cannot consume another tenant's
  contract quota.

Production-grade distributed rate limiting is a later deployment concern; P18.6
validates semantics and tenant scoping only.

## 8. Security-Event Audit Mapping

P18.6 maps at minimum:

- authentication failure;
- session misuse;
- IDOR denial;
- injection denial;
- SSRF denial;
- CSRF denial;
- privilege-escalation denial;
- tenant resource-limit denial;
- blocked secret exposure.

Security event records are append-only from the contract-harness perspective,
tenant scoped, issuer-aware when an actor exists, recursively redacted, and
explicitly:

`factual_verification_authority = false`

Security/audit state never promotes P13.5/P13.6 factual verification.

## 9. Threat-Control Evidence Matrix

| Threat/control | P18.6 evidence |
| --- | --- |
| HTTP/shared ingress downgrade | policy rejects non-HTTPS application boundary |
| Public datastore exposure | policy rejects `datastore_public_ingress=True` |
| Unencrypted datastore transport | policy rejects TLS-disabled datastore contract |
| Public admin ingress | policy rejects unrestricted public admin boundary |
| Cross-issuer identity collision | issuer-bound membership/RBAC negative tests |
| Session credential rebinding | session binding guard negative test |
| Cross-tenant IDOR | tenant-object reference negative test |
| Raw query/injection | structured-query allowlist negative tests |
| SSRF/local metadata access | HTTPS/host/IP/port negative tests |
| Cookie-session CSRF | origin + token-pair negative tests |
| Privilege escalation | deny-by-default RBAC + mapped security audit event |
| Secret leakage | recursive redaction + fail-closed surface tests |
| Tenant resource abuse | per-tenant rate/request/page limits |
| Audit as factual truth | explicit truth-neutral security-event records |
| P18.5 issuer retry collision | issuer-aware retry identity regression |

## 10. Acceptance Interpretation

The P18.6 ROADMAP acceptance is interpreted as follows:

- threat-model control matrix: validated by provider-neutral code/tests;
- “datastore is not publicly reachable”: P18.6 proves the configuration contract
  **forbids** public datastore ingress; observed reachability proof belongs to
  P18.8/P18.9 after an actual non-production candidate exists;
- tenant/private secrets absent from logs/public/non-sensitive surfaces:
  validated by projection/surface contracts and negative tests; provider/log
  sink inspection repeats in P18.8/P18.9;
- privileged operations deny-by-default and auditable: preserved by P18.2 and
  P18.5, extended with P18.6 issuer-aware/security-event controls.

## 11. Validation Requirements

P18.6 MUST NOT be declared `VALIDATED` until:

- targeted P18.6 tests pass;
- full repository regression passes on the implementation head;
- dependency check passes;
- exact implementation/main validation evidence is recorded under the project's
  existing x64/native-ARM64 validation policy;
- owner-local bootstrap/unattended/systemd contracts remain green where required;
- formal closure updates ROADMAP/state only after evidence exists.

Until formal closure:

`P18_6 = IMPLEMENTATION_IN_PROGRESS / VALIDATION_REQUIRED`

and the canonical ROADMAP/state remains at the existing P18.6 readiness gate.
