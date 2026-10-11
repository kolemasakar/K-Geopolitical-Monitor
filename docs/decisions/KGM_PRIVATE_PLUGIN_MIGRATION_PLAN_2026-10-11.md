# KGM — Private Plugin Migration Plan (Phase 24 parallel track)

Date: 2026-10-11
Status: ACCELERATED_STAGE_GATED / MINIMAL_PREFLIGHT_NEXT; NOT ACTIVATED
Owner request: Plan the optimal migration stage for the existing K-Geopolitical Monitor Custom GPT.

## Rationale and authority

OpenAI's Custom GPT retirement and migration FAQ (checked 2026-10-11): retirement target 2026-12-11; migrated GPT becomes read-only, migration uses latest published GPT version, plugin starts private, GPT Custom Actions are not automatically transferred. Account/workspace migration availability must be verified in-product. A screenshot from the KGM GPT shows a migration warning for 11 December. This is a migration deadline, NOT a KGM production release deadline.

Existing KGM authoritative decision: `docs/decisions/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md` (PLUGIN_FIRST / NO ACTIVATION).

## Phase placement

Introduce a **cross-cutting, parallel migration workstream M24**, starting during P24.0 closeout / early P24.1. It does not replace P24.0–P24.4, change the Phase 23 canonical strategic gate, require production readiness, or activate KGM runtime.

### Accelerated stage-gated migration — owner revision

No calendar target dates or waiting periods are assigned to migration stages. Begin the next stage immediately when its acceptance criteria are satisfied.

1. **M24.0 — MINIMAL PREFLIGHT (immediate):** confirm ownership, latest published GPT version, existing instructions/knowledge/assets and migration capability. Preserve a minimal recoverable snapshot. Do not delay migration for an exhaustive infrastructure audit.
2. **M24.1 — PRIVATE PLUGIN MIGRATION (next):** transfer GPT to a private Plugin immediately after minimal preflight. Use the platform migration flow if available. If unavailable, record the specific blocker and evaluate the authorized private Plugin Creator path; do not invent a successful migration.
3. **M24.2 — FAST FUNCTIONAL ACCEPTANCE:** run a compact critical test suite on the private Plugin: short world brief; fact vs inference; primary-source provenance; underlying-origin independence; conflicting evidence; localized-source search; three bounded forecast scenarios; no automatic VERIFIED. Fix only blocking deviations before cutover.
4. **M24.3 — PRIVATE CUTOVER:** after owner acceptance, set Plugin as primary ChatGPT interface. Preserve legacy reference material and recovery instructions; do not wait for Phase 24 production readiness.

**Critical path:** M24.0 → M24.1 → M24.2 → M24.3, uninterrupted when gates pass. P24.0–P24.4 research/operational engineering continues independently in parallel.

**Not a blocker:** expanding the 11 source-adapter set, implementing unattended operation, production readiness, Sentinel/K-Trader integration, public release, or broad test-suite expansion. These do not delay an instructions-and-reference private Plugin.

**Boundaries:** no production, persistent scheduler, paid/shared runtime or public Plugin activation. The target account must confirm the migration/build option before any successful transfer is claimed.

## Explicit acceptance

- Plugin capability and account ownership confirmed, and imported snapshot corresponds to latest *published* GPT version.
- Core KGM instructions, source hierarchy, provenance, origin independence, fact/inference distinctions and verification restrictions retained.
- Reference documents/version identifiers synchronized; no secrets or owner credentials embedded in reference assets.
- Representative behavior regression passes; material output differences are documented and reviewed.
- Plugin is private and usable in the correct account; installation/access verified. Sharing/public publication stays disabled.
- Any Custom Action/API integration requires independent contract, authentication, permission, privacy, safety and owner approval gates. Missing Actions do not block an instructions-only private plugin pilot.
- No production activation, unattended scheduler, shared K-project runtime, paid providers, HP-OMEN, K-Sentinel or K-Trader integration.

## Recovery / continuity

Do not rely on unexported ChatGPT conversation history as a migration asset. Preserve authoritative KGM repository documents and prompt-based acceptance examples. GPT remains available only according to platform schedule and becomes read-only after migration.

## Dependency

M24.0 inventory begins immediately, in parallel with P24.0 full-suite/CI closure. Full private cutover requires dedicated Plugin validation, NOT P24.4 production readiness.
