import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'docs/state/CURRENT_PROJECT_STATE.json'
AUTH=ROOT/'docs/evidence/P21_5_CONTROLLED_SOURCE_ONBOARDING_OWNER_AUTHORIZATION_2026-09-16.json'
PLAN=ROOT/'docs/evidence/P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_2026-09-16.json'

def test_p21_5_owner_authorization_is_bound_and_bounded():
    s=json.loads(STATE.read_text())
    a=json.loads(AUTH.read_text())
    assert s['roadmap']['state_sync_version']=='4.42'
    assert s['roadmap']['current_position']=='PHASE_21_P21_5_AUTHORIZED_WAVE_A_READY'
    assert a['authority_state']=='APPROVED'
    assert a['bound_plan_blob_sha']=='383d1bb1f9764c5962bbb41035abc4a33140a223'
    assert a['initial_wave']=='A_CRITICAL_REQUIRED'
    assert a['initial_cell_ids']==['ukraine.uk.official_government','ukraine.uk.national_media']
    assert a['authorized']['public_free_anonymous_public_data_sources'] is True
    assert a['not_authorized']['runtime_deployment_or_service_restart'] is True
    assert a['not_authorized']['paid_or_credentialed_or_restricted_sources'] is True
    assert a['independence_credit_auto_granted'] is False

def test_p21_5_authorization_preserves_runtime_and_truth_boundaries():
    s=json.loads(STATE.read_text())
    p=s['phase21_p21_5']
    assert p['state']=='AUTHORIZED_READY_TO_BEGIN'
    assert p['runtime_deployment_authorized'] is False
    assert p['service_restart_authorized'] is False
    assert p['production_live_cutover_authorized'] is False
    assert p['paid_or_shared_resources_authorized'] is False
    assert p['migration_033']=='NOT_CREATED / NOT_PREAUTHORIZED'
    assert p['verification_authority']=='P13.5/P13.6'
    assert s['runtime']['production_live']=='NOT_OPERATIONAL'
