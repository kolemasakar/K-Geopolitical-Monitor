from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.report_dossiers import DossierStorylineSelection, DossierStorylineService
from kgeopolitical_monitor.reporting_environment import ANALYTICAL_CONTEXT, CLAIM, EVENT, EVENT_DOSSIER, GRAPH_EDGE, RAW_ITEM, STORYLINE_REPORT

NOW = datetime(2026, 8, 26, 19, 30, tzinfo=timezone.utc)


def _seed(db):
    service = DossierStorylineService(db)
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO sources(id,name,source_class,reliability) VALUES ('source-1','Source one','Official','HIGH'),('source-2','Source two','Media','MEDIUM')")
        c.execute("INSERT INTO raw_items(id,source_id,title,content,collected_at) VALUES ('raw-1','source-1','First observation','Body one',?),('raw-2','source-2','Second observation','Body two',?)", (NOW.isoformat(), NOW.replace(minute=35).isoformat()))
        c.execute("INSERT INTO events(id,title,status,importance) VALUES ('event-1','Event one','ACTIVE','HIGH'),('event-2','Event two','ACTIVE','MEDIUM')")
        c.execute("INSERT INTO claims(id,event_id,text,confidence) VALUES ('claim-1','event-1','Claim one','0.70'),('claim-2','event-1','Claim two','0.60')")
        c.execute("INSERT INTO operational_findings(finding_id,run_id,watch_id,title,summary,importance,confidence,evidence_refs,explanation,created_at) VALUES ('finding-1','run-1','watch-1','Finding one','Summary one',0.8,0.7,'[\"claim:claim-1\",\"raw_item:raw-1\"]','Finding explanation',?)", (NOW.isoformat(),))
        c.execute("INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,relation_type,relation_class,confidence,status,valid_from,valid_to,first_observed_at,last_observed_at,explanation,created_at,updated_at) VALUES ('edge-1','node-a','node-b','INFLUENCES','INFLUENCE',0.72,'ACTIVE',?,NULL,?,?,?, ?,?)", (NOW.isoformat(), NOW.isoformat(), NOW.isoformat(), 'Graph context', NOW.isoformat(), NOW.isoformat()))
    return service


def _section(bundle, section_type):
    return next(item for item in bundle.sections if item.section_type == section_type)


def test_event_dossier_is_anchored_to_canonical_event_and_explicit_refs(tmp_path):
    service = _seed(tmp_path / 'project.db')
    selection = DossierStorylineSelection(claim_ids=('claim-1',), raw_item_ids=('raw-1',), finding_ids=('finding-1',), graph_edge_ids=('edge-1',))
    bundle = service.event_dossier('event-1', selection, title='Event dossier', summary='Explicit dossier scope.', as_of=NOW, persist=False)

    assert bundle.snapshot.report_type == EVENT_DOSSIER
    assert bundle.snapshot.subject_ref_type == EVENT
    assert bundle.snapshot.subject_ref_id == 'event-1'
    assert _section(bundle, 'EVENTS').content['events'][0]['event_id'] == 'event-1'
    assert _section(bundle, 'CLAIMS').content['claims'][0]['claim_id'] == 'claim-1'
    assert _section(bundle, 'SOURCE_EVIDENCE').content['raw_items'][0]['raw_item_id'] == 'raw-1'
    assert _section(bundle, 'FINDINGS').content['findings'][0]['finding_id'] == 'finding-1'
    assert _section(bundle, 'RELATIONSHIPS').content['edges'][0]['edge_id'] == 'edge-1'
    assert all(item['event_id'] != 'event-2' for item in _section(bundle, 'EVENTS').content['events'])


def test_observation_timeline_uses_only_selected_persisted_collection_times(tmp_path):
    service = _seed(tmp_path / 'project.db')
    bundle = service.event_dossier('event-1', DossierStorylineSelection(raw_item_ids=('raw-2','raw-1')), title='Dossier', summary='Timeline scope.', as_of=NOW, persist=False)
    timeline = _section(bundle, 'TIMELINE')

    assert timeline.presentation_class == ANALYTICAL_CONTEXT
    assert [item['raw_item_id'] for item in timeline.content['observations']] == ['raw-1','raw-2']
    assert [item['collected_at'] for item in timeline.content['observations']] == [NOW.isoformat(), NOW.replace(minute=35).isoformat()]
    assert 'event_time' not in timeline.content['observations'][0]


def test_claim_verification_state_is_display_only_and_contradictions_are_analytical_context(tmp_path):
    db = tmp_path / 'project.db'
    service = _seed(db)
    with sqlite3.connect(db) as c:
        before = c.execute("SELECT text,confidence FROM claims WHERE id='claim-1'").fetchone(), c.execute("SELECT text,confidence FROM claims WHERE id='claim-2'").fetchone()

    bundle = service.storyline_report('storyline-scope:claims', DossierStorylineSelection(claim_ids=('claim-1','claim-2'), contradiction_pairs=(('claim-2','claim-1'),)), title='Storyline', summary='Contradiction scope.', as_of=NOW, persist=False)
    contradictions = _section(bundle, 'CONTRADICTIONS')
    refs = {(r.reference_kind,r.reference_value,r.reference_role) for r in bundle.references if r.section_id == contradictions.section_id}

    assert contradictions.presentation_class == ANALYTICAL_CONTEXT
    assert contradictions.content['claim_pairs'] == [['claim-1','claim-2']]
    assert refs == {(CLAIM,'claim-1','CONTRADICTION_SIDE'),(CLAIM,'claim-2','CONTRADICTION_SIDE')}
    with sqlite3.connect(db) as c:
        after = c.execute("SELECT text,confidence FROM claims WHERE id='claim-1'").fetchone(), c.execute("SELECT text,confidence FROM claims WHERE id='claim-2'").fetchone()
        assert 'storylines' not in {row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert before == after


def test_storyline_is_scope_only_and_remapped_common_assembler_refs_remain_typed(tmp_path):
    service = _seed(tmp_path / 'project.db')
    bundle = service.storyline_report('storyline-scope:event-1', DossierStorylineSelection(event_ids=('event-1',), finding_ids=('finding-1',), graph_edge_ids=('edge-1',)), title='Storyline', summary='Explicit report-scoped collection.', as_of=NOW, persist=False)

    assert bundle.snapshot.report_type == STORYLINE_REPORT
    assert bundle.snapshot.subject_ref_type is None
    assert bundle.snapshot.subject_ref_id is None
    relationship = _section(bundle, 'RELATIONSHIPS')
    assert any(r.section_id == relationship.section_id and r.reference_kind == GRAPH_EDGE and r.reference_value == 'edge-1' for r in bundle.references)
    assert len({section.section_id for section in bundle.sections}) == len(bundle.sections)
    assert [section.section_order for section in bundle.sections] == list(range(len(bundle.sections)))


@pytest.mark.parametrize(('field','value','message'), [('event','event-x','unknown event'),('claim','claim-x','unknown claim'),('raw','raw-x','unknown raw item')])
def test_dossier_storyline_fail_closed_on_unknown_refs(tmp_path, field, value, message):
    service = _seed(tmp_path / 'project.db')
    if field == 'event':
        with pytest.raises(ValueError, match=message):
            service.event_dossier(value, DossierStorylineSelection(), title='Dossier', summary='Summary', as_of=NOW, persist=False)
    elif field == 'claim':
        with pytest.raises(ValueError, match=message):
            service.storyline_report('storyline-scope:x', DossierStorylineSelection(claim_ids=(value,)), title='Storyline', summary='Summary', as_of=NOW, persist=False)
    else:
        with pytest.raises(ValueError, match=message):
            service.storyline_report('storyline-scope:x', DossierStorylineSelection(raw_item_ids=(value,)), title='Storyline', summary='Summary', as_of=NOW, persist=False)


def test_storyline_requires_explicit_selection_and_rejects_self_contradiction(tmp_path):
    service = _seed(tmp_path / 'project.db')
    with pytest.raises(ValueError, match='explicit persisted references'):
        service.storyline_report('storyline-scope:empty', DossierStorylineSelection(), title='Storyline', summary='Summary', as_of=NOW, persist=False)
    with pytest.raises(ValueError, match='two different claims'):
        service.storyline_report('storyline-scope:self', DossierStorylineSelection(contradiction_pairs=(('claim-1','claim-1'),)), title='Storyline', summary='Summary', as_of=NOW, persist=False)


def test_dossier_composition_does_not_mutate_upstream_event_raw_finding_or_graph_state(tmp_path):
    db = tmp_path / 'project.db'
    service = _seed(db)
    with sqlite3.connect(db) as c:
        before = c.execute("SELECT title,status,importance FROM events WHERE id='event-1'").fetchone(), c.execute("SELECT title,collected_at FROM raw_items WHERE id='raw-1'").fetchone(), c.execute("SELECT importance,confidence,evidence_refs FROM operational_findings WHERE finding_id='finding-1'").fetchone(), c.execute("SELECT confidence,status,explanation FROM graph_edges WHERE edge_id='edge-1'").fetchone()
    service.event_dossier('event-1', DossierStorylineSelection(raw_item_ids=('raw-1',), finding_ids=('finding-1',), graph_edge_ids=('edge-1',)), title='Dossier', summary='Summary', as_of=NOW, persist=False)
    with sqlite3.connect(db) as c:
        after = c.execute("SELECT title,status,importance FROM events WHERE id='event-1'").fetchone(), c.execute("SELECT title,collected_at FROM raw_items WHERE id='raw-1'").fetchone(), c.execute("SELECT importance,confidence,evidence_refs FROM operational_findings WHERE finding_id='finding-1'").fetchone(), c.execute("SELECT confidence,status,explanation FROM graph_edges WHERE edge_id='edge-1'").fetchone()
    assert before == after
