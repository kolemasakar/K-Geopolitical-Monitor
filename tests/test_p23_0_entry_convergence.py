import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'docs/state/CURRENT_PROJECT_STATE.json'
EVIDENCE = ROOT / 'docs/evidence/P23_0_ENTRY_CONVERGENCE_OWNER_GATES_2026-09-20.json'
RESULT = ROOT / 'docs/implementation/P23_0_ENTRY_CONVERGENCE_OWNER_GATES_RESULT.md'
CHECKPOINT = ROOT / 'docs/checkpoints/PROJECT_CHECKPOINT_2026-09-20_P23_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED.md'

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def test_p23_0_entry_baseline_matches_phase22_closure():
    b = load(EVIDENCE)['entry_baseline']
    assert (b['required_adequate'], b['required_degraded_collection'], b['required_missing_expected_coverage'], b['required_thin']) == (1,3,18,5)
    assert b['canonical_semantic_claim_count'] == 28 and b['attribution_only_count'] == 28
    assert b['underlying_origin_unresolved_count'] == 28 and b['semantic_independence_assessment_count'] == 0

def test_p23_0_owner_gates_fail_closed():
    x = load(EVIDENCE); a=x['authorization']; r=x['runtime_boundary']
    assert a['new_or_blocked_source_activation'] == 'OWNER_DECISION_REQUIRED'
    assert a['acquisition_resource_limit_relaxation'] == 'OWNER_DECISION_REQUIRED'
    assert a['bounded_owner_facing_delivery_sample'] == 'OWNER_DECISION_REQUIRED'
    assert a['persistent_owner_operation'] == 'NOT_ACTIVATED'
    assert r['runtime_deployment'] is False and r['service_restart'] is False and r['hp_omen_used'] is False

def test_p23_0_historical_entry_convergence_remains_valid_after_forward_progress():
    s=load(STATE); x=s['phase23']
    assert s['roadmap']['current_position'].startswith('PHASE_23_P23_')
    assert x['p23_0_state'] == 'VALIDATED'
    assert x['p23_0_gate'] == 'P23_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED'
    assert RESULT.exists() and CHECKPOINT.exists()
