import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'docs/state/CURRENT_PROJECT_STATE.json'
ROADMAP = ROOT / 'ROADMAP.md'
HANDOFF = ROOT / 'docs/handoff/CURRENT_HANDOFF.md'
DECISION = ROOT / 'docs/decisions/PHASE_23_EVIDENCE_DEPTH_CORROBORATION_OPERATIONAL_YIELD_ROADMAP_DECISION_2026-09-20.md'
PLAN = ROOT / 'docs/implementation/PHASE_23_EVIDENCE_DEPTH_CORROBORATION_OPERATIONAL_YIELD_PLAN.md'
PROPOSAL = ROOT / 'docs/decisions/POST_PHASE_22_ROADMAP_DECISION_PROPOSAL_2026-09-20.md'

def state():
    return json.loads(STATE.read_text(encoding='utf-8'))

def test_phase23_owner_approval_creates_phase_without_activation():
    s = state(); x = s['phase23']
    assert s['roadmap']['state_sync_version'] == '4.60'
    assert s['roadmap']['current_position'].startswith('PHASE_23_')
    assert s['phases']['23'].startswith('PHASE_23_EVIDENCE_DEPTH_CORROBORATION_OPERATIONAL_YIELD_APPROVED')
    assert s['post_phase22_strategic_audit']['decision_state'] == 'OWNER_APPROVED_PHASE_23'
    assert x['implementation_authorized'] is True
    assert x['strategic_direction'] == 'EVIDENCE_YIELD_DUAL_TRACK'
    assert x['p23_0_state'] == 'VALIDATED'

def test_phase23_preserves_boundaries():
    x = state()['phase23']
    assert x['repository_only_bounded_remediation'] == 'AUTHORIZED'
    assert x['new_or_blocked_source_activation'] == 'OWNER_DECISION_REQUIRED'
    assert x['acquisition_resource_limit_relaxation'] == 'OWNER_DECISION_REQUIRED'
    assert x['bounded_owner_facing_delivery_sample'] == 'OWNER_DECISION_REQUIRED'
    assert x['persistent_owner_operation'] == 'NOT_ACTIVATED'
    assert x['verification_authority'] == 'P13.5/P13.6'
    assert x['runtime_deployment'] is False and x['service_restart'] is False
    assert x['production_live'] == 'NOT_OPERATIONAL'
    assert x['hp_omen_allowed'] is False

def test_phase23_documents_converged():
    s = state(); roadmap = ROADMAP.read_text(encoding='utf-8'); handoff = HANDOFF.read_text(encoding='utf-8')
    assert DECISION.exists() and PLAN.exists()
    assert 'Version: 4.60' in roadmap
    assert '## Phase 23 — Evidence Depth, Corroboration & Operational Yield' in roadmap
    assert 'PHASE_23_P23_0_ENTRY_CONVERGENCE_VALIDATED' in handoff
    assert 'APPROVED / SUPERSEDED_BY_PHASE_23_ROADMAP_DECISION' in PROPOSAL.read_text(encoding='utf-8')
    assert s['phase22']['state'] == 'VALIDATED_WITH_KNOWN_LIMITATIONS'
