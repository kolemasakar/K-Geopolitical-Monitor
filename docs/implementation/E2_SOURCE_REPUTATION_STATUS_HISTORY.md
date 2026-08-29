# E2 Source Reputation and Status History

Status: BASELINE_VALIDATED
Date: 2026-08-29
Project: K-Geopolitical Monitor
Workstream: E2 - unnumbered post-Phase-11 expansion

This workstream does not create ROADMAP Phase 12 or M14.
Production/live remains NOT_OPERATIONAL.

## 1. Purpose

E2 adds durable, append-only source reputation and status history without turning source reputation into a claim-truth operator.

A source can have a poor historical reliability assessment while a specific new claim remains independently verifiable. Conversely, a good source status does not make every substantive claim automatically true.

## 2. Audit Finding

Before E2, the canonical sources table contained only:
- id;
- name;
- source_class;
- legacy reliability text.

Live and controlled-pilot ingestion could update that legacy reliability field, but there was no durable assessment/status history, policy identity, review timing, reason/evidence trail or restoration lineage.

E2 therefore adds a separate append-only reputation layer and does not reinterpret or rewrite legacy source metadata.

## 3. Additive Persistence

Migration:
- migrations/019_source_reputation_history.sql

Table:
- source_reputation_history

Persisted fields:
- assessment_id;
- source_id;
- assessment_version;
- status;
- reliability_rating;
- reason;
- evidence_refs_json;
- policy_name;
- policy_version;
- assessed_at;
- reviewed_at;
- review_due_at;
- supersedes_assessment_id;
- restoration_of_assessment_id;
- created_at.

History is append-only and versioned per source.

## 4. Status and Reliability Model

Supported statuses:
- ACTIVE;
- WATCH;
- COMPROMISED;
- RESTRICTED;
- SUSPENDED;
- RESTORED;
- RETIRED.

Supported reliability ratings:
- HIGH;
- MEDIUM;
- LOW;
- UNKNOWN.

Status and reliability rating are related assessment metadata but are not claim verification state.

## 5. Runtime Contract

Module:
- src/kgeopolitical_monitor/source_reputation.py

Implemented:
- SourceReputationRecord;
- SourceReputationService;
- append-only record_assessment;
- deterministic current-state query;
- complete per-source history query;
- current-state query across assessed sources;
- evidence-reference normalization;
- policy name/version retention;
- review and review-due timestamps;
- explicit supersession chain;
- explicit restoration lineage.

RESTORED requires a referenced adverse assessment for the same source. Valid restoration targets are COMPROMISED, RESTRICTED or SUSPENDED assessments. Cross-source or non-adverse restoration fails closed.

## 6. Truth and Evidence Isolation

Mandatory rules validated:
- COMPROMISED is not automatic FALSE;
- source status does not modify claim truth;
- source status does not change independent-origin count;
- source reputation metadata can describe the evidentiary burden and source context;
- compromised sources can still be evidence that a claim or narrative exists;
- M8 verification status is unchanged by adding or changing source reputation records;
- legacy sources.reliability remains separate and is not rewritten by the reputation service;
- restoration does not erase previous adverse history.

## 7. Validation

Implementation commits:
- 751dd3a02e561a2552d0fb665b1cedafeb11e650 - Add E2 source reputation history schema
- 90643015065310639f88d73b435fbc032bed7cfe - Implement E2 source reputation history service
- d851be937ee51d79956e9b7db04efb428bcd5401 - Add E2 source reputation history tests
- 563b5a247f1921a8bb287f6ceed4f42a3a870a35 - Validate E2 reputation migration

Canonical E2 code regression:
- GitHub Actions run: 33244795277
- job: 99080306790
- result: SUCCESS
- pytest: 248 passed in 24.01s

Validated behavior:
- append-only version history;
- deterministic current record;
- evidence/policy/review metadata persistence;
- COMPROMISED remains non-automatic-FALSE;
- RESTORED preserves adverse history and references the assessment being restored from;
- invalid restoration fails closed;
- legacy source reliability is not rewritten by E2;
- M8 verification state and independent-origin count remain unchanged;
- history survives runtime restart;
- unknown source and invalid time ordering fail closed.

## 8. Gate

E2 gate result:
E2_SOURCE_REPUTATION_STATUS_HISTORY_BASELINE_PASS

State:
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- E2 Source Reputation and Status History: BASELINE_VALIDATED
- runtime storage: PROJECT_LOCAL_ONLY
- production/live: NOT_OPERATIONAL
- next workstream: E3 Private GPT Backend Action API

E3 remains an unnumbered post-Phase-11 workstream and does not create ROADMAP Phase 12 or M14.
