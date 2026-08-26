# SOURCE_POLICY
Source management and provenance rules.

Version: 1.1
Status: APPROVED

## Source Classes

- Official sources
- International media
- Regional media
- Social platforms
- OSINT
- Structured data
- User-provided information

## Principle

Source quantity does not equal source independence.

## Provenance Requirement

Every operational source item must remain traceable to:

- source identity;
- source class;
- collection context;
- raw item identity;
- derived operational finding where applicable.

Derived conclusions must remain distinguishable from source evidence.

## Controlled Pilot Rule

The validated M6 controlled pilot baseline uses deterministic project-local JSONL source fixtures under the project-local data boundary.

The controlled pilot validates source-class enforcement, source/raw-item persistence, evidence references and coverage reporting without approving any production external integration.

Live public sources require an explicit integration record and approval under EXTERNAL_INTEGRATIONS.md before activation.

## User Data

User-provided information requires reliability assessment and remains identifiable as non-public unless independently verified.

## Current State

Source/provenance implementation: BASELINE_VALIDATED through M6
Controlled project-local pilot: PASS
Live external-source validation: NOT_STARTED
Production external sources: NOT_APPROVED
