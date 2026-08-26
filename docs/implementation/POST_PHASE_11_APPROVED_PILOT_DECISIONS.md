# Post-Phase-11 Approved Pilot Decisions

Status: APPROVED
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Purpose

Record approved product and operational decisions after completion of ROADMAP Phase 11 without assigning a new roadmap phase or engineering milestone number.

## Public Source Policy

The system is oriented to publicly available information.

Eligible source universe:
- all publicly accessible publications that can be lawfully retrieved and processed;
- official websites and public institutional releases;
- global, regional and local media;
- public structured data sources;
- public social-media posts and channels;
- other public web publications relevant to an approved monitoring task or interest class.

Source inclusion does not mean automatic trust.

Every source used as operational evidence must have explicit source identity, source class, reputation/reliability state and reviewable status.

## Local Source Requirement

For an event with a local geographic scope, the system must actively seek local sources in relevant local languages.

Local sources are not optional decoration. They are required coverage inputs when available.

Each local source must preserve:
- source identity;
- local language;
- geographic relevance;
- source class;
- reputation/reliability state;
- current operational status;
- provenance to the original publication.

Translation or republication does not create a new independent origin.

## Production Source Catalog

A production source catalog will be created and populated incrementally as the system develops and is tested.

The catalog is a living registry, not a fixed one-time whitelist.

The current `sources` table remains canonical source identity storage until an additive migration extends its reputation/status lifecycle.

Required future source-governance capabilities include:
- reputation/reliability history;
- status history;
- reason/evidence for status changes;
- review timestamp;
- policy/version under which the decision was made;
- reversible review and restoration when source policy or source behavior changes.

Recommended source-status baseline:
- ACTIVE;
- WATCH;
- COMPROMISED;
- RESTRICTED;
- SUSPENDED;
- RESTORED;
- RETIRED.

A source marked COMPROMISED is not automatically ignored. Its material may still be collected as a claim, narrative or disinformation signal, but its reputation state must remain visible and must not silently increase verification confidence.

Sources repeatedly associated with fabricated or materially misleading content must be marked with an explicit reviewable status. The status must be reversible when the source changes policy/behavior or when the assessment is corrected.

## Unattended Monitoring Decision

The target operating model is continuous unattended monitoring.

Required behavior includes:
- automatic service start after host reboot;
- recovery of due or interrupted watches;
- collection without manual user initiation;
- retry/backoff for unavailable sources;
- persisted attempt/failure state;
- coverage refresh after each collection cycle;
- idempotent restart/recovery;
- health and failure visibility.

This does not change the current production/live status. Production/live remains NOT_OPERATIONAL until a separate launch approval.

## Dashboard Decision

During the free/test start, the operational dashboard should be an admin-only project component using the same project-local runtime data.

Initial placement should be inside the K-Geopolitical Monitor repository/runtime rather than a separate shared platform.

The dashboard should initially expose read-only operational state and remain private/local unless an explicit test-access decision authorizes external exposure.

## Delivery and Notifications

External delivery/publishing is out of scope for the initial test stage.

Automatic notifications are initially represented only as durable database state with at least:
- notification/alert marker;
- created_at/triggered_at timestamp;
- relevant subject/reference;
- status.

No email, Telegram, Slack, SMS or other outbound delivery channel is approved for the initial test stage.

## Automatic Translation

Automatic translation is not part of the initial GPT Store test launch.

It is approved as the first planned expansion after successful testing, subject to provider/architecture selection and validation.

Translation must preserve:
- original text/source;
- detected/original language;
- translated representation;
- provider/model/version provenance where applicable;
- translation timestamp;
- verification independence from the original source.

## Shared Production Runtime

Shared production runtime is deferred until:
- public/test operation is successful;
- launch requirements are reviewed;
- runtime/storage/security/cost conditions are explicitly approved.

Until then:
- runtime remains PROJECT_LOCAL_ONLY;
- mixed/shared runtime storage remains blocked.

## Coverage Model Direction

Absolute proof of complete world coverage is not the target claim.

Coverage should be evaluated against explicit task/interest classes.

Each task/interest class should define at least:
- geographic scope;
- topic/domain scope;
- actors/entities where relevant;
- required local-language coverage;
- required source classes;
- freshness requirement;
- verification requirement;
- expected output/report class.

Initial candidate classes for later design:
- GLOBAL_STRATEGIC_MONITORING;
- REGION_COUNTRY_WATCH;
- EVENT_INCIDENT_MONITORING;
- ACTOR_ENTITY_WATCH;
- DOMAIN_THEME_MONITORING;
- RAPID_FACT_VERIFICATION;
- FORECAST_OUTLOOK;
- NARRATIVE_DISINFORMATION_MONITORING.

These class names are candidate design inputs, not yet a new canonical schema.

## Immediate Development Focus

The analytical core was the primary goal of the completed engineering stages and is now the validated baseline.

The immediate focus is:
- prepare the system/GPT for permitted GPT Store publication;
- conduct structured external testing;
- collect defects, usability findings and architecture gaps;
- only after successful pilot testing, prepare the next roadmap extension covering planned expansions and newly discovered requirements.

No new ROADMAP phase number or M14 milestone is assigned by this decision record.
