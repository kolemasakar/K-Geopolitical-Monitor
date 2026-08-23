# CORE_ENTITIES
Core data entities for K-Geopolitical Monitor.

Version: 0.1
Status: APPROVED

## Purpose
Defines minimum domain objects required for Minimal Functional Core.

## Source
Represents an information origin.

Required fields:
- source_id
- name
- source_class
- origin
- language
- reliability_profile

## RawItem
Original collected information.

Required fields:
- raw_item_id
- source_id
- collected_at
- published_at
- content_reference
- provenance

## Claim
A statement extracted from information.

Required fields:
- claim_id
- raw_item_id
- claim_type
- verification_status

## Evidence
Support or contradiction for claims.

Required fields:
- evidence_id
- claim_id
- source_reference
- evidence_type

## Event
A normalized real-world occurrence.

Required fields:
- event_id
- event_type
- actors
- location
- time
- status

## EventUpdate
A change to an existing event state.

Required fields:
- update_id
- event_id
- change_type
- timestamp

## Entity
A person, organization, country or institution.

## Storyline
A long-running geopolitical process connecting events.

## Forecast
A probability-based assessment of future scenarios.
