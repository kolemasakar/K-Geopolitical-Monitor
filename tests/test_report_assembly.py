from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.advanced_forecasting import ForecastRecord, ScenarioVersion, SQLiteAdvancedForecastRepository, forecast_version_id
from kgeopolitical_monitor.forecast_inputs import GRAPH_RELATIONSHIP, SOURCE_EVIDENCE, ForecastInputRef, SQLiteForecastInputRepository, create_forecast_version_with_inputs
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType
from kgeopolitical_monitor.report_assembly import ReportAssembler, ReportAssemblyRequest
from kgeopolitical_monitor.reporting_environment import ANALYST_ASSUMPTION, CLAIM, COVERAGE_METADATA, COVERAGE_REPORT, FINDING, FORECAST, FORECAST_SCENARIO, FORECAST_VERSION, GLOBAL_GEOPOLITICAL_BRIEF, GRAPH_EDGE, GRAPH_INFERENCE, RAW_ITEM, SCENARIO_VERSION, SOURCE, ReportSnapshot

NOW = datetime(2026, 8, 26, 18, 30, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)


def _seed(db):
    assembler = ReportAssembler(db)
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO sources(id,name,source_class,reliability) VALUES ('source-1','Official source','Official','HIGH')")
        c.execute("INSERT INTO raw_items(id,source_id,title,content,collected_at) VALUES ('raw-1','source-1','Update','Observed content',?)", (NOW.isoformat(),))
        c.execute("INSERT INTO claims(id,event_id,text,confidence) VALUES ('claim-1',NULL,'Observed claim','0.70')")
        c.execute("INSERT INTO operational_findings(finding_id,run_id,watch_id,title,summary,importance,confidence,evidence_refs,explanation,created_at) VALUES ('finding-1','run-1','watch-1','Material change','Observed material change',0.82,0.71,'[\"claim:claim-1\",\"raw_item:raw-1\"]','Upstream finding semantics preserved',?)", (NOW.isoformat(),))
        c.execute("INSERT INTO strategic_alerts(alert_id,watch_id,finding_id,trigger_type,dedup_key,priority,status,first_triggered_at,last_updated_at,evidence_refs,explanation,invalidation_reason) VALUES ('alert-1','watch-1','finding-1','QUALIFYING_FINDING','material-change','HIGH','OPEN',?,?,'[\"claim:claim-1\",\"raw_item:raw-1\"]','Priority does not modify evidence confidence',NULL)", (NOW.isoformat(), NOW.isoformat()))
        c.execute("INSERT INTO region_language_coverage_reports(report_id,watch_id,required_scopes,observed_scopes,observed_regions,observed_languages,missing_scopes,coverage_ratio,created_at) VALUES ('coverage-1','watch-1','[\"R:en\"]','[\"R:en\"]','[\"R\"]','[\"en\"]','[]',1.0,?)", (NOW.isoformat(),))
        c.execute("INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,relation_type,relation_class,confidence,status,valid_from,valid_to,first_observed_at,last_observed_at,explanation,created_at,updated_at) VALUES ('edge-1','node-a','node-b','INFLUENCES','INFLUENCE',0.74,'ACTIVE',?,NULL,?,?,?, ?,?)", (NOW.isoformat(), NOW.isoformat(), NOW.isoformat(), 'Analytical graph relation', NOW.isoformat(), NOW.isoformat()))

    forecasts = SQLiteAdvancedForecastRepository(db)
    forecast = ForecastRecord.create('reporting-target-30d','Will the target condition occur within 30 days?',ForecastHorizon.SHORT,DEADLINE,created_at=NOW)
    forecasts.save_forecast(forecast)
    version_id = forecast_version_id(forecast.forecast_id, 1)
    inputs = (
        ForecastInputRef.durable(version_id, SOURCE_EVIDENCE, 'raw-1', created_at=NOW),
        ForecastInputRef.durable(version_id, GRAPH_RELATIONSHIP, 'edge-1', metadata={'independent_evidence': False}, created_at=NOW),
    )
    version = create_forecast_version_with_inputs(forecast.forecast_id,1,inputs=inputs,constraints=('project-local inputs only',),change_reason='Initial report integration',created_at=NOW)
    scenarios = (
        ScenarioVersion.create(version.forecast_version_id,ScenarioType.BASELINE,'Condition occurs',0.6,0.55,0.7),
        ScenarioVersion.create(version.forecast_version_id,ScenarioType.NEGATIVE,'Condition does not occur',0.4,0.45,0.65),
    )
    forecasts.save_version(version, scenarios)
    SQLiteForecastInputRepository(db).bind(version, inputs, constraints=('project-local inputs only',))
    return assembler, forecast, version, scenarios


def _request(version):
    snapshot = ReportSnapshot.create(GLOBAL_GEOPOLITICAL_BRIEF,'global:m13.2','Global brief','Integrated validated snapshot',NOW,created_at=NOW,generator_version='m13.2')
    return ReportAssemblyRequest(snapshot=snapshot,finding_ids=('finding-1',),alert_ids=('alert-1',),coverage_report_ids=('coverage-1',),graph_edge_ids=('edge-1',),forecast_version_ids=(version.forecast_version_id,),assumptions=('Target conditions remain observable',))


def _source_kinds(bundle):
    section = next(s for s in bundle.sections if s.section_type == 'SOURCES')
    return {r.reference_kind for r in bundle.references if r.section_id == section.section_id}


def test_full_report_uses_one_common_typed_contract(tmp_path):
    assembler, forecast, version, scenarios = _seed(tmp_path / 'project.db')
    bundle = assembler.assemble(_request(version))
    assert [s.section_type for s in bundle.sections] == ['FINDINGS','ALERTS','COVERAGE','RELATIONSHIPS','FORECAST','ASSUMPTIONS','SOURCES']
    classes = {s.section_type: s.presentation_class for s in bundle.sections}
    assert classes['COVERAGE'] == COVERAGE_METADATA
    assert classes['RELATIONSHIPS'] == GRAPH_INFERENCE
    assert classes['FORECAST'] == FORECAST_SCENARIO
    refs = {(r.reference_kind,r.reference_value,r.reference_role) for r in bundle.references}
    assert (FINDING,'finding-1','ANALYTICAL_INPUT') in refs
    assert (COVERAGE_REPORT,'coverage-1','COVERAGE_INPUT') in refs
    assert (FORECAST,forecast.forecast_id,'FORECAST_INPUT') in refs
    assert (FORECAST_VERSION,version.forecast_version_id,'FORECAST_VERSION') in refs
    assert all((SCENARIO_VERSION,s.scenario_version_id,'SCENARIO') in refs for s in scenarios)
    assert (ANALYST_ASSUMPTION,'Target conditions remain observable','ASSUMPTION') in refs
    assert _source_kinds(bundle) == {SOURCE,RAW_ITEM,CLAIM}


def test_forecast_source_evidence_and_graph_context_are_separate(tmp_path):
    assembler, _, version, _ = _seed(tmp_path / 'project.db')
    refs = {(r.reference_kind,r.reference_value,r.reference_role) for r in assembler.assemble(_request(version)).references}
    assert (RAW_ITEM,'raw-1','FORECAST_SOURCE_EVIDENCE') in refs
    assert (GRAPH_EDGE,'edge-1','FORECAST_GRAPH_CONTEXT') in refs
    assert (GRAPH_EDGE,'edge-1','FORECAST_SOURCE_EVIDENCE') not in refs


def test_alert_only_and_forecast_only_reports_have_source_provenance_without_graph_promotion(tmp_path):
    db = tmp_path / 'project.db'
    assembler, _, version, _ = _seed(db)
    alert_snapshot = ReportSnapshot.create(GLOBAL_GEOPOLITICAL_BRIEF,'global:alert-only','Alert-only brief','Alert evidence provenance',NOW,created_at=NOW,generator_version='m13.2')
    alert_bundle = assembler.assemble(ReportAssemblyRequest(snapshot=alert_snapshot,alert_ids=('alert-1',)),persist=False)
    assert _source_kinds(alert_bundle) == {SOURCE,RAW_ITEM,CLAIM}

    forecast_snapshot = ReportSnapshot.create(GLOBAL_GEOPOLITICAL_BRIEF,'global:forecast-only','Forecast-only brief','Forecast evidence provenance',NOW,created_at=NOW,generator_version='m13.2')
    forecast_bundle = assembler.assemble(ReportAssemblyRequest(snapshot=forecast_snapshot,forecast_version_ids=(version.forecast_version_id,)),persist=False)
    assert _source_kinds(forecast_bundle) == {SOURCE,RAW_ITEM}
    source_section = next(s for s in forecast_bundle.sections if s.section_type == 'SOURCES')
    assert all(not (r.section_id == source_section.section_id and r.reference_kind == GRAPH_EDGE) for r in forecast_bundle.references)
    assert any(r.reference_kind == GRAPH_EDGE and r.reference_role == 'FORECAST_GRAPH_CONTEXT' for r in forecast_bundle.references)


def test_assembly_is_idempotent_restart_safe_and_read_only_upstream(tmp_path):
    db = tmp_path / 'project.db'
    assembler, _, version, _ = _seed(db)
    request = _request(version)
    with sqlite3.connect(db) as c:
        before = c.execute("SELECT title,importance,confidence,evidence_refs FROM operational_findings WHERE finding_id='finding-1'").fetchone(), c.execute("SELECT priority,status,evidence_refs FROM strategic_alerts WHERE alert_id='alert-1'").fetchone(), c.execute("SELECT confidence,status FROM graph_edges WHERE edge_id='edge-1'").fetchone(), c.execute("SELECT version_number,change_reason FROM forecast_versions WHERE forecast_version_id=?",(version.forecast_version_id,)).fetchone()
    first = assembler.assemble(request)
    second = assembler.assemble(request)
    restarted = ReportAssembler(db).repository.get_bundle(request.snapshot.report_id)
    with sqlite3.connect(db) as c:
        after = c.execute("SELECT title,importance,confidence,evidence_refs FROM operational_findings WHERE finding_id='finding-1'").fetchone(), c.execute("SELECT priority,status,evidence_refs FROM strategic_alerts WHERE alert_id='alert-1'").fetchone(), c.execute("SELECT confidence,status FROM graph_edges WHERE edge_id='edge-1'").fetchone(), c.execute("SELECT version_number,change_reason FROM forecast_versions WHERE forecast_version_id=?",(version.forecast_version_id,)).fetchone()
    assert first == second == restarted
    assert before == after


@pytest.mark.parametrize(('field','missing'), [('finding_ids','finding-x'),('alert_ids','alert-x'),('coverage_report_ids','coverage-x'),('graph_edge_ids','edge-x'),('forecast_version_ids','forecast-version-x')])
def test_assembly_fails_closed_on_unknown_inputs(tmp_path, field, missing):
    db = tmp_path / 'project.db'
    assembler, _, version, _ = _seed(db)
    base = _request(version)
    values = dict(snapshot=base.snapshot,finding_ids=(),alert_ids=(),coverage_report_ids=(),graph_node_ids=(),graph_edge_ids=(),forecast_version_ids=(),assumptions=())
    values[field] = (missing,)
    with pytest.raises(ValueError, match='unknown'):
        assembler.assemble(ReportAssemblyRequest(**values))
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM report_snapshots').fetchone()[0] == 0


def test_assembly_requires_validated_input_and_supports_non_persisting_preview(tmp_path):
    db = tmp_path / 'project.db'
    assembler, _, version, _ = _seed(db)
    empty = ReportSnapshot.create(GLOBAL_GEOPOLITICAL_BRIEF,'global:empty','Empty brief','No inputs',NOW,created_at=NOW,generator_version='m13.2')
    with pytest.raises(ValueError, match='at least one validated input'):
        assembler.assemble(ReportAssemblyRequest(snapshot=empty))
    request = _request(version)
    assert assembler.assemble(request,persist=False) == assembler.assemble(request,persist=False)
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM report_snapshots').fetchone()[0] == 0
