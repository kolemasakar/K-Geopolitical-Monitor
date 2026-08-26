from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.report_briefs import BriefReportService, BriefSelection
from kgeopolitical_monitor.reporting_environment import ALERT, GLOBAL_GEOPOLITICAL_BRIEF, REGION, REGIONAL_COUNTRY_BRIEF, STRATEGIC_ALERT

NOW = datetime(2026, 8, 26, 19, 0, tzinfo=timezone.utc)


def _seed(db):
    service = BriefReportService(db)
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO sources(id,name,source_class,reliability) VALUES ('source-1','Source','Official','HIGH')")
        c.execute("INSERT INTO raw_items(id,source_id,title,content,collected_at) VALUES ('raw-1','source-1','Update','Observed content',?)", (NOW.isoformat(),))
        c.execute("INSERT INTO claims(id,event_id,text,confidence) VALUES ('claim-1',NULL,'Observed claim','0.70')")
        for finding_id, title, importance in (('finding-1','Selected finding',0.8),('finding-2','Unselected finding',0.6)):
            c.execute("INSERT INTO operational_findings(finding_id,run_id,watch_id,title,summary,importance,confidence,evidence_refs,explanation,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", (finding_id,'run-'+finding_id,'watch-1',title,'Persisted summary',importance,0.7,'[\"claim:claim-1\",\"raw_item:raw-1\"]','Persisted explanation',NOW.isoformat()))
        c.execute("INSERT INTO strategic_alerts(alert_id,watch_id,finding_id,trigger_type,dedup_key,priority,status,first_triggered_at,last_updated_at,evidence_refs,explanation,invalidation_reason) VALUES ('alert-1','watch-1','finding-1','QUALIFYING_FINDING','selected-finding','HIGH','OPEN',?,?,'[\"claim:claim-1\",\"raw_item:raw-1\"]','Alert explanation',NULL)", (NOW.isoformat(),NOW.isoformat()))
        c.execute("INSERT INTO region_catalog(region_code,name,region_group,created_at) VALUES ('UA','Ukraine','EUROPE',?),('PL','Poland','EUROPE',?)", (NOW.isoformat(),NOW.isoformat()))
        c.execute("INSERT INTO language_catalog(language_code,name,created_at) VALUES ('uk','Ukrainian',?),('en','English',?),('pl','Polish',?)", (NOW.isoformat(),NOW.isoformat(),NOW.isoformat()))
        c.execute("INSERT INTO region_language_coverage_reports(report_id,watch_id,required_scopes,observed_scopes,observed_regions,observed_languages,missing_scopes,coverage_ratio,created_at) VALUES ('coverage-ua','watch-1','[\"UA:en\",\"UA:uk\"]','[\"UA:uk\"]','[\"UA\"]','[\"uk\"]','[\"UA:en\"]',0.5,?)", (NOW.isoformat(),))
        c.execute("INSERT INTO region_language_coverage_reports(report_id,watch_id,required_scopes,observed_scopes,observed_regions,observed_languages,missing_scopes,coverage_ratio,created_at) VALUES ('coverage-pl','watch-1','[\"PL:pl\"]','[\"PL:pl\"]','[\"PL\"]','[\"pl\"]','[]',1.0,?)", (NOW.isoformat(),))
    return service


def _finding_ids(bundle):
    section = next(s for s in bundle.sections if s.section_type == 'FINDINGS')
    return [item['finding_id'] for item in section.content['findings']]


def _coverage(bundle):
    section = next(s for s in bundle.sections if s.section_type == 'COVERAGE')
    return section.content['coverage_reports'][0]


def test_strategic_alert_brief_is_anchored_to_canonical_alert_and_finding(tmp_path):
    service = _seed(tmp_path / 'project.db')
    bundle = service.strategic_alert_report('alert-1', as_of=NOW, persist=False)

    assert bundle.snapshot.report_type == STRATEGIC_ALERT
    assert bundle.snapshot.subject_ref_type == ALERT
    assert bundle.snapshot.subject_ref_id == 'alert-1'
    assert bundle.snapshot.title == 'Strategic alert: Selected finding'
    assert _finding_ids(bundle) == ['finding-1']
    assert {s.section_type for s in bundle.sections} == {'FINDINGS','ALERTS','SOURCES'}


def test_global_brief_uses_only_explicit_selection_and_preserves_incomplete_coverage(tmp_path):
    service = _seed(tmp_path / 'project.db')
    selection = BriefSelection(finding_ids=('finding-1',), coverage_report_ids=('coverage-ua',))
    bundle = service.global_brief(selection, title='Global brief', summary='Explicit selected scope.', as_of=NOW, persist=False)

    assert bundle.snapshot.report_type == GLOBAL_GEOPOLITICAL_BRIEF
    assert bundle.snapshot.subject_ref_type is None
    assert _finding_ids(bundle) == ['finding-1']
    coverage = _coverage(bundle)
    assert coverage['coverage_ratio'] == 0.5
    assert coverage['missing_scopes'] == ['UA:en']
    assert 'global_complete' not in coverage
    assert bundle.snapshot.summary == 'Explicit selected scope.'


def test_global_brief_rejects_coverage_only_or_implicit_database_selection(tmp_path):
    service = _seed(tmp_path / 'project.db')
    with pytest.raises(ValueError, match='explicit finding, alert or forecast-version selection'):
        service.global_brief(BriefSelection(coverage_report_ids=('coverage-ua',)), title='Global brief', summary='No explicit intelligence.', as_of=NOW, persist=False)


def test_regional_brief_requires_canonical_region_languages_and_matching_coverage(tmp_path):
    service = _seed(tmp_path / 'project.db')
    selection = BriefSelection(finding_ids=('finding-1',), coverage_report_ids=('coverage-ua',))
    bundle = service.regional_brief('ua', ('uk','en'), selection, title='Regional brief', summary='Regional selected scope.', as_of=NOW, persist=False)

    assert bundle.snapshot.report_type == REGIONAL_COUNTRY_BRIEF
    assert bundle.snapshot.subject_ref_type == REGION
    assert bundle.snapshot.subject_ref_id == 'UA'
    assert bundle.snapshot.scope_key == 'region:UA|languages:en,uk'
    assert _coverage(bundle)['coverage_ratio'] == 0.5
    assert _coverage(bundle)['missing_scopes'] == ['UA:en']


def test_regional_brief_rejects_missing_or_mismatched_coverage(tmp_path):
    service = _seed(tmp_path / 'project.db')
    with pytest.raises(ValueError, match='requires region-language coverage metadata'):
        service.regional_brief('UA', ('uk',), BriefSelection(finding_ids=('finding-1',)), title='Regional', summary='Summary', as_of=NOW, persist=False)

    with pytest.raises(ValueError, match='does not cover requested regional scope'):
        service.regional_brief('UA', ('uk',), BriefSelection(finding_ids=('finding-1',), coverage_report_ids=('coverage-pl',)), title='Regional', summary='Summary', as_of=NOW, persist=False)


@pytest.mark.parametrize(('region','languages','message'), [('XX',('en',),'unknown region'),('UA',('xx',),'unknown language')])
def test_regional_brief_fails_closed_on_unknown_scope_metadata(tmp_path, region, languages, message):
    service = _seed(tmp_path / 'project.db')
    with pytest.raises(ValueError, match=message):
        service.regional_brief(region, languages, BriefSelection(finding_ids=('finding-1',), coverage_report_ids=('coverage-ua',)), title='Regional', summary='Summary', as_of=NOW, persist=False)


def test_brief_facade_does_not_mutate_upstream_finding_or_coverage_state(tmp_path):
    db = tmp_path / 'project.db'
    service = _seed(db)
    with sqlite3.connect(db) as c:
        before = c.execute("SELECT importance,confidence,evidence_refs FROM operational_findings WHERE finding_id='finding-1'").fetchone(), c.execute("SELECT coverage_ratio,missing_scopes FROM region_language_coverage_reports WHERE report_id='coverage-ua'").fetchone()
    service.regional_brief('UA', ('uk','en'), BriefSelection(finding_ids=('finding-1',), coverage_report_ids=('coverage-ua',)), title='Regional', summary='Summary', as_of=NOW, persist=False)
    with sqlite3.connect(db) as c:
        after = c.execute("SELECT importance,confidence,evidence_refs FROM operational_findings WHERE finding_id='finding-1'").fetchone(), c.execute("SELECT coverage_ratio,missing_scopes FROM region_language_coverage_reports WHERE report_id='coverage-ua'").fetchone()
    assert before == after
