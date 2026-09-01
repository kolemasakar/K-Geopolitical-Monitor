# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 2.0
Status: APPROVED / ROADMAP_V4_PHASE_12_SYNCHRONIZED

## Source Classes

Baseline classes include:
- Official sources;
- International media;
- Regional/local media;
- Social platforms;
- OSINT;
- Structured data/discovery;
- User-provided information.

Phase 12 may refine class/role metadata through the source-portfolio contract without weakening provenance rules.

## Core Principle

Source quantity does not equal source independence.

Publisher/domain/adapter identity is not automatically the underlying-origin identity.

## Provenance Requirement

Every operational source item must remain traceable, where applicable, to:
- source identity;
- source class/role;
- collection context and attempt;
- raw item identity;
- original/public URL;
- publisher and known/assessed underlying origin;
- translation/derived-representation lineage;
- derived finding/claim/evidence objects.

Derived conclusions remain distinguishable from source evidence.

## Independence Rules

- same-origin duplicate observations do not increase independent corroboration;
- reposts, syndication, translations and citations do not create new independent origins;
- an official source is authoritative for what it states, but that alone does not prove the substantive event claim;
- a discovery/index source does not corroborate a linked claim merely by indexing it;
- source reputation/status changes context/review burden, not truth automatically.

## Validated Starting Live Baseline

The current live public-source baseline contains:
- Consilium press-release RSS — Official sources;
- GDELT DOC 2.0 — Structured discovery/index metadata.

Both are read-only and were validated in controlled live workflows. GDELT metadata is not independent verification of linked publisher claims.

This two-source baseline is intentionally recognized as narrow relative to KGM's intended global scope.

## Phase 12 Source Expansion Rule

Phase 12 is approved to materially expand the public-source network.

Before activation, each new source requires an explicit integration/source record covering identity, role/class, region/language, access mode, cadence/freshness, parser/adapter, provenance/origin characteristics, failure boundary, required egress and approval state.

Additional rules:
- prefer public/free sources first;
- no paid provider is approved by Phase 12 alone;
- local-language gaps remain explicit;
- translation is a derived representation and does not create source independence;
- one source failure must remain isolated from other sources;
- deterministic CI does not depend on live network availability;
- source health/freshness and required egress are measured in P12.5 before network restriction decisions.

P12.1 will formalize the versioned source-portfolio contract. P12.0 does not activate new sources by itself.

## User Data

User-provided information requires reliability assessment and remains identifiable as user-provided/non-public unless independently supported and handled under applicable privacy/data rules.

## Coverage Boundary

Configured source requirements and source availability contribute to coverage measurement only. Source count or coverage confidence cannot strengthen factual verification confidence, and `GLOBAL` does not prove exhaustive world coverage.

## Current State

- source/provenance implementation: `BASELINE_VALIDATED` across the current engineering line;
- controlled live starting source network: `2 integrations / VALIDATED_BASELINE`;
- Phase 12 source-network expansion: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- P12.0: canonical convergence in progress;
- P12.1 source-portfolio contract: not yet implemented;
- new Phase 12 source activations: none created by P12.0;
- paid source providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
