# Project Checkpoint — P21.5 Controlled Source Onboarding Validated

Date: 2026-09-17
Gate: `P21_5_CONTROLLED_SOURCE_ONBOARDING_VALIDATED`
Decision: `VALIDATED_WITH_MEASURED_CONTENT_STALENESS`
Implementation merge anchor: `e2b78f8511154e9b626a39d0525d9b118c842bd2`
PR: `#123`
Validation: CI `#1752` / run `35174372833`, job `105052706519` — `1292 passed in 141.35s / SUCCESS`.

Wave A repository onboarding validated two owner-authorized public/free/anonymous Ukrainian RSS paths:

- `ukraine-government-kmu-uk` -> `ukraine.uk.official_government`;
- `suspilne-uk` -> additional `ukraine.uk.national_media`.

Fresh isolated owner-local probe: `2/2 SUCCESS`, `120 items`. `suspilne-uk` was fresh against its 120-minute threshold. KMU collector/parser was healthy but content was stale (~464 minutes against 240), so the limitation is preserved and no healthy/fresh adequacy credit is claimed for that snapshot.

P20.5 qualification remains non-activating; repository activation derives from the explicit P21.5 owner authorization. Deterministic adapter-disable rollback was validated without deleting governance/provenance history. No automatic independent-origin credit was granted. P13.5/P13.6 remain factual-verification authority.

No deployed `/opt/k-geopolitical-monitor` mutation or restart occurred. Production/live remains not operational; paid/shared resources, migration `033`, Phase 18 activation and Plugin build/publication remain unauthorized.

Current position: `PHASE_21_P21_5_VALIDATED_P21_6_READY`.
Next gate: `P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED`.
