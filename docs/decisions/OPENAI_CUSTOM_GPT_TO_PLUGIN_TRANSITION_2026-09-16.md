# KGM — OpenAI Custom GPT → Plugin transition decision

Date: 2026-09-16  
Status: **ARCHITECTURE DIRECTION RECORDED / NO ACTIVATION**

## Context

OpenAI has announced retirement of Custom GPTs and migration toward Plugins. KGM currently retains GPT-facing publication/integration concepts in its documentation (`private GPT backend Action`, public-sharing boundary, controlled publication readiness), but these are not activated production capabilities.

This decision updates the strategic deployment target without changing canonical runtime/storage/truth boundaries or activating any external publication.

## Decision

```text
PRIMARY_CHATGPT_SURFACE = Plugin
LEGACY_GPT_SURFACE      = transitional only
PUBLIC_GPT_ACTION       = legacy integration concept
PLUGIN_PUBLICATION      = NOT_ACTIVATED
```

Any future ChatGPT-facing KGM product should be designed around:

- KGM workflow / policy as Plugin skill(s);
- reference assets as explicit structured resources;
- external capabilities through supported App / Connector / MCP-based integration;
- existing KGM backend/runtime APIs only where they satisfy the Plugin integration contract;
- regression and truth-governance invariants preserved independently of the UI/deployment wrapper.

## Mapping of existing KGM concepts

```text
KGM instructions / operational workflow
-> Plugin skill/workflow

private GPT backend Action concept
-> App / Connector / custom MCP integration candidate

controlled publication readiness
-> Plugin sharing/publication readiness, still owner-gated

truth/provenance/forecast policies
-> unchanged domain invariants
```

## Non-effects

This decision does **not**:

- activate Phase 17 publication;
- activate any public GPT or Plugin;
- change Phase 18 shared-runtime state;
- create migration `033`;
- approve paid providers;
- change `PROJECT_LOCAL_ONLY` storage;
- change truth/provenance semantics;
- create public API/dashboard ingress;
- authorize production/live launch.

## Implementation direction

1. Preserve existing publication/integration docs as historical and regression evidence.
2. Treat any future GPT-specific work as legacy maintenance only.
3. When KGM reaches a new publication architecture gate, design the ChatGPT-facing layer as Plugin-first.
4. Inventory any future Action/API requirements separately; do not assume Custom Actions migrate automatically.
5. Build Plugin regression around existing KGM truth, provenance, forecasting, delivery, and publication invariants.
6. Sharing/publication remains an explicit owner decision after platform capability and launch-time validation.

## Canonical boundary

```text
KGM_RUNTIME_CHANGE=NONE
KGM_STATE_MACHINE_CHANGE=NONE
PUBLICATION_ACTIVATION=NO
PLUGIN_BUILD=NOT_STARTED
PLUGIN_PUBLICATION=HOLD
PAID_PROVIDERS=NONE_APPROVED
PRODUCTION_LIVE=NOT_OPERATIONAL
```

Source context: `kolemasakar/AI_general/docs/openai-custom-gpts-retirement-to-plugins-2026-09-16.md`.
