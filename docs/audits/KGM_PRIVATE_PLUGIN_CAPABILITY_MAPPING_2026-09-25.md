# Private KGM Plugin — repository capability mapping (2026-09-25)

Status: SOURCE AUDIT / NO RUNTIME ACTIVATION. Inspected canonical main source modules, not assumed deployed SHA. No tests run.

| Proposed tool | Existing code evidence | Mapping / gap |
|---|---|---|
| kgm_get_status | `backend_action_api.BackendStateReader.state_summary`, `monitoring_runs`, `source_collection_attempts`, `degraded_sources`, `latest_coverage`; `runtime_health.RuntimeHealthStore.latest` | Strong existing read-model basis. Need sanitized unified projection and separately verified deployed schema/version. |
| kgm_get_brief | `report_briefs.BriefReportService.global_brief`, `regional_brief` | Existing report services. Verify side effects, prerequisites, report freshness and runtime availability before allowing as read-only plugin calls; consider persisted brief read model instead. |
| kgm_get_events | `intelligence_query.IntelligenceQuery.actor_events`, `query`; `backend_action_api.BackendStateReader.recent_alerts` | Query capabilities exist but no verified bounded global event-search interface; design an indexed bounded read projection rather than equating alerts with all events. |
| kgm_get_evidence | `evidence_repository.EvidenceRepository.get`; `backend_action_api.BackendStateReader.alert_detail` | Existing retrieval basis; verify authorization, provenance joins and bounded public-safe serialization. Evidence lookup alone does not imply independent corroboration. |

Existing `backend_action_api.create_action_app` defines `/health`, authenticated `/v1/state/summary`, `/v1/alerts`, alert detail, watches, monitoring runs, source collection, degraded sources, coverage and forecasts. **This is repository code, NOT evidence of a currently deployed/reachable HTTP API.** The historical Action naming does not authorize public deployment or make it the final Plugin transport.

## Next bounded implementation gate
1. Read source bodies and tests for `BackendStateReader`, `BriefReportService`, `IntelligenceQuery` and evidence/provenance projections. Confirm actual read-only semantics, no generation-side mutations, input limits, failure states and authorization.
2. Implement a standalone internal adapter for status first using existing read model and sanitized output. Unit-test with synthetic fixtures; do not connect to production DB.
3. Map and test brief, events, evidence incrementally; preserve source-vs-fact and provenance constraints.
4. Separately decide supported private Plugin transport and server-side owner authentication; no public ingress or new secrets before explicit approval.

No GitHub Actions required for this audit. No RDC dependence in final Plugin architecture.
