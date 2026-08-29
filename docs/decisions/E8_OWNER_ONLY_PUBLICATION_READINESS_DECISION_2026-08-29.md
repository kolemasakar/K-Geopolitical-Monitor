# E8 Owner-Only Publication Readiness Decision

Date: 2026-08-29
Project: K-Geopolitical Monitor
Status: OWNER_DECISION_APPROVED
Scope: GPT development/publication readiness only

## Decision

The K-Geopolitical Monitor GPT will be developed from this point with an explicit future publication target.

Owner decisions:
- the GPT remains owner-only during active development;
- there will be exactly one intended user until development is complete: the owner;
- no controlled external user cohort is required before development completion;
- the owner plans to move the ChatGPT account/workspace to Business before the publication stage;
- GPT Store/public sharing configuration will be performed only after Business workspace eligibility, workspace settings and role permissions are verified at that time;
- current owner-only development should nevertheless be publication-ready by design, so public-facing instructions, safety/truth boundaries, branding, privacy requirements and any future Action architecture are prepared before the launch gate;
- public sharing, public backend exposure and GPT Store publication remain inactive until a later explicit publication approval.

## Effect on the E8 preflight recommendation

This decision supersedes the earlier recommendation to use a controlled external cohort as the first E8 activation step.

The previous E8A external-cohort step is no longer mandatory.

The approved development trajectory is now:

`OWNER_ONLY DEVELOPMENT -> PUBLICATION-READY HARDENING -> BUSINESS WORKSPACE -> FINAL PUBLICATION GATE -> PUBLICATION/SHARING`

This does not activate E8 external sharing today.

## Publication-ready development scope

During the remaining owner-only development, the GPT should be prepared as though it will eventually be reviewed for public publication.

Required preparation includes:
- stable GPT name, description and category positioning;
- publication-quality system/instruction contract;
- conversation starters suitable for public users;
- explicit truth/verification/provenance/coverage/forecast boundaries;
- public-facing behavior tests and adversarial test matrix;
- review of knowledge/files/capabilities for disclosure suitability;
- review of any future Action data surface for data minimization;
- privacy-policy preparation if a public Action is retained for the publication build;
- domain/builder-profile plan if required by the selected publication path;
- publication rollback/unpublish procedure;
- final Business workspace permission and publication-eligibility check immediately before launch.

## Backend Action decision

No public Action is approved by this decision.

Current owner-only E3 Action API remains:
- VALIDATED_LOCAL_READ_ONLY;
- HTTPS NOT_DEPLOYED;
- GPT Action NOT_CONNECTED;
- owner/admin only by architecture.

If persisted backend state is later required in the public GPT, the E8 preflight rule remains mandatory:
- do not expose the existing owner API directly;
- create a distinct sanitized external read-only facade;
- use a separate external credential;
- allowlist public fields/endpoints;
- keep monitoring, dashboard and database non-public;
- use HTTPS and appropriate exposure controls;
- provide a valid Privacy Policy URL for any public Action;
- retain a kill switch and credential-revocation path.

The external Action implementation requires a separate explicit owner approval.

## Current OpenAI platform dependency

Official OpenAI Help Center guidance was rechecked on 2026-08-29.

Relevant current constraints:
- personal ChatGPT accounts, including Free, Go, Plus and Pro, cannot create or publish new GPTs under the current rules;
- Business, Enterprise and Edu workspace creation/sharing/publishing depend on workspace settings and role permissions;
- GPT Store publication depends on eligibility and workspace permissions;
- public Actions require a valid Privacy Policy URL;
- publication rules may change and must be rechecked at the actual launch gate.

These are external platform constraints, not permanent KGM architecture facts.

References:
- https://help.openai.com/en/articles/8798878-sharing-and-publishing-gpts
- https://help.openai.com/en/articles/8554407-what-are-gpts
- https://help.openai.com/en/articles/11325361

## Unchanged project boundaries

This decision does not change:
- runtime storage: PROJECT_LOCAL_ONLY;
- shared/mixed runtime storage: NOT_APPROVED;
- production/live operational status: NOT_OPERATIONAL;
- E9 Shared Production Runtime: NOT_APPROVED;
- backend HTTPS: NOT_DEPLOYED;
- public API ingress: NOT_DEPLOYED;
- admin dashboard: LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED;
- E4 owner-approved temporary SSH/egress development exception;
- truth, provenance, verification, forecast and coverage invariants.

## Gate state after decision

- `E8_OWNER_ONLY_PUBLICATION_READINESS = APPROVED`
- `E8_SINGLE_USER_DEVELOPMENT = ACTIVE`
- `E8_CONTROLLED_EXTERNAL_COHORT = NOT_REQUIRED_BEFORE_COMPLETION`
- `E8_BUSINESS_MIGRATION = PLANNED`
- `E8_EXTERNAL_SHARING = NOT_ACTIVE`
- `E8_PUBLIC_ACTION = NOT_APPROVED`
- `E8_PUBLIC_BACKEND = NOT_DEPLOYED`
- `E8_PUBLIC_GPT = NOT_PUBLISHED`
- `E9_SHARED_PRODUCTION_RUNTIME = NOT_APPROVED`

Owner-only publication-ready development may proceed without waiting for Business migration. Actual sharing/publication requires a later explicit gate after the Business workspace is available and current OpenAI requirements are revalidated.
