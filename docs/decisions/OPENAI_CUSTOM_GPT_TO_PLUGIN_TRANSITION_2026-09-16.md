# KGM — OpenAI Custom GPT → Plugin transition decision

Date: 2026-09-16  
Status: **PLUGIN-FIRST ARCHITECTURE REBASE / NO ACTIVATION**

## Context

OpenAI has announced retirement of Custom GPTs across ChatGPT plans and a migration path toward Plugins. KGM currently retains GPT-facing publication/integration concepts in historical documentation (`private GPT backend Action`, public-sharing boundary, controlled publication readiness), but these are not activated production capabilities.

The source analysis in `kolemasakar/AI_general/docs/openai-custom-gpts-retirement-to-plugins-2026-09-16.md` was revalidated against the current OpenAI Help Center on 2026-09-16.

Confirmed platform facts relevant to KGM:

- Plugins combine reusable skills/instructions with apps/integrations;
- the transition affects ChatGPT plans, while detailed migration timing and permissions may vary by account/workspace;
- Custom GPT migration is not a guaranteed 1:1 clone;
- GPT instructions are expected to become a Plugin skill under the migration flow;
- Custom Actions do not transfer automatically and must be separately rebuilt/revalidated through a supported connector or custom MCP integration where needed;
- selected-model configuration does not transfer as a durable application contract;
- conversation starters and previous chats are not guaranteed migration assets;
- replacement Plugins start private and sharing/access must be explicitly revalidated;
- migrated GPTs become read-only before retirement; therefore the long-lived maintainable artifact is the Plugin/workflow layer, not the legacy GPT wrapper.

Enterprise dates described by OpenAI are treated as target/planned milestones rather than universal KGM deadlines. KGM must follow the actual capability/notice state of the account/workspace used at launch time.

## Decision

```text
PRIMARY_CHATGPT_SURFACE = PLUGIN
LEGACY_GPT_SURFACE = TRANSITIONAL_ONLY
PUBLIC_GPT_ACTION = LEGACY_INTEGRATION_CONCEPT
CUSTOM_ACTION_AS_LONG_TERM_ARCHITECTURE = NO
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
```

Any future ChatGPT-facing KGM product must be designed around:

- KGM workflow / policy as Plugin skill(s);
- reference assets as explicit versioned resources rather than GPT-only knowledge state;
- external data/actions through supported App / Connector / custom MCP integration as appropriate;
- existing KGM backend/runtime APIs only where they satisfy the selected integration contract;
- permissions, account authorization and sharing as explicit launch-time gates;
- regression and truth-governance invariants preserved independently of the UI/deployment wrapper;
- model-agnostic workflow contracts: no canonical KGM behavior may depend on one selected ChatGPT model being permanently attached to the product.

## Mapping of existing KGM concepts

```text
KGM instructions / operational workflow
-> Plugin skill/workflow

reference files / examples / templates
-> versioned Plugin reference assets, regression-checked

private GPT backend Action concept
-> App / Connector / custom MCP integration candidate

controlled external publication readiness
-> Plugin sharing/publication readiness, separately capability- and owner-gated

truth / provenance / contradiction / forecast policies
-> unchanged domain invariants
```

## Phase 17 capability rebase

The historical Phase 17 decision `PHASE_17_EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY` remains valid evidence for the legacy publication surface that existed when Phase 17 closed, but it must not be projected unchanged onto Plugins.

The current forward-looking capability state is therefore:

```text
LEGACY_PHASE17_PUBLICATION_CAPABILITY = HISTORICAL_UNAVAILABLE
PLUGIN_DIRECTORY_GENERAL_AVAILABILITY = PLATFORM_DEPENDENT
PLUGIN_BUILD_OR_UPLOAD_CAPABILITY = NOT_YET_VALIDATED_FOR_KGM_ACCOUNT_WORKSPACE
PLUGIN_SHARING_PUBLICATION_CAPABILITY = NOT_YET_VALIDATED_FOR_KGM_ACCOUNT_WORKSPACE
PHASE_17_PLUGIN_CAPABILITY_REVALIDATION_REQUIRED = YES
PLUGIN_PUBLICATION_ACTIVATION = NO
```

This is deliberately fail-closed. General Plugin availability does not prove that KGM can upload, publish, share or operate the exact Plugin/integration shape it will eventually require.

Phase 17 engineering readiness remains reusable because its eligibility, redaction, release-manifest, provider-neutral delivery and owner-approval concepts are deployment-surface independent. A future Plugin launch must add fresh capability, permission, security, privacy, regression, sharing and rollback validation.

## Phase 21 consequence

Phase 21 remains a source-network/evidence-quality phase and is not converted into a Plugin implementation phase.

However:

- P21 source/evidence contracts must remain deployment-wrapper independent;
- any future ChatGPT-facing access to KGM source data must use Plugin-compatible integration rather than new Custom Action investment;
- P21.6 intelligence-quality regression artifacts should be reusable later as Plugin skill/reference/integration regression cases;
- no source may receive trust, independence or verification credit because it is surfaced through a Plugin/App/Connector/MCP integration.

## Non-effects

This decision does **not**:

- activate Phase 17 publication;
- activate any public GPT or Plugin;
- start Plugin implementation;
- change Phase 18 shared-runtime state;
- create migration `033`;
- approve paid providers;
- change `PROJECT_LOCAL_ONLY` storage;
- change truth/provenance semantics;
- create public API/dashboard ingress;
- authorize production/live launch.

## Implementation direction

1. Preserve historical GPT/publication documentation for audit continuity.
2. Treat future GPT-specific work as legacy transition maintenance only.
3. Store workflow logic, reference assets and regression cases outside the legacy GPT wrapper.
4. Inventory all API/action dependencies and classify each future integration as supported App, Connector or custom MCP candidate; do not assume Action migration.
5. Keep core KGM behavior independent of a selected ChatGPT model.
6. Build Plugin regression around existing KGM truth, provenance, forecasting, delivery and publication invariants.
7. Revalidate Plugin build/upload/sharing capability on the actual launch account/workspace before any publication decision.
8. Sharing/publication remains an explicit owner decision after platform capability and launch-time validation.

## Canonical boundary

```text
KGM_RUNTIME_CHANGE = NONE
KGM_STATE_MACHINE_CHANGE = NONE
PUBLICATION_ACTIVATION = NO
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = HOLD
PHASE_17_PLUGIN_CAPABILITY_REVALIDATION_REQUIRED = YES
PAID_PROVIDERS = NONE_APPROVED
PRODUCTION_LIVE = NOT_OPERATIONAL
```

Source context: `kolemasakar/AI_general/docs/openai-custom-gpts-retirement-to-plugins-2026-09-16.md`.

Official revalidation basis: OpenAI Help Center — `Custom GPT retirement and migration FAQ`, `Plugins in ChatGPT and Codex`, and ChatGPT Release Notes (checked 2026-09-16).
