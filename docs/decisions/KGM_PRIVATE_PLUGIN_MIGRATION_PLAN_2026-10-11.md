# KGM — Private Plugin Migration Plan (Phase 24 parallel track)

Date: 2026-10-11
Status: PLANNED; NOT ACTIVATED
Owner request: Plan the optimal migration stage for the existing K-Geopolitical Monitor Custom GPT.

## Rationale and authority

OpenAI's Custom GPT retirement and migration FAQ (checked 2026-10-11): retirement target 2026-12-11; migrated GPT becomes read-only, migration uses latest published GPT version, plugin starts private, GPT Custom Actions are not automatically transferred. Account/workspace migration availability must be verified in-product. A screenshot from the KGM GPT shows a migration warning for 11 December. This is a migration deadline, NOT a KGM production release deadline.

Existing KGM authoritative decision: `docs/decisions/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md` (PLUGIN_FIRST / NO ACTIVATION).

## Phase placement

Introduce a **cross-cutting, parallel migration workstream M24**, starting during P24.0 closeout / early P24.1. It does not replace P24.0–P24.4, change the Phase 23 canonical strategic gate, require production readiness, or activate KGM runtime.

### Proposed owner migration milestones

| Window (2026) | Gate | Deliverable |
|---|---|---|
| Oct 11–20 | M24.0 PREPARE | Inventory current GPT latest published instructions, knowledge, reference files, starters, Actions and permissions; snapshot versioned resources outside GPT; baseline user prompt suite; confirm in-account migration option. |
| Oct 20–31 | M24.1 PRIVATE MIGRATION | Use official `My GPTs → Migrate to plugin` flow when available; review skill/instructions and imported assets; keep private. If option unavailable, record a migration-capability blocker and use authorized Plugin Creator build path only after separate scope review. |
| Nov 1–15 | M24.2 PARALLEL VALIDATION | Compare legacy GPT with private Plugin on geopolitics brief, source provenance, independence, disputed claims, local-language sourcing, three-scenario forecasting, uncertainty, and no false VERIFIED; record deviations. Backend integrations (Apps/MCP) remain optional and separately approved. |
| Nov 16–30 | M24.3 PRIVATE CUTOVER | Owner signs off equivalent workflow quality; make private Plugin primary interface, preserve versioned fallback procedures and transition docs. No public publication required. |
| By Dec 11 | DEADLINE SAFETY | Confirm private Plugin access and usability ahead of standard GPT retirement; do not rely on old GPT remaining accessible after retirement. |

Windows are target planning dates (not guaranteed provider feature availability). Escalate blockers no later than early November to preserve a testing buffer.

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
