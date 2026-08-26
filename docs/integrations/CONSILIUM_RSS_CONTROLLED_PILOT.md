# Integration Record - Consilium Press Releases RSS

Status: APPROVED_FOR_CONTROLLED_PILOT
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Purpose

Provide a live official-source feed for controlled monitoring of public statements and press releases from the Council of the European Union and the European Council.

## Owner

K-Geopolitical Monitor owns the local adapter, collection audit and local persisted copy of retrieved metadata.

## Provider or Source

Provider: General Secretariat of the Council of the European Union
Feed: https://www.consilium.europa.eu/en/rss/pressreleases.ashx
Documentation: https://www.consilium.europa.eu/en/about-site/rss/

## Data Exchanged

Inbound only:

- RSS item title;
- description/summary when supplied;
- canonical item link;
- publication date when supplied.

No data is written back to the provider.

## Data Classification

Public information.

## Authentication Mode

None.

## Security Considerations

- HTTPS only;
- strict response-size and timeout limits in runtime transport;
- XML parsing uses the Python standard library and does not enable external entity expansion;
- retrieved content remains untrusted external input;
- no scripts or HTML are executed.

## Source of Truth

The Consilium website and linked Council/European Council publication are the Source of Truth for the official statement.

The local database is the Source of Truth only for K-Geopolitical Monitor collection metadata and derived analysis state.

## Fallback Strategy

Fail closed for the source adapter and record the source failure. Do not silently replace this official source with another provider.

## Failure Isolation Rule

Failure of this feed must not prevent other approved source adapters from completing their collection cycle.

## Operational Impact

Controlled-pilot input only. Not sufficient on its own for a verified geopolitical conclusion.

## Approval Status

APPROVED_FOR_CONTROLLED_PILOT.

Production/global operational approval: NOT_GRANTED.
