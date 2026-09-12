# P19 Milestone Evidence Automation

Date: 2026-09-11
Status: `PREPARED_OFFLINE / NOT_WIRED_TO_LIVE_SOAK_WORKFLOW`

## Purpose

`scripts/p19_milestone_evidence.py` validates a completed P19 milestone audit and renders the durable evidence record required by `PHASE_19_CLOSURE_PREP_AND_EVIDENCE_RETENTION.md`.

The tool is intentionally offline. It does not query GitHub, connect to Tailscale, access the owner-local VM, alter the baseline, dispatch controls, restart services, or commit evidence automatically.

## Fail-closed inputs

The generator refuses evidence unless all of the following are explicit and valid:

```text
P19_SOAK_AUDIT = PASS
P19_CONTINUITY_STATUS = PASS
MILESTONE_STATUS = PASS
TERMINAL_OBSERVATION_UTC >= BOUNDARY_UTC
CURRENT_MAX_GAP_HOURS <= MAX_ALLOWED_GAP_HOURS
FAILED_CONTROL_COUNT = 0
SERVICE_BEFORE = active
SERVICE_AFTER = active
RUNTIME_DB_READ = denied
ARBITRARY_ROOT_ESCALATION = denied
RESTART_PERFORMED = NO
POST_BASELINE_QUALIFYING_OBSERVATIONS >= 1
DEPLOYED_RUNTIME_SHA = valid 40-char SHA
CANONICAL_REPOSITORY_SHA_AT_CLOSURE = valid 40-char SHA
AUDIT/RUN/JOB/ARTIFACT IDs = explicit positive IDs
CONTROL_RUN_IDS = explicit non-empty set
```

The tool intentionally does **not** require deployed SHA equality with canonical repository SHA because 24h/72h/7d milestone evidence and final P19 runtime-candidate identity are separate gates. Final P19 closure must still resolve runtime candidate identity explicitly.

## Output fields

Generated Markdown contains at least:

```text
ATTEMPT_ID
MILESTONE
BASELINE_UTC
BOUNDARY_UTC
TERMINAL_OBSERVATION_UTC
AUDIT_RUN_ID
AUDIT_JOB_ID
ARTIFACT_ID
QUALIFYING_OBSERVATION_COUNT_AFTER_BASELINE
FAILED_CONTROL_COUNT
MAX_OBSERVED_GAP_HOURS
MAX_ALLOWED_GAP_HOURS
CONTROL_RUN_IDS
DEPLOYED_RUNTIME_SHA
CANONICAL_REPOSITORY_SHA_AT_CLOSURE
SERVICE_BEFORE
SERVICE_AFTER
RUNTIME_DB_READ
ARBITRARY_ROOT_ESCALATION
RESTART_PERFORMED
P19_SOAK_AUDIT
P19_CONTINUITY_STATUS
MILESTONE_RESULT
```

## Intended milestone procedure

After a milestone boundary and a qualifying post-boundary health observation:

1. run the canonical soak gate audit;
2. preserve/download the audit JSON and identify audit run/job/artifact IDs;
3. collect the explicit control run IDs and closure health assertions;
4. run `p19_milestone_evidence.py` locally/offline;
5. review generated Markdown;
6. only after review, commit the accepted durable record under `docs/evidence/` through normal repository process.

No automatic commit or workflow mutation is authorized by this package.

## Example invocation shape

```text
python scripts/p19_milestone_evidence.py \
  --audit-json p19-soak-audit.json \
  --milestone 24h \
  --attempt-id P19_ATTEMPT_2 \
  --audit-run-id <RUN_ID> \
  --audit-job-id <JOB_ID> \
  --artifact-id <ARTIFACT_ID> \
  --failed-control-count 0 \
  --deployed-runtime-sha <DEPLOYED_SHA> \
  --canonical-repository-sha <CANONICAL_SHA> \
  --service-before active \
  --service-after active \
  --runtime-db-read denied \
  --arbitrary-root-escalation denied \
  --restart-performed no \
  --control-run-id <CONTROL_RUN_ID> \
  --output docs/evidence/PHASE_19_24H_REAL_SOAK_EVIDENCE.md
```

The placeholder values above are deliberate; the tool must never fabricate IDs or SHAs.

## Test coverage

`tests/test_p19_milestone_evidence.py` covers:

- valid 24h evidence rendering;
- missing terminal PASS rejection;
- pre-boundary terminal rejection;
- evidence-gap overflow rejection;
- failed-control rejection;
- service-state regression rejection;
- DB security assertion regression rejection;
- restart rejection;
- malformed SHA rejection.

## Current boundary

```text
LIVE_WORKFLOW_WIRING = NO
RUNTIME_MUTATION = NO
BASELINE_MUTATION = NO
CADENCE_MUTATION = NO
TAILSCALE_TRUST_CHANGE = NO
AUTOMATIC_EVIDENCE_COMMIT = NO
```
