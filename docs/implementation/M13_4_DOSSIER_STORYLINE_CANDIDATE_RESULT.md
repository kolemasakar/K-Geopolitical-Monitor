# M13.4 Event Dossier and Storyline Result

Status: VALIDATION_PENDING
Date: 2026-08-26
Project: K-Geopolitical Monitor
Milestone: M13.4 Event Dossier and Storyline Report

## Implementation

Original candidate implementation:
- `7651ac787762e7b3b446c94beff0a3b16eeb1a9c`

Main promotion:
- `891c2c251382676ed11ac1c173f6572f27aac7db`

## Implemented Contracts

- Event Dossier is anchored to a valid canonical event ID;
- explicit persisted event, claim, raw-item, finding and graph references only;
- claim verification/confidence is display-only and is not recalculated by reporting;
- source evidence contains explicit persisted observations and source provenance;
- observation timeline uses persisted raw-item collection timestamps only;
- timeline does not infer event-occurrence timestamps;
- contradiction pairs are explicit report-scoped analytical context;
- contradiction composition does not mutate claim verification state;
- common M13.2 assembler sections are shifted and reference-remapped deterministically;
- Storyline Report is scope-only and creates no canonical storyline entity/table;
- unknown durable references fail closed;
- dossier/storyline composition does not mutate upstream event, claim, raw-item, finding or graph state;
- no new report-specific truth table or migration;
- runtime storage remains project-local.

## Validation State

The M13.4 implementation and acceptance tests are now on `main`.

Full repository CI on the combined M13.3-M13.5 main checkpoint is required before this gate can be changed to PASS.

Gate:
`M13_4_DOSSIER_STORYLINE_VALIDATED = PENDING`

## Boundary

This implementation does not approve canonical storyline persistence, inferred event timestamps, shared runtime storage, external publishing/delivery, production dashboards or production/live OPERATIONAL status.
