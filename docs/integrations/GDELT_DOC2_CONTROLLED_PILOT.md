# Integration Record - GDELT DOC 2.0 API

Status: APPROVED_FOR_CONTROLLED_PILOT
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Purpose

Provide a live structured discovery source for locating recent online news coverage relevant to active monitoring watches.

## Owner

K-Geopolitical Monitor owns the local adapter, collection audit and local persisted copy of retrieved metadata.

## Provider or Source

Provider: The GDELT Project
API: https://api.gdeltproject.org/api/v2/doc/doc
Documentation: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

## Data Exchanged

Outbound:

- watch search query;
- bounded result-count and time-window parameters.

Inbound:

- article title;
- publisher URL/domain;
- GDELT observation metadata such as language, source country and seen date when supplied.

The adapter does not fetch or republish the full publisher article body.

## Data Classification

Public structured metadata.

## Authentication Mode

None.

## Security Considerations

- HTTPS only;
- bounded request size, timeout and result count;
- explicit User-Agent;
- response must be valid JSON with the expected article-list structure;
- non-JSON HTTP-200 error bodies are treated as failures;
- rate-limit or malformed responses fail closed.

## Source of Truth

GDELT is the Source of Truth for GDELT discovery/index metadata only.

The original linked publisher or primary source remains the Source of Truth for factual claims contained in the linked content. A GDELT match must not be treated as independent verification of a claim.

The local database is the Source of Truth only for K-Geopolitical Monitor collection metadata and derived analysis state.

## Fallback Strategy

Fail closed for the GDELT adapter and record the source failure. Do not silently substitute another aggregation service.

## Failure Isolation Rule

GDELT failure must not prevent other approved source adapters from completing their collection cycle.

## Operational Impact

Controlled-pilot discovery input. It expands discovery coverage but does not independently satisfy verification or cross-check requirements.

## Approval Status

APPROVED_FOR_CONTROLLED_PILOT.

Production/global operational approval: NOT_GRANTED.
