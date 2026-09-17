import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ONBOARD=ROOT/'docs/evidence/P21_5_WAVE_A_ONBOARDING_2026-09-17.json'
HEALTH=ROOT/'docs/evidence/P21_5_WAVE_A_FRESH_HEALTH_2026-09-17.json'
RESULT=ROOT/'docs/implementation/P21_5_WAVE_A_CONTROLLED_SOURCE_ONBOARDING_RESULT.md'

def test_wave_a_onboarding_is_p20_5_qualified_and_separately_p21_5_activated():
    x=json.loads(ONBOARD.read_text())
    assert x['summary']=={'candidate_count':2,'p20_5_eligible_count':2,'repository_active_count':2,'fresh_healthy_count':1,'healthy_collector_stale_content_count':1,'independence_credit_granted_count':0}
    assert all(s['eligibility_decision']=='ELIGIBLE_NOT_ACTIVE' for s in x['sources'])
    assert all(s['live_activation_authorized'] is False and s['live_activation_state']=='NOT_ACTIVE' for s in x['sources'])
    assert all(s['p21_5_repository_activation']=='ACTIVE' for s in x['sources'])
    assert all(s['rollback_disable_status']=='PASS' for s in x['sources'])

def test_wave_a_fresh_health_preserves_measured_degradation():
    h=json.loads(HEALTH.read_text()); by={s['source_id']:s for s in h['sources']}
    assert h['success_count']==2 and h['failure_count']==0 and h['item_count']==120
    assert by['suspilne-uk']['content_age_minutes'] < 120
    assert by['ukraine-government-kmu-uk']['content_age_minutes'] > 240
    assert h['production_runtime_mutated'] is False and h['runtime_deployment'] is False and h['service_restart'] is False

def test_wave_a_result_keeps_truth_and_runtime_boundaries():
    t=RESULT.read_text()
    assert 'IMPLEMENTED / VALIDATION_CANDIDATE' in t
    assert 'P13.5/P13.6 remain factual-verification authority' in t
    assert 'HEALTHY_COLLECTOR / STALE_CONTENT' in t
