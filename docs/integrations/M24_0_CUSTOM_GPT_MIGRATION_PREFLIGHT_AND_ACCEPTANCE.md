# M24.0 — Actual GPT Migration Preflight and Acceptance

Status: MINIMAL PREFLIGHT COMPLETED / NATIVE GPT TRANSFER REQUIRES CREATOR UI
Track: accelerated, stage-gated, private only; no date-based waits
Target: Existing **K-Geopolitical Monitor** Custom GPT shown by owner
Authority: `docs/decisions/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md` and `docs/decisions/KGM_PRIVATE_PLUGIN_MIGRATION_PLAN_2026-10-11.md`

## Verified facts

- Existing GPT screenshot shows title `K-Geopolitical Monitor`, author, description, four example prompts and migration notice; it does **not** expose its published instructions, uploaded knowledge assets, actions or GPT ID.
- Existing GitHub KGM project and Phase 24 migration plan are accessible. Repository code/documents are project authority but **not an export of the GPT's latest published configuration**.
- Plugin Creator connection supports **creating an independent private Plugin from an archive**. It does not have a `migrate_custom_gpt` operation or read access to the source GPT's complete published configuration. Thus an independent generated plugin must not be misrepresented as an automatic migration of the source GPT.
- Official platform migration, once visible for creator, uses `My GPTs → Migrate to plugin`; published instructions and knowledge migrate to skill/reference files. Existing GPT becomes read-only after migration. Custom Actions are excluded; sharing and installation are separate operations.
- Existing owned personal plugin inventory in connected Plugin Creator lists KRC-related private plugins but no confirmed KGM migrated Plugin. This inventory may not include workspace-managed or non-owned plugins.

## Immediate required creator action (single UI operation)

Open the owning ChatGPT account: **My GPTs → K-Geopolitical Monitor → Migrate to plugin**. Review and confirm the private migration. If missing, capture the unavailable option or current GPT configuration status; do not create an incomplete substitute silently.

No public listing, publication, sharing or server activation.

## After creation: rapid M24.2 acceptance

1. Confirm target Plugin name, backend plugin ID, version, release and scope `PRIVATE`.
2. Inspect its skill(s), migrated instructions and reference file inventory; compare against source GPT and repository policies.
3. Test: (a) 24-hour global brief with separate sourced facts vs inference; (b) claim's primary source vs reposts and underlying-origin independence; (c) contradicting official narratives with `UNVERIFIED` preserved; (d) locally-language primary research; (e) 3 scenarios with signals and disconfirming conditions.
4. Fail-closed: missing source data, false verification, fabricated source/availability, leaked credentials, unapproved KGM production calls.
5. Check Custom Actions inventory separately. Missing action parity must be explicitly flagged rather than silently claimed to work; defer Apps/MCP wiring to dedicated approval.
6. Owner accepts private Plugin for chat use only after critical behavioral tests pass; keep project owner-pilot runtime isolated.

## Gate

`M24_0_MINIMAL_PREFLIGHT = PASS_WITH_CREATOR_UI_HANDOFF`.
`M24_1_NATIVE_GPT_MIGRATION = WAITING_FOR_CREATOR_UI`.
`M24_2_PLUGIN_ACCEPTANCE = NOT_STARTED`.
`M24_3_PRIVATE_CUTOVER = NOT_STARTED`.

No assumption of equivalent knowledge or workflows until actual migrated plugin files can be inspected.
