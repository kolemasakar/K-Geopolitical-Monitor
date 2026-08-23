# MINIMAL_CORE_STORAGE_MODEL

Version: 0.1
Status: APPROVED

## Purpose

Define storage requirements for the first implementation.

## Required persistent objects

- Source
- RawItem
- Claim
- Evidence
- Entity
- Event
- EventUpdate
- Storyline
- Forecast
- Report

## Storage requirements

The storage layer must support:

- provenance tracking;
- history preservation;
- versioning;
- relationships between entities;
- auditability.

The first implementation may use a simplified database model.
