from datetime import datetime, timedelta, timezone
import json
import sqlite3

import pytest

from kgeopolitical_monitor.advanced_forecasting import ForecastRecord, ScenarioVersion, SQLiteAdvancedForecastRepository, forecast_version_id
from kgeopolitical_monitor.forecast_evaluation import BINARY_ONE_VS_REST, BINARY_ONE_VS_REST_VERSION, evaluation_id, outcome_id
from kgeopolitical_monitor.forecast_inputs import SOURCE_EVIDENCE, ForecastInputRef, SQLiteForecastInputRepository, create_forecast_version_with_inputs
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType
from kgeopolitical_monitor.report_forecasts import ForecastReportSelection, ForecastReportingService, StrategicOutlookSelection
from kgeopolitical_monitor.reporting_environment import FORECAST_REPORT, FORECAST_SCENARIO, FORECAST_VERSION, STRATEGIC_OUTLOOK

NOW = datetime(2026, 8, 26, 20, 0, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)


def _seed(db, with_history=True):
    service = ForecastReportingService(db)
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO sources(id,name,source_class,reliability) VALUES ('source-1','Source','Official','HIGH')")
        c.execute("INSERT INTO raw_items(id,source_id,title,content,collected_at) VALUES ('raw-1','source-1','Update','Observed content',?)", (NOW.isoformat(),))
        c.execute("INSERT INTO operational_findings(finding_id,run_id,watch_id,title,summary,importance,confidence,evidence_refs,explanation,created_at) VALUES ('finding-1','run-1','watch-1','Finding','Summary',0.8,0.7,'[\"raw_item:raw-1\"]','Finding explanation',?)", (NOW.isoformat(),))

    repo = SQLiteAdvancedForecastRepository(db)
    forecast = ForecastRecord.create('forecast-report-target','Will the target condition occur within 30 days?',ForecastHorizon.SHORT,DEADLINE,created_at=NOW)
    repo.save_forecast(forecast)
    vid = forecast_version_id(forecast.forecast_id, 1)
    inputs = (ForecastInputRef.durable(vid,SOURCE_EVIDENCE,'raw-1',created_at=NOW),)
    version = create_forecast_version_with_inputs(forecast.forecast_id,1,inputs=inputs,constraints=('project-local inputs only',),change_reason='Initial version',created_at=NOW)
    scenarios = (
        ScenarioVersion.create(vid,ScenarioType.BASELINE,'Condition occurs',0.6,0.55,0.7,uncertainty_factors=('Timing',),invalidation_signals=('Formal cancellation',)),
        ScenarioVersion.create(vid,ScenarioType.NEGATIVE,'Condition does not occur',0.4,0.45,0.65,uncertainty_factors=('Private information',),invalidation_signals=('Condition confirmed',)),
    )
    repo.save_version(version, scenarios)
    SQLiteForecastInputRepository(db).bind(version, inputs, constraints=('project-local inputs only',))

    if with_history:
        oid = outcome_id(forecast.forecast_id)
        sid = scenarios[0].scenario_version_id
        eid = evaluation_id(oid, sid, BINARY_ONE_VS_REST, BINARY_ONE_VS_REST_VERSION)
        with sqlite3.connect(db) as c:
            c.execute("INSERT INTO forecast_outcomes(outcome_id,forecast_id,resolved_at,outcome_state,observed_scenario_type,evidence_refs_json,explanation,created_at) VALUES (?,?,?,'OBSERVED','baseline',?,'Observed outcome explanation',?)", (oid,forecast.forecast_id,NOW.isoformat(),json.dumps(['raw-1']),NOW.isoformat()))
            c.execute("INSERT INTO forecast_evaluations(evaluation_id,outcome_id,forecast_id,forecast_version_id,scenario_version_id,horizon,scenario_type,scenario_label,raw_probability,calibrated_probability,observed_value,brier_score_raw,brier_score_calibrated,calibration_error_raw,calibration_error_calibrated,evaluation_method,evaluation_method_version,sample_count,evaluated_at) VALUES (?,?,?,?,?,'short_term','baseline','Condition occurs',0.6,0.55,1.0,0.16,0.2025,0.4,0.45,?,?,1,?)", (eid,oid,forecast.forecast_id,vid,sid,BINARY_ONE_VS_REST,BINARY_ONE_VS_REST_VERSION,NOW.isoformat()))
            c.execute("INSERT INTO forecast_calibration_runs(calibration_id,calibration_method,calibration_method_version,evaluation_method,evaluation_method_version,cohort_horizon,cohort_scenario_type,min_sample_count,sample_count,evaluation_ids_json,raw_mean_probability,calibrated_mean_probability,observed_frequency,raw_brier_mean,calibrated_brier_mean,raw_calibration_error_mean,calibrated_calibration_error_mean,created_at) VALUES ('calibration-1','EMPIRICAL_CALIBRATION_REPORT','1',?,?,'short_term','baseline',1,1,?,0.6,0.55,1.0,0.16,0.2025,0.4,0.45,?)", (BINARY_ONE_VS_REST,BINARY_ONE_VS_REST_VERSION,json.dumps([eid]),NOW.isoformat()))
            c.execute("INSERT INTO forecast_calibration_buckets(calibration_id,probability_basis,bucket_index,bucket_lower,bucket_upper,sample_count,mean_probability,observed_frequency,mean_brier_score,mean_calibration_error) VALUES ('calibration-1','RAW',0,0.5,0.7,1,0.6,1.0,0.16,0.4),('calibration-1','CALIBRATED',0,0.5,0.7,1,0.55,1.0,0.2025,0.45)")
    return service, forecast, version, scenarios


def _section(bundle, kind):
    return next(item for item in bundle.sections if item.section_type == kind)


def test_forecast_report_is_version_anchored_and_exposes_scenario_uncertainty_invalidation(tmp_path):
    service, forecast, version, scenarios = _seed(tmp_path / 'project.db', with_history=False)
    bundle = service.forecast_report(version.forecast_version_id, ForecastReportSelection(finding_ids=('finding-1',)), title='Forecast report', summary='Versioned forecast snapshot.', as_of=NOW, persist=False)

    assert bundle.snapshot.report_type == FORECAST_REPORT
    assert bundle.snapshot.subject_ref_type == FORECAST_VERSION
    assert bundle.snapshot.subject_ref_id == version.forecast_version_id
    assert bundle.snapshot.scope_key == f'forecast:{forecast.forecast_id}|version:1'
    assert _section(bundle,'FORECAST').presentation_class == FORECAST_SCENARIO
    assert _section(bundle,'UNCERTAINTY').presentation_class == FORECAST_SCENARIO
    assert _section(bundle,'INVALIDATION_SIGNALS').presentation_class == FORECAST_SCENARIO
    assert {item['scenario_version_id'] for item in _section(bundle,'UNCERTAINTY').content['scenarios']} == {item.scenario_version_id for item in scenarios}
    assert _section(bundle,'UNCERTAINTY').content['scenarios'][0].get('uncertainty_factors') is not None
    assert _section(bundle,'INVALIDATION_SIGNALS').content['scenarios'][0].get('invalidation_signals') is not None
    assert all(section.presentation_class != 'OBSERVED_FACT' for section in bundle.sections if section.section_type in {'FORECAST','UNCERTAINTY','INVALIDATION_SIGNALS'})


def test_forecast_report_includes_available_outcome_evaluation_and_calibration_history(tmp_path):
    service, _, version, _ = _seed(tmp_path / 'project.db', with_history=True)
    bundle = service.forecast_report(version.forecast_version_id, ForecastReportSelection(), title='Forecast report', summary='Historical evaluation available.', as_of=NOW, persist=False)

    outcome = _section(bundle,'OUTCOME_EVALUATION').content['history'][0]
    calibration = _section(bundle,'CALIBRATION_HISTORY').content['history'][0]
    assert outcome['outcome_state'] == 'OBSERVED'
    assert outcome['evaluations'][0]['forecast_version_id'] == version.forecast_version_id
    assert outcome['evaluations'][0]['raw_probability'] == 0.6
    assert calibration['calibration_id'] == 'calibration-1'
    assert calibration['sample_count'] == 1
    assert {item['probability_basis'] for item in calibration['buckets']} == {'RAW','CALIBRATED'}


def test_missing_history_is_omitted_not_invented(tmp_path):
    service, _, version, _ = _seed(tmp_path / 'project.db', with_history=False)
    bundle = service.forecast_report(version.forecast_version_id, ForecastReportSelection(), title='Forecast report', summary='No historical outcome yet.', as_of=NOW, persist=False)
    assert 'OUTCOME_EVALUATION' not in {item.section_type for item in bundle.sections}
    assert 'CALIBRATION_HISTORY' not in {item.section_type for item in bundle.sections}


def test_strategic_outlook_is_scope_only_explicit_forecast_composition(tmp_path):
    service, _, version, _ = _seed(tmp_path / 'project.db', with_history=False)
    selection = StrategicOutlookSelection(forecast_version_ids=(version.forecast_version_id,), finding_ids=('finding-1',), assumptions=('Conditions remain monitorable',))
    bundle = service.strategic_outlook(selection, title='Strategic outlook', summary='Selected scenario outlook.', as_of=NOW, persist=False)

    assert bundle.snapshot.report_type == STRATEGIC_OUTLOOK
    assert bundle.snapshot.subject_ref_type is None
    assert bundle.snapshot.subject_ref_id is None
    assert {item.section_type for item in bundle.sections}.issuperset({'FINDINGS','FORECAST','UNCERTAINTY','INVALIDATION_SIGNALS','ASSUMPTIONS','SOURCES'})


def test_strategic_outlook_requires_explicit_forecast_version_and_unknown_version_fails_closed(tmp_path):
    service, _, _, _ = _seed(tmp_path / 'project.db', with_history=False)
    with pytest.raises(ValueError, match='at least one explicit forecast version'):
        StrategicOutlookSelection(forecast_version_ids=())
    with pytest.raises(ValueError, match='unknown forecast version'):
        service.strategic_outlook(StrategicOutlookSelection(forecast_version_ids=('forecast-version-x',)), title='Outlook', summary='Summary', as_of=NOW, persist=False)
    with pytest.raises(ValueError, match='unknown forecast version'):
        service.forecast_report('forecast-version-x', ForecastReportSelection(), title='Forecast', summary='Summary', as_of=NOW, persist=False)


def test_reporting_does_not_mutate_forecast_probabilities_outcome_or_calibration(tmp_path):
    db = tmp_path / 'project.db'
    service, _, version, _ = _seed(db, with_history=True)
    with sqlite3.connect(db) as c:
        before = c.execute("SELECT raw_probability,calibrated_probability,scenario_confidence FROM forecast_scenario_versions WHERE forecast_version_id=? ORDER BY scenario_version_id",(version.forecast_version_id,)).fetchall(), c.execute("SELECT outcome_state,evidence_refs_json FROM forecast_outcomes").fetchall(), c.execute("SELECT sample_count,raw_mean_probability,calibrated_mean_probability FROM forecast_calibration_runs").fetchall()
    service.forecast_report(version.forecast_version_id, ForecastReportSelection(), title='Forecast report', summary='Summary', as_of=NOW, persist=False)
    with sqlite3.connect(db) as c:
        after = c.execute("SELECT raw_probability,calibrated_probability,scenario_confidence FROM forecast_scenario_versions WHERE forecast_version_id=? ORDER BY scenario_version_id",(version.forecast_version_id,)).fetchall(), c.execute("SELECT outcome_state,evidence_refs_json FROM forecast_outcomes").fetchall(), c.execute("SELECT sample_count,raw_mean_probability,calibrated_mean_probability FROM forecast_calibration_runs").fetchall()
    assert before == after
