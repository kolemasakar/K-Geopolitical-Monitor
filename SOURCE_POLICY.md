# SOURCE_POLICY
Source management and provenance rules.

Version: 1.2
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
- original source URL where applicable;
- derived operational finding where applicable.

Derived conclusions must remain distinguishable from source evidence.

## Controlled Pilot State

M6 validated deterministic project-local source fixtures.

M7 validated two live read-only public-source integrations under explicit controlled-pilot records:

- Consilium press-release RSS as Official sources;
- GDELT DOC 2.0 as Structured data discovery metadata.

GDELT discovery metadata is not independent verification of publisher claims. The original publisher or primary source remains the factual Source of Truth for linked content.

The M7 live smoke gate succeeded against both approved public endpoints.

## Live Source Rule

Only integrations with explicit records under docs/integrations may be activated for controlled live pilots.

A controlled-pilot approval does not equal production/global operational approval.

## User Data

User-provided information requires reliability assessment and remains identifiable as non-public unless independently verified.

## Current State

Source/provenance implementation: BASELINE_VALIDATED through M7
Deterministic controlled pilot: PASS
Live read-only source acquisition pilot: PASS
Production external-source operation: NOT_APPROVED
Runtime storage: PROJECT_LOCAL_ONLY
