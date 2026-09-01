# P12.3 — Priority Authoritative Source Pack Result

Date: 2026-09-01
Status: `VALIDATED_WITH_EXPLICIT_DEGRADATION`
Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`
Validation anchor: `038122e44139d6ff23bc5d79bb50a8dee3c38cde`

## Implemented Scope

P12.3 adds a governed public/free authoritative source pack over the validated P12.1 portfolio contract and P12.2 adapter framework:

- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

Existing Consilium RSS remains the prior validated official-source integration and is not duplicated by the pack.

## Deterministic Validation

Validation anchor `038122e44139d6ff23bc5d79bb50a8dee3c38cde`:

- x64 CI run `33527433110`, job `99921745359`: `356 passed, 1 warning / SUCCESS`;
- native ARM64 run `33527433197`, job `99921746285`: native `aarch64`, `356 passed, 1 warning / SUCCESS`, host-bootstrap/unattended/systemd checks PASS.

Deterministic fixtures cover RSS/Atom parsing, pack identity, P12.1 governance, idempotent onboarding, governance-drift fail-closed behavior, source-failure isolation and epistemic isolation.

## Controlled-Live Evidence

First probe on commit `dbeed606db6d07602b0a17d86c30838afd8a4213`:
- run `33527134432`, job `99920724311`;
- `3 SUCCESS / 1 FAILED`, overall `PARTIAL`.

Repeat probe on validation anchor `038122e44139d6ff23bc5d79bb50a8dee3c38cde`:
- run `33527433106`, job `99921745640`;
- checked at `2026-09-01T15:43:14.116668+00:00`;
- European Commission: `SUCCESS`, 1 parsed item;
- European Parliament: `FAILED`, `P12.2 feed payload is not valid XML`;
- GOV.UK: `SUCCESS`, 0 query matches;
- OSCE: `SUCCESS`, 7 parsed items;
- overall: `PARTIAL`, source-failure isolation PASS.

The European Parliament official RSS directory resolves to the configured endpoint, but the unattended runner receives anti-bot HTML instead of RSS XML. The adapter correctly fails closed. The source is retained as the official canonical endpoint and governed as `DEGRADED`; no anti-bot bypass or third-party mirror substitution is authorized.

## Gate Interpretation

P12.3 is validated because the pack contract, governance, adapters, deterministic fixtures, x64/native ARM64 regressions and controlled-live failure-isolation behavior are validated. The gate does not require every external endpoint to be continuously healthy. The explicit degraded state is part of the validated result and must remain visible to P12.5 source-health work.

## Permanent Boundaries

- official publication establishes what the institution published/stated, not automatically the underlying event;
- four publishers are not four independent underlying origins;
- source/domain/adapter/item count is not independent corroboration count;
- parser/acquisition success is operational evidence, not truth promotion;
- a failed endpoint probe does not prove absence of relevant institutional information;
- controlled-live probe success is not continuous uptime or exhaustive coverage evidence.

## Security / Runtime

- public anonymous read-only HTTPS only;
- no credentials introduced;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- public KGM ingress: not approved/deployed;
- production/live operational status: `NOT_OPERATIONAL`.

## Next Gate

`P12.4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

Next engineering activity:
`P12.4_LOCAL_LANGUAGE_AND_MEDIA_DISCOVERY_PACK / NEXT_NOT_STARTED`.
