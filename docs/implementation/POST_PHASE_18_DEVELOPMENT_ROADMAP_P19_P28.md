# K-Geopolitical Monitor — Post-Phase 18 Development Roadmap P19–P28

Date: 2026-09-09
Status: `APPROVED`
Approval: owner-selected roadmap option 1
Base at approval: `81c51db0d4faad5c963f0f7ae2523316e6614640`
Strategic machine state: `4.34` intentionally unchanged

## 1. Starting Position

Phase 18 established infrastructure and activation readiness. It did not authorize activation.

```text
P18.0–P18.9 = VALIDATED
A0 = COMPLETE
A1 = VALIDATED
A2 = VALIDATED
A3 = VALIDATED
A4 = VALIDATED
ACTIVATION_STATE = ACTIVATION_READY / NOT_ACTIVATED
A5 = DEFERRED / NOT AUTHORIZED
```

The development priority now shifts from proving that a shared runtime can be launched safely to improving the quality, completeness, explainability, and operational usefulness of geopolitical intelligence.

## 2. Binding Beta Boundaries

This roadmap does not alter the Phase 18 activation policy.

```text
OWNER_LOCAL_RUNTIME = CANONICAL
CANONICAL_STORAGE = PROJECT_LOCAL_ONLY
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
PRODUCTION_LIVE = NOT_OPERATIONAL
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
RAILWAY_PAID_UPGRADE_AUTHORIZED = NO
RAILWAY_PAYMENT_METHOD_ADD_AUTHORIZED = NO
RAILWAY_CREDIT_PURCHASE_AUTHORIZED = NO
RAILWAY_POST_TRIAL_SPEND_AUTHORIZED = NO
```

Railway Trial exhaustion or expiry is a stop condition for the disposable candidate, never automatic authorization to purchase resources or activate A5.

## 3. Roadmap Sequence

```text
Phase 18 — Infrastructure / Activation Readiness       VALIDATED
                         ↓
P19 — Beta Operational Stability
                         ↓
P20 — Source Coverage & Collection Quality
                         ↓
P21 — Evidence / Verification / Confidence
                         ↓
P22 — Event Graph / Timeline Intelligence
                         ↓
P23 — Analytical & Early-Warning Layer
                         ↓
P24 — Intelligence Product Layer
                         ↓
P25 — OSINT / External Enrichment
                         ↓
P26 — Long-Run Reliability / Security / Recovery
                         ↓
P27 — Beta Exit Review
                  ↙              ↘
 owner-local continues          explicit A5 decision
                                  only if justified
                                        ↓
P28 — Multi-user / Production Scale
      only if demonstrated need exists
```

A5 is not a mandatory phase in this sequence. P27 may conclude that owner-local canonical operation remains the preferred architecture.

---

## 4. P19 — Beta Operational Stability

### Objective

Prove that KGM can operate continuously in beta without routine manual intervention and without silent pipeline degradation.

### Scope

- unattended monitoring cycles;
- ingest, clustering, enrichment, scoring, and briefing health;
- source-health monitoring;
- stale-data and missed-cycle detection;
- retry, idempotency, and dead-letter behavior;
- deterministic runtime failure classification;
- operational status/dashboard summary;
- 7/14/30-day stability evidence;
- explicit detection of silent partial failures.

### Exit criteria

- repeated unattended cycles are observable and auditable;
- critical failures are surfaced rather than silently skipped;
- no evidence of canonical data loss or corruption;
- recovery procedures are exercised for representative beta failures;
- operational metrics are sufficient to distinguish healthy, degraded, and failed states.

### Gate

`P19_BETA_OPERATIONAL_STABILITY_VALIDATED`

### Why it matters

A green test suite proves implementation correctness at a point in time. P19 proves that the system remains usable under sustained real operation.

---

## 5. P20 — Source Coverage & Collection Quality

### Objective

Make global coverage measurable so KGM can identify not only what it knows, but also where its information picture is weak or missing.

### Scope

Create and maintain a source taxonomy covering, as appropriate:

- official government sources;
- international organizations;
- wire services;
- national and regional media;
- defense/security sources;
- think tanks and research institutions;
- public OSINT sources;
- economic and energy sources;
- sanctions and regulatory registers;
- approved public social sources.

For sources, capture structured metadata such as:

```text
COUNTRY
REGION
LANGUAGE
SOURCE_TYPE
RELIABILITY_CLASS
UPDATE_FREQUENCY
COLLECTION_STATUS
COVERAGE_ROLE
```

Add coverage analysis for:

- geography;
- language;
- source-type diversity;
- source redundancy;
- source monoculture risk;
- collection latency;
- missing-source and stale-source conditions.

### Exit criteria

- coverage is measurable by region, language, and source type;
- material collection gaps are visible;
- apparent corroboration caused by many copies of one source can be distinguished from independent coverage;
- source-health failures do not masquerade as a quiet geopolitical environment.

### Gate

`P20_GLOBAL_SOURCE_COVERAGE_VALIDATED`

---

## 6. P21 — Evidence / Verification / Confidence Layer

### Objective

Move from article-level reporting to claim-level evidence and explainable confidence.

### Target model

```text
CLAIM
 ├── supporting sources
 ├── contradicting sources
 ├── primary evidence
 ├── source independence assessment
 ├── source reliability
 ├── provenance
 └── confidence + explanation
```

### Scope

- claim-level provenance;
- independent-source/copy-chain distinction;
- corroboration scoring;
- contradiction preservation;
- primary vs secondary evidence distinction;
- source and evidence confidence;
- confidence explanations rather than opaque labels;
- explicit separation of confirmed fact, reported claim, unresolved contradiction, and unknown.

### Exit criteria

- important claims can be traced to evidence;
- conflicting accounts can coexist without the system arbitrarily selecting one as fact;
- confidence can be explained from observable evidence features;
- downstream briefs retain provenance to the underlying claims and sources.

### Gate

`P21_EVIDENCE_VERIFICATION_CONFIDENCE_VALIDATED`

---

## 7. P22 — Event Graph / Timeline Intelligence

### Objective

Represent geopolitical developments as connected episodes and timelines rather than isolated news items.

### Scope

- entity resolution for countries, governments, officials, organizations, military structures, locations, and relevant assets;
- event deduplication across sources and languages;
- event relationships such as:
  - `PRECEDES`;
  - `FOLLOWS`;
  - `RESPONDS_TO`;
  - `ESCALATES`;
  - `DEESCALATES`;
  - `CONTRADICTS`;
  - `CAUSES` only where evidence supports causality;
  - `RELATED_TO`;
- episode grouping;
- chronological and causal-context timelines;
- provenance-preserving graph navigation.

### Exit criteria

- repeated reports about one development do not inflate event counts;
- multi-step geopolitical episodes can be reconstructed chronologically;
- entity ambiguity is bounded and visible;
- causal links are not inferred beyond the available evidence.

### Gate

`P22_EVENT_GRAPH_TIMELINE_INTELLIGENCE_VALIDATED`

---

## 8. P23 — Analytical & Early-Warning Layer

### Objective

Convert validated events into explainable signals, patterns, risk indicators, and bounded scenarios while preserving the distinction between facts and analysis.

### Scope

Potential indicator families include:

- unusual military force activity;
- strategic aviation or missile-carrier activity;
- airspace restrictions / NOTAM-type signals;
- diplomatic warnings and evacuations;
- sanctions preparation;
- abnormal government communication patterns;
- cyber or infrastructure signals where supported by reliable data;
- economic, energy, and logistics indicators.

Develop:

- baseline vs anomaly detection;
- escalation/de-escalation indicators;
- scenario construction;
- supporting and contradicting indicators;
- explicit unknowns;
- confidence and calibration evidence;
- Ukraine national-interest lens for military, diplomatic, economic, energy, sanctions, alliance, Russian-resource, and defense-industrial implications.

Required output separation:

```text
FACT
ASSESSMENT
SCENARIO
```

### Exit criteria

- analytical statements are never emitted as raw facts;
- scenarios show the indicators that support or weaken them;
- uncertainty is explicit;
- historical evaluation demonstrates that alerts are useful rather than merely frequent.

### Gate

`P23_GEOPOLITICAL_ANALYTICS_EARLY_WARNING_VALIDATED`

---

## 9. P24 — Intelligence Product Layer

### Objective

Turn backend intelligence into consistent products for daily operational use.

### Scope

- global 24-hour brief;
- regional/thematic briefs;
- `FACTS / ANALYSIS / WHAT CHANGED / WHAT TO WATCH` structure;
- watchlists;
- alert thresholds using importance, novelty, and confidence;
- event/claim/source drill-down;
- concise change detection since previous brief;
- explicit uncertainty and evidence links.

### Exit criteria

- briefs are reproducible from canonical evidence;
- important developments are not hidden by high-volume low-value reporting;
- alert volume is controlled and auditable;
- every material analytical conclusion can be drilled down to evidence.

### Gate

`P24_INTELLIGENCE_PRODUCT_LAYER_VALIDATED`

---

## 10. P25 — OSINT / External Enrichment

### Objective

Add specialized external capabilities without weakening project isolation or canonical authority.

### Candidate capabilities

Only where legally, technically, and operationally appropriate:

- public satellite/imagery metadata;
- geolocation support;
- sanctions databases;
- public economic indicators;
- public flight/maritime data;
- approved public social intelligence;
- video/audio enrichment;
- document extraction and structured evidence capture.

### Architecture boundary

Preferred model:

```text
KGM canonical storage
       │
       ├── bounded API / task contract → external capability
       │
       └── sanitized structured result ← evidence/provenance
```

Forbidden by default:

- uncontrolled shared canonical databases across projects;
- cross-project filesystem authority;
- secret reuse without explicit design;
- an enrichment service becoming canonical by accident.

### Exit criteria

- every enrichment path has explicit data/provenance boundaries;
- external service failure does not corrupt canonical KGM state;
- sensitive/non-sensitive data classifications are respected;
- project isolation remains auditable.

### Gate

`P25_EXTERNAL_INTELLIGENCE_ENRICHMENT_VALIDATED`

---

## 11. P26 — Long-Run Reliability / Security / Recovery

### Objective

Revalidate resilience after P19–P25 expand the system surface.

### Scope

- backup and restore;
- application-level recovery validation;
- database integrity;
- secrets and key rotation;
- dependency/security scanning;
- remote-control-plane boundaries;
- host/runtime recovery;
- reproducible deployment;
- incident runbooks;
- provenance/audit-trail preservation;
- failure injection where safe;
- explicit recovery objectives appropriate to the actual beta/production model.

Required recovery chain:

```text
BACKUP EXISTS
      ↓
RESTORE WORKS
      ↓
RESTORED DATA IS VALID
      ↓
APPLICATION OPERATES CORRECTLY
```

### Exit criteria

- backups are demonstrated by restore, not file existence alone;
- recovery preserves security and tenant/isolation properties where applicable;
- critical operational procedures are documented and reproducible;
- no new dependency silently creates an unapproved paid or shared-runtime requirement.

### Gate

`P26_LONG_RUN_RESILIENCE_VALIDATED`

---

## 12. P27 — Beta Exit Review

### Objective

Use actual beta evidence to decide the target operating model rather than assuming that shared runtime or scale is inherently desirable.

### Required review

Evaluate at least:

- intelligence quality and usefulness;
- coverage gaps;
- false-positive/false-negative behavior where measurable;
- real data volume and compute load;
- operational bottlenecks;
- actual need for 24/7 remote runtime;
- whether PostgreSQL needs to become canonical;
- whether multi-user/team operation is needed;
- realistic hosting/backup/monitoring cost;
- security and operational burden;
- benefits of owner-local continuation versus shared runtime.

### Outcomes

Possible valid outcome A:

`OWNER_LOCAL_CANONICAL_CONTINUES`

Possible valid outcome B:

`A5_REVIEW_JUSTIFIED`

P27 does not itself perform A5.

### Gate

`P27_BETA_EXIT_REVIEW_COMPLETED`

---

## 13. A5 — Explicit Owner Shared-Runtime Activation Decision

A5 remains outside automatic roadmap execution.

Status at roadmap approval:

`DEFERRED / NOT AUTHORIZED`

Before any A5 approval, re-evaluate:

- whether shared runtime is actually needed;
- current provider and cost state;
- Railway Trial or successor-provider state;
- paid-resource justification if beta policy is being changed;
- backup/PITR capability;
- canonical datastore choice;
- canonical data migration/cutover;
- split-brain prevention;
- rollback window and stop criteria;
- migration `033` need and explicit authorization;
- monitoring and public/private API exposure.

A5 requires a separate explicit owner decision. No P19–P27 success implies permission to activate it.

---

## 14. P28 — Multi-user / Production Scale

### Objective

Implement multi-user and production-scale capabilities only after real usage demonstrates a need.

### Potential scope

- identity and authentication;
- RBAC;
- workspace/tenant isolation;
- user audit trail;
- API rate/usage limits;
- scalable worker model;
- HA and production datastore design;
- SLO/SLA definitions;
- production operations and support model.

### Entry condition

P28 must not start merely because the system is technically capable of scaling. It requires a documented need arising from P27 and, where relevant, an explicit A5 outcome.

### Gate

`P28_MULTIUSER_PRODUCTION_SCALE_VALIDATED`

---

## 15. Priority Order

| Priority | Stage | Primary value |
|---|---|---|
| 1 | P19 | prove sustained beta stability |
| 2 | P20 | measure what the monitor sees and misses |
| 3 | P21 | increase evidence quality and trust |
| 4 | P22 | convert news into event/timeline intelligence |
| 5 | P23 | add explainable early-warning analysis |
| 6 | P24 | turn intelligence into daily operational products |
| 7 | P25 | add bounded specialist OSINT enrichment |
| 8 | P26 | revalidate resilience after feature expansion |
| 9 | P27 | decide beta exit architecture from evidence |
| 10 | A5/P28 | only if need and owner authorization are established |

## 16. Immediate Next Stage

The next implementation stage is:

`P19 — BETA OPERATIONAL STABILITY`

P19 work may begin without opening A5, changing canonical storage, using a paid Railway plan, or altering strategic state `4.34`.

## 17. Related Binding Records

- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_READY_RAILWAY_TRIAL_BOUNDARY.md`
- `docs/evidence/PHASE_18_A4_RAILWAY_TRIAL_NO_CHARGE_EVIDENCE_2026-09-09.md`
- `docs/implementation/PHASE_18_ACTIVATION_A2_A5_APPROVED_PLAN.md`

This roadmap extends development beyond Phase 18. It does not supersede the activation or Trial cost boundaries in those records.