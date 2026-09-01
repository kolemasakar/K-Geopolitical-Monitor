# K-Geopolitical Monitor — System Development Analysis

Date: 2026-09-01
Status: `ANALYSIS_COMPLETE`
Basis checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_PRE_NEXT_ROADMAP_ANALYSIS.md`
Repository state anchor before analysis document: `376cdd6c98627de44e7c9678059a9dfb8a1b8370`

## 1. Executive conclusion

K-Geopolitical Monitor has completed the transition from a concept/MVP into a **broad, strongly governed engineering platform** with validated persistence, operational monitoring, alerts, region/language coverage modeling, graph persistence, forecasting persistence/evaluation structures, reporting, reproducibility, an owner-only read-only API/dashboard foundation, unattended OCI execution, backup/DR and owner-only production-candidate hardening.

The next development problem is no longer infrastructure completeness.

The principal gap is that **engineering breadth is materially ahead of intelligence depth and operational productization**.

The repository has strong contracts and truth boundaries, but several central analytical engines remain deliberately simple baselines. The current live acquisition surface is narrow, the live claim model is title-based, contradiction reasoning is minimal, confidence remains heuristic, forecast generation does not yet infer probabilities from evidence, adaptive learning remains baseline-level, the dashboard/API are not operationally exposed, and there is no approved delivery/notification layer.

Therefore the recommended next strategy is:

`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> CALIBRATION -> DELIVERY -> OPTIONAL PUBLICATION/SHARED RUNTIME`

Do **not** prioritize E8 public publication or E9 shared runtime ahead of intelligence quality and owner operational value.

## 2. What is genuinely mature today

### 2.1 Governance and epistemic boundaries — HIGH maturity

Strongest part of the project.

Validated and repeatedly regression-protected boundaries include:
- publisher/publication is not automatically the underlying origin;
- syndication/repost/translation does not create independent corroboration;
- official statement is evidence that an actor made the statement, not automatic proof of the substantive claim;
- source reputation is context, not a truth operator;
- graph inference cannot become independent source evidence;
- forecast probability cannot become factual verification confidence;
- coverage confidence cannot become factual verification confidence;
- GLOBAL is scope, not proof of exhaustive global coverage;
- unavailable persisted backend state cannot be replaced by ad hoc web research;
- exact research/tool history cannot be reconstructed and mislabeled exact.

This is strategically valuable and should remain the non-negotiable architecture core.

### 2.2 Persistence / audit / reproducibility — HIGH maturity

The platform has durable state for major analytical and operational objects, versioning/history in several subsystems, migration-based SQLite evolution, explicit reproducibility instrumentation, persisted artifact hashing and strong fail-closed behavior.

E9A adds:
- single-instance runtime lease;
- explicit SQLite profile;
- online backup/restore bundle;
- runtime health;
- DR drill;
- real reboot/recovery evidence.

This is much stronger than the analytical sophistication currently sitting above it.

### 2.3 Owner-only runtime — HIGH engineering maturity

The OCI ARM64 runtime has real-host evidence for:
- immutable/state-preserving deployment;
- systemd startup/restart;
- physical reboot recovery;
- interrupted-run recovery;
- due-watch resumption;
- SQLite integrity;
- second-instance rejection;
- backup/restore;
- hardened service identity and write paths;
- removal of unnecessary rpcbind/111 surface.

The runtime is correctly classified as `OWNER_ONLY_PRODUCTION_CANDIDATE_READY`, not production/live.

### 2.4 Reporting / coverage representation — MEDIUM-HIGH maturity

The repository has a substantial reporting environment with common assembly, structured and Markdown output, report snapshots, dossier/brief/forecast surfaces and explicit coverage semantics.

The main limitation is not reporting mechanics. It is the quality and breadth of the intelligence that feeds those reports.

## 3. Where the implementation is weaker than the architecture language suggests

### 3.1 Live source network — LOW maturity relative to project ambition

Approved live integrations are currently only:
- Consilium press-release RSS;
- GDELT DOC 2.0 discovery/index API.

`live_sources.py` confirms that the live adapter layer is currently centered on `GdeltDoc2Adapter` and `ConsiliumRssAdapter`.

This is not enough for a system whose product identity is global geopolitical monitoring.

Important missing source classes for actual operational value include:
- more official government/foreign-affairs/defence feeds;
- UN and major international organizations;
- national/parliamentary/regulatory sources;
- sanctions and legal/regulatory feeds;
- humanitarian/security institutions;
- energy/shipping/aviation/economic structured data where legally/technically feasible;
- broader international and local-language media discovery;
- carefully governed social/OSINT discovery sources;
- source availability/freshness monitoring across a much larger registry.

The existing coverage layer measures configured requirements. It cannot compensate for a small source universe.

### 3.2 Claim extraction and claim identity — LOW-MEDIUM maturity

The live end-to-end processor derives `claim_key` from normalized article titles.

This creates several risks:
- semantically identical claims with different wording may remain separate;
- similar headlines about materially different claims may collide;
- one article can contain multiple claims but currently maps naturally to one title-based claim;
- quoted/attributed claims are not deeply decomposed into actor, proposition, scope, time and modality;
- changes to a headline can affect deterministic claim identity despite unchanged underlying proposition.

The next-generation claim layer should represent claims structurally rather than treating title normalization as the principal semantic identity mechanism.

### 3.3 Verification engine — LOW-MEDIUM analytical maturity

The baseline `verification.py` still evaluates claim status essentially from evidence count and does not implement a full verification policy engine.

The live processor currently upgrades a live claim to `PARTLY_VERIFIED` when there are at least two distinct origin hosts.

This is safer than counting reposts as independent adapters, but it is still weaker than the project's own epistemic model because:
- distinct domains are not automatically independent underlying origins;
- two publishers can cite the same official statement, wire report or source dataset;
- source proximity to the event is not fully modeled in the decision;
- evidence type and contradiction substance are not fully evaluated;
- primary-source status and independence are different dimensions.

The project has the right policy philosophy but needs a richer executable verification engine.

### 3.4 Contradiction reasoning — LOW maturity

`contradictions.py` currently defines a simple `Contradiction` object but not a substantive contradiction-detection/resolution engine.

This is a major gap for geopolitical research because high-value events often involve:
- conflicting casualty/asset numbers;
- disputed attribution;
- incompatible timelines;
- claim/denial pairs;
- official vs independent-observer disagreement;
- evolving preliminary estimates.

Contradiction should become a first-class typed analytical object linked to claims, evidence, dimensions, time and resolution state.

### 3.5 Confidence calculation — LOW-MEDIUM maturity

The current confidence baseline is a fixed weighted formula using evidence count, average source reliability, source-ID independence and contradiction penalty.

This is transparent, which is good, but it is too coarse for the intended product.

Needed separation:
- evidence sufficiency;
- source independence confidence;
- source proximity/authority;
- source reliability history;
- contradiction severity;
- temporal freshness;
- claim-specific uncertainty;
- extraction/translation uncertainty;
- coverage limitation.

A single scalar can still be produced for presentation, but the underlying dimensions should remain independently inspectable.

### 3.6 Advanced graph — MEDIUM infrastructure / LOW-MEDIUM inference maturity

Graph persistence, identity, lifecycle/history and temporal traversal are substantial.

However, some relationship-analysis entry modules remain baseline/simple. The architecture therefore has a strong **graph storage/query substrate**, but not yet a fully developed automated geopolitical relationship-inference system.

The next value step is not a new graph database. It is better evidence-backed graph projection and relationship extraction.

### 3.7 Forecasting — MEDIUM-HIGH persistence / LOW probability-generation maturity

M12/E7 provides strong forecast identity, versioning, scenario history, provenance, semantic separation, outcome/evaluation and calibration structures.

But the baseline `ProbabilisticForecastEngine` normalizes probabilities supplied to it; it does not itself derive calibrated probabilities from evidence/signals.

Therefore KGM currently has a good **forecast governance and persistence framework**, not yet a mature forecasting model.

Future forecasting work should prioritize:
- explicit feature/signal construction;
- base-rate/reference-class inputs;
- analyst/model probability generation with traceable rationale;
- retrospective scoring on resolved forecasts;
- calibration by horizon/domain;
- comparison of model vs analyst vs combined forecasts;
- guardrails preventing false numerical precision.

### 3.8 Adaptive learning — LOW maturity

Existing source-drift logic is baseline threshold logic rather than a mature learning system.

Do not prioritize opaque self-modifying learning. First implement observable metrics and deterministic calibration loops:
- source reliability changes;
- adapter failure rates;
- extraction error rates;
- claim merge/split corrections;
- alert usefulness;
- forecast Brier/log scores;
- operator feedback.

Only then should automated policy adaptation be considered.

## 4. Product/operational gaps

### 4.1 The system is not yet an everyday intelligence product

The owner-only runtime can operate, but key user-value loops are incomplete:

`COLLECT -> VERIFY -> PRIORITIZE -> ALERT -> EXPLAIN -> REVIEW -> LEARN`

Collection and persistence exist, but the owner experience still depends heavily on direct repository/backend interaction and ChatGPT web research rather than a unified operational product.

### 4.2 Admin dashboard exists but is not deployed

E5 provides a read-only dashboard foundation, but it is `NOT_DEPLOYED`.

A safe owner-only operator surface would materially increase usefulness without requiring public publication.

Recommended approach:
- private access only;
- no public KGM application ingress;
- SSH tunnel / private overlay / other owner-only route after a security decision;
- preserve dashboard read-only semantics.

### 4.3 Backend Action exists but private GPT is not connected

E3 is locally validated but:
- HTTPS is not deployed;
- GPT Action is not connected.

This creates a split experience:
- ChatGPT is strong at current web research;
- KGM runtime contains persisted monitoring state;
- the two are not connected.

Before public publication, there is a strong case for an **owner-only sanitized/controlled connection** to persisted state if a secure private connectivity model can be established without exposing owner operational metadata publicly.

### 4.4 No operational notification/delivery layer

The repository has strategic alert persistence but no approved external notification provider.

For real monitoring value, the owner should not have to open the database/dashboard to discover urgent events.

A future delivery layer should support at minimum:
- priority-based notification policy;
- dedup/update/resolution notifications;
- delivery audit;
- failure/retry isolation;
- quiet-hours/escalation policy where appropriate;
- strict redaction/data-minimization rules.

Provider choice should remain a separate integration decision.

### 4.5 No real source-portfolio operations

A global monitor needs source portfolio management:
- source onboarding;
- source-class and region/language assignment;
- freshness SLA/objectives;
- parser/adapter health;
- source drift;
- replacement/fallback source;
- legal/licensing notes;
- provenance/origin characteristics;
- source reputation review.

The existing source registry and reputation foundations can support this, but the operator workflow needs to be built.

## 5. Documentation / architecture debt

The post-E9A canonical sync fixed ROADMAP/README/PROJECT_HISTORY, but some secondary canonical documents remain stale.

Examples:
- `ARCHITECTURE.md` still describes pre-E9A current state and the former E8 preflight activity;
- `SECURITY_AND_DATA_POLICY.md` still marks E9A.6 real-host/network evidence as pending even though E9A.6 is complete;
- `EXTERNAL_INTEGRATIONS.md` still reflects the controlled-pilot production-review boundary rather than the new candidate-ready runtime state.

This is not runtime failure, but it creates recovery/governance risk. The next roadmap should begin with a documentation/architecture convergence gate.

## 6. Security / operational decisions still unresolved

### 6.1 SSH exposure

Remaining explicit exception:
`TCP/22 from 0.0.0.0/0`.

For long-running owner operation, this should eventually be replaced or restricted by one of:
- fixed trusted IP/CIDR where practical;
- OCI Bastion;
- private overlay/VPN;
- another explicit private-admin path.

Do not change it without confirming the owner's real access/recovery requirements.

### 6.2 Broad egress

Broad outbound access is still an explicit exception.

Do not prematurely lock egress while source expansion is underway. First create an **egress inventory** from the actual approved source portfolio and OS/dependency requirements. Restrict only after the required destinations/protocols are known.

### 6.3 Backup location

The DR mechanism is validated but remains project-local and no off-host backup provider is active.

A single-host disaster can therefore still remove both runtime state and local backup copies.

A later owner-only production gate should evaluate encrypted off-host backup while preserving canonical storage ownership and secret isolation.

## 7. Maturity matrix

Scores are architectural assessment, not external certification.

| Capability | Maturity | Main reason |
| --- | --- | --- |
| Governance / truth boundaries | 9/10 | unusually explicit and regression-protected |
| Persistence / schema / history | 8.5/10 | strong durable project-local model |
| Runtime reliability | 8.5/10 | real ARM64/reboot/DR evidence |
| Security hardening | 7.5/10 | strong service sandbox; SSH/egress exceptions remain |
| Reproducibility | 8/10 | good instrumentation and hashing; not every research mode instrumented |
| Reporting | 8/10 | broad deterministic report environment |
| Coverage measurement | 8/10 | strong semantics; actual source universe still narrow |
| Source acquisition breadth | 3/10 | only two approved live integrations |
| Provenance/origin automation | 5/10 | good rules, but host-level origin remains too coarse for complex chains |
| Claim extraction/identity | 4/10 | live identity still heavily title-based |
| Verification reasoning | 4/10 | strong policy, simple executable engine |
| Contradiction reasoning | 2.5/10 | baseline data structure only |
| Graph substrate | 7/10 | strong persistence/query/lifecycle |
| Automated relationship inference | 3.5/10 | inference entry layer remains basic |
| Forecast governance/persistence | 8/10 | strong history/semantics/evaluation structure |
| Forecast probability generation | 3/10 | supplied probabilities are normalized rather than derived |
| Adaptive learning | 2.5/10 | baseline threshold logic |
| Operator dashboard | 5/10 | foundation exists, not deployed |
| ChatGPT/backend integration | 4/10 | backend exists; no HTTPS/Action connection |
| Alert delivery | 2/10 | persisted alerts exist; external delivery absent |
| Real global operational coverage | 2.5/10 | measurement framework exists; source portfolio is far from global |
| Public-product readiness | 5/10 | E8 planning exists, but should not be prioritized yet |

## 8. Strategic development options

### Option A — Publish/share soon

Path:
`E8 -> Business -> publication -> optional public facade`.

Advantages:
- fastest path to external visibility;
- validates public user interest.

Disadvantages:
- exposes a product whose analytical depth/source coverage is still weaker than its architecture suggests;
- risks confusing excellent safety semantics with high substantive monitoring coverage;
- creates support/security/privacy work before owner value is fully optimized.

Recommendation: **not first priority**.

### Option B — Build shared/team runtime now

Path:
`E9 shared storage / multi-user operations`.

Advantages:
- future team scalability.

Disadvantages:
- introduces distributed-state/concurrency/security complexity;
- solves a scale problem before the intelligence-quality/product loop is mature;
- conflicts with successful current `PROJECT_LOCAL_ONLY` simplicity.

Recommendation: **defer**.

### Option C — Intelligence-quality and owner-operationalization first

Path:
`source expansion -> semantic claims -> provenance/origin -> contradictions -> verification -> calibration -> operator experience -> notifications -> controlled live owner operation`.

Advantages:
- directly increases intelligence value;
- uses the strong runtime/persistence foundation already built;
- preserves owner-only security boundary;
- improves eventual public product rather than merely exposing the current one.

Disadvantages:
- requires deeper analytical engineering and more real-world validation;
- source onboarding has ongoing maintenance cost.

Recommendation: **preferred**.

## 9. Recommended architecture direction

Keep the current architectural spine and evolve intelligence inside it.

Do not replace:
- SQLite/project-local canonical storage yet;
- current monitoring runtime;
- current graph store merely for fashion/scale;
- current forecast/report persistence contracts;
- existing E3/E5 owner read surfaces.

Add incrementally:

`Source Portfolio -> Semantic Claim Layer -> Provenance/Origin Graph -> Evidence Relation Layer -> Contradiction Layer -> Verification Decision -> Intelligence Graph -> Forecast Signals -> Reports/Alerts`

Key design rule:
**LLM/model-assisted analysis may propose structured analytical objects, but canonical truth-state promotion must remain policy-controlled, provenance-bound, auditable and fail-closed.**

This is the most important architectural principle for the next generation of KGM.

## 10. Recommended development priority

### P0 — Canonical convergence

Synchronize ARCHITECTURE, SECURITY_AND_DATA_POLICY, EXTERNAL_INTEGRATIONS and supporting docs to post-E9A state.

### P1 — Source Network Expansion

Create scalable source-adapter/registry operations and expand public/free authoritative/local-language coverage before adding paid providers.

### P1 — Semantic Claim and Provenance Upgrade

Replace title-only claim identity with typed claims and explicit underlying-origin/citation/syndication relationships.

### P1 — Verification / Contradiction Engine v2

Implement evidence-type, independence, proximity, contradiction and uncertainty dimensions without weakening existing truth boundaries.

### P2 — Owner Operational Intelligence Mode

Deploy a safe owner-only dashboard/access path, recurring briefs and practical alert review workflow; retain `PRODUCTION_LIVE = NOT_OPERATIONAL` until a separate launch gate succeeds.

### P2 — Forecast Quality / Calibration

Turn forecast persistence into measurable forecasting capability using resolved historical predictions and calibration metrics.

### P2 — Notification / Delivery

Add one explicitly approved owner notification channel with fail-closed/redacted delivery and delivery audit.

### P3 — Adaptive Quality Loops

Use observed correction/error/performance metrics before any self-modifying behavior.

### P4 — E8 Publication

Revisit Business migration/publication only after owner operation demonstrates useful and stable intelligence output.

### P5 — E9 Shared Runtime

Revisit shared/team production only if there is a real multi-user/team need.

## 11. Recommended next roadmap decision

Approve a new development generation focused on **Operational Intelligence Quality and Source Expansion**, not publication or shared runtime.

Recommended first new numbered phase:

`Phase 12 — Intelligence Quality and Source Network Foundation`

This is appropriate now because the owner has explicitly requested creation of the next roadmap; the previous prohibition on inventing Phase 12 applied only while no new owner roadmap decision existed.

Recommended subsequent phases:
- Phase 13 — Semantic Verification and Provenance Intelligence;
- Phase 14 — Owner Operational Intelligence Activation;
- Phase 15 — Forecast Calibration and Performance Intelligence;
- Phase 16 — Delivery, Operator Experience and Quality Feedback;
- Phase 17 — Controlled External Publication Readiness (optional/owner-gated);
- Phase 18 — Shared/Team Runtime (optional/new architecture gate).

The next roadmap should explicitly keep Phase 17/18 inactive until separate owner gates and should not equate completion of Phase 14 with public production.

## 12. Final assessment

KGM is not an immature project. It is a **mature engineering skeleton with a partially mature intelligence brain**.

The correct next investment is to make its analytical core and real source portfolio catch up with the excellent governance, persistence and runtime foundation already built.

Primary strategic recommendation:

`DO NOT REPLATFORM.`

`DO NOT PUBLISH FIRST.`

`DO NOT BUILD SHARED RUNTIME FIRST.`

`DEEPEN INTELLIGENCE + EXPAND SOURCES + OPERATIONALIZE OWNER VALUE.`
