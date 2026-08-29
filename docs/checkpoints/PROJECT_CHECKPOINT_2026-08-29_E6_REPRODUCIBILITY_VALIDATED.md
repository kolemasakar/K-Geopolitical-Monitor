# Project Checkpoint — E6 Reproducibility Instrumentation Validated

Date: 2026-08-29
Project: K-Geopolitical Monitor
Checkpoint status: `E6_BASELINE_VALIDATED / TRANSITION_READY`

## Canonical engineering state

E6 Reproducibility Instrumentation is complete and validated.

Validated engineering SHA:

`af4444098ff4e1541ddaa2323c0fed723eeb3d65`

No E7 implementation has been started at this checkpoint.

## E6 validated capabilities

- additive migration `020_reproducibility_instrumentation.sql`: PASS;
- project-local `research_audit_runs`: PASS;
- exact query snapshot capture: PASS;
- timezone-aware research cut-off capture: PASS;
- instrumentation version capture: PASS;
- adapter identity/version or inspectable code fingerprint: PASS;
- canonical source-attempt linkage: PASS;
- deterministic SHA-256 persisted-artifact hashing: PASS;
- `KGM_PERSISTED_LIVE_ITEM_V1` hash basis: PASS;
- missing request locator remains `NOT_INSTRUMENTED`: PASS;
- source-collection status is distinct from audit status: PASS;
- explicit provenance annotation only when classification exists: PASS;
- no inferred origin/syndication/repost/translation/citation/duplicate state from URL count: PASS;
- provenance annotation cannot mutate verification state or independent-origin count: PASS;
- uninstrumented collections do not fabricate research history: PASS;
- adapter/source-attempt mismatch fails closed: PASS;
- canonical unattended runtime uses the E6 instrumented collector wrapper: PASS;
- runtime storage remains `PROJECT_LOCAL_ONLY`: PASS.

## Canonical regression

### x64

- workflow run: `33264133429`;
- job: `99131026905`;
- `290 passed, 1 warning in 27.77s`;
- conclusion: SUCCESS.

### native ARM64

- workflow run: `33264133407`;
- job: `99131026851`;
- architecture: `aarch64`;
- `290 passed, 1 warning in 29.53s`;
- bootstrap shell: PASS;
- unattended one-tick smoke: PASS;
- systemd contract: PASS;
- conclusion: SUCCESS.

The warning is the existing Starlette/TestClient deprecation warning and is nonblocking.

## E4/E5 state carried forward

### E4

`BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION`

Owner-approved development exception remains in force:

- public SSH TCP/22 from `0.0.0.0/0` remains open during active development;
- broad egress remains unchanged during active development;
- SSH/Bastion/private-admin and egress least-privilege hardening are deferred to final project security review.

This exception is not a production security approval.

### E5

`BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`

The admin dashboard remains local/protected and has not been publicly deployed.

## Truth and architecture invariants

- publisher != automatically underlying origin;
- same-origin duplication != independent corroboration;
- syndication/repost/translation do not create source independence;
- official-source status != substantive claim truth;
- COMPROMISED != automatic FALSE;
- graph relation/score/degree = analytical context, not independent evidence;
- forecast probability = analytical, not factual confidence;
- report wording cannot strengthen evidence;
- coverage confidence cannot strengthen verification confidence;
- GLOBAL scope != universal completeness;
- absence of evidence != universal absence;
- public web cannot substitute persisted backend state;
- no fabricated backend/database/monitoring state;
- runtime storage remains project-local;
- no shared runtime database;
- no implicit mixed storage;
- no direct cross-project canonical-store mutation;
- controlled live integrations remain Consilium RSS + GDELT DOC 2.0 only;
- GDELT remains discovery/index metadata only;
- no external provider activation without explicit approval.

## Deployment state

- OCI ARM64 owner-only unattended runtime: deployed and real-host validated;
- private GPT backend Action connection: NOT_CONNECTED;
- backend HTTPS deployment: NOT_DEPLOYED;
- admin dashboard deployment: NOT_DEPLOYED;
- public GPT sharing: DEFERRED;
- shared production runtime: NOT_APPROVED;
- production/live operational status: `NOT_OPERATIONAL`.

## Transition boundary

Current completed workstream:

`E6 Reproducibility Instrumentation — BASELINE_VALIDATED`

Deterministic next task:

`E7 Forecast Probability Semantics`

The new session must recover repository state read-only first and start E7 only after repository identity and required documents are verified.

No ROADMAP Phase 12 and no M14 are approved by this checkpoint.