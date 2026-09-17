import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'docs/state/CURRENT_PROJECT_STATE.json'
ROADMAP=ROOT/'ROADMAP.md'
HANDOFF=ROOT/'docs/handoff/CURRENT_HANDOFF.md'
RESULT=ROOT/'docs/implementation/P21_5_WAVE_A_CONTROLLED_SOURCE_ONBOARDING_RESULT.md'
CHECKPOINT=ROOT/'docs/checkpoints/PROJECT_CHECKPOINT_2026-09-17_P21_5_CONTROLLED_SOURCE_ONBOARDING_VALIDATED.md'
ONBOARD=ROOT/'docs/evidence/P21_5_WAVE_A_ONBOARDING_2026-09-17.json'
HEALTH=ROOT/'docs/evidence/P21_5_WAVE_A_FRESH_HEALTH_2026-09-17.json'

def test_p21_5_formal_closure_state_is_converged():
    s=json.loads(STATE.read_text()); x=s['phase21_p21_5']
    assert s['roadmap']['state_sync_version']=='4.43'
    assert s['roadmap']['current_position']=='PHASE_21_P21_5_VALIDATED_P21_6_READY'
    assert s['phase21']['validated_sequence'][-1]=='P21.5'
    assert s['phase21']['next_gate']=='P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED'
    assert x['state']=='VALIDATED_WITH_MEASURED_CONTENT_STALENESS'
    assert x['implementation_merge_anchor']=='e2b78f8511154e9b626a39d0525d9b118c842bd2'
    assert x['implementation_pr']==123 and x['validation_run_id']==35174372833 and x['test_count']==1292
    assert x['repository_active_count']==2 and x['fresh_healthy_count']==1 and x['healthy_collector_stale_content_count']==1
    assert x['independence_credit_granted_count']==0 and x['p21_6_state']=='READY_TO_BEGIN'

def test_p21_5_closure_preserves_measured_and_runtime_boundaries():
    o=json.loads(ONBOARD.read_text()); h=json.loads(HEALTH.read_text()); r=RESULT.read_text(); roadmap=ROADMAP.read_text(); handoff=HANDOFF.read_text()
    assert o['summary']['repository_active_count']==2 and o['summary']['independence_credit_granted_count']==0
    by={x['source_id']:x for x in h['sources']}
    assert by['suspilne-uk']['content_age_minutes'] < 120
    assert by['ukraine-government-kmu-uk']['content_age_minutes'] > 240
    assert h['production_runtime_mutated'] is False and h['service_restart'] is False
    assert '1292 passed in 141.35s / SUCCESS' in r
    assert CHECKPOINT.exists()
    assert 'P21_5_CONTROLLED_SOURCE_ONBOARDING_VALIDATED' in roadmap
    assert 'P21.5 controlled public/free onboarding' in handoff
    assert 'P13.5/P13.6 remain factual-verification authority' in r
    assert json.loads(STATE.read_text())['migrations']['033']=='NOT_CREATED / NOT_PREAUTHORIZED'
