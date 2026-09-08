from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


roadmap = ROOT / "ROADMAP.md"
plan = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
p18_7_test = ROOT / "tests" / "test_p18_7_formal_closure.py"

replace_once(roadmap, "Version: 4.32", "Version: 4.33")
replace_once(
    roadmap,
    "State: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_READY / NOT_ACTIVATED`",
    "State: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_VALIDATED / P18_9_READY / NOT_ACTIVATED`",
)
replace_once(
    roadmap,
    "### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness\nState: `READY_TO_BEGIN`\nGate: `P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`\n\nP18.8 is the next permitted engineering step. It may implement a provider-neutral non-production shared candidate, controlled provenance-bound copy/export, reconciliation, read-only shadow comparison, security/recovery evidence, provider/cost comparison where infrastructure is actually required, and canary-readiness design. No paid provider may be committed without a separate explicit owner decision, and no canonical cutover or shared-runtime activation is authorized by P18.8 readiness.\n",
    "### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness\nState: `VALIDATED`\nGate: `P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`\nImplementation anchor: `5cb0c4075c709c2f32c62857de7b577d04a90da6`.\nContract: `docs/implementation/P18_8_NONPROD_SHADOW_CANARY_CONTRACT.md`\nResult: `docs/implementation/P18_8_NONPROD_SHADOW_CANARY_READINESS_RESULT.md`\nCheckpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-08_P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED.md`\n\nExact implementation validation:\n- PR #32 branch CI run `34172333125`, job `101894888146`: `1077 passed in 114.49s / SUCCESS`, dependency check PASS;\n- exact-main x64 run `34172531605`, job `101895457213`: exact `5cb0c4075c709c2f32c62857de7b577d04a90da6`, `1077 passed in 141.19s / SUCCESS`, dependency check PASS;\n- exact-main native ARM64 run `34172531604`, job `101895457340`: exact `5cb0c4075c709c2f32c62857de7b577d04a90da6`, native `aarch64`, `1077 passed in 102.82s / SUCCESS`, dependency check, bootstrap, unattended one-tick and systemd contract PASS; unattended smoke `execution_count=0`, `recovered_runs=0`.\n\nValidated shadow/canary contract: provenance-bound owner-local snapshots load only into an isolated provider-neutral read-only non-production candidate; imported tables must belong to the approved target schema; cross-tenant import, overwrite, writes and unapproved table reads fail closed; row-count/content/semantic drift is explicit and budgetable only when non-fatal; tenant, schema and invariant mismatches are always fatal; P18.4/P18.6/P18.7 contract evidence is composed without inventing infrastructure observations; provider selection/spend remains separately owner-gated; staged canary design is read-only and cannot auto-promote, cut over, activate shared runtime or authorize production/live.\n\nP18.8 validates provider-neutral shadow/canary readiness only. Real PostgreSQL/shared-datastore deployment, live TLS/private reachability, concrete encrypted off-host backup, provider PITR/WAL-equivalent, provider billing and real canary traffic remain `NOT_OBSERVED`. P18.8 did not select or purchase a provider, allocate migration `033`, expose shared/public ingress, switch canonical storage, authorize canonical cutover, activate shared runtime or change production/live status.\n\n### P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness\nState: `READY_TO_BEGIN`\nGate: `PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`\n\nP18.9 is the next permitted engineering step. It must validate the complete Phase 18 tenancy/RBAC, migration, concurrency/idempotency/outbox, security, recovery/rollback, provider/cost-approval-where-applicable, owner-local compatibility and architecture regression matrix. Infrastructure-dependent claims remain fail-closed unless real evidence exists. P18.9 means activation readiness only and must not set `PHASE_18_SHARED_RUNTIME_ACTIVE = YES`; final activation requires a separate explicit owner decision plus fresh launch-time validation.\n",
)
replace_once(roadmap, "- state synchronization: `v4.32`;", "- state synchronization: `v4.33`;")
replace_once(
    roadmap,
    "- Phase 18: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_READY / NOT_ACTIVATED`;",
    "- Phase 18: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_VALIDATED / P18_9_READY / NOT_ACTIVATED`;",
)
replace_once(roadmap, "- P18.8: `READY_TO_BEGIN`;", "- P18.8: `VALIDATED`;\n- P18.9: `READY_TO_BEGIN`;")
replace_once(
    roadmap,
    "Phase 18 architecture and implementation are owner-authorized; P18.0 through P18.7 are validated and P18.8 is ready to begin. P18.8 readiness does not authorize migration `033`, provider spending/selection, shared datastore deployment, shared-runtime activation/cutover or production/live transition.",
    "Phase 18 architecture and implementation are owner-authorized; P18.0 through P18.8 are validated and P18.9 is ready to begin. P18.8 validation records provider-neutral shadow/canary contract readiness while real external infrastructure observations remain `NOT_OBSERVED`. P18.9 readiness work does not authorize migration `033`, provider spending/selection, shared datastore deployment, shared-runtime activation/cutover or production/live transition; final activation remains a separate explicit owner decision after fresh launch-time validation.",
)

replace_once(
    plan,
    "Status: `IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_READY`",
    "Status: `IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_VALIDATED / P18_9_READY`",
)
replace_once(
    plan,
    "P18.0 through P18.7 have since been implemented and validated. P18.8 is now the next permitted engineering step, but shared-runtime activation, canonical cutover, paid providers, migration `033` and production/live operation remain separately gated.",
    "P18.0 through P18.8 have since been implemented and validated. P18.9 is now the next permitted engineering step, but shared-runtime activation, canonical cutover, paid providers, migration `033` and production/live operation remain separately gated.",
)
replace_once(
    plan,
    "P18.7 is formally validated at `P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED`; P18.8 is `READY_TO_BEGIN`.",
    "P18.7 is formally validated at `P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED`; P18.8 is formally validated at `P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`; P18.9 is `READY_TO_BEGIN`.",
)
replace_once(
    plan,
    "### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness\n\nState: `READY_TO_BEGIN`\nGate: `P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`\n\nScope after implementation authorization:\n\n- provider-neutral non-production shared runtime candidate;\n- controlled copy/export with provenance from local canonical source;\n- row-count, invariant and semantic reconciliation;\n- read-only shadow comparison;\n- concurrency, isolation, security and restore evidence;\n- provider/cost comparison when external infrastructure is actually needed;\n- explicit owner provider approval before any paid-provider commitment;\n- canary design without canonical cutover.\n\nAcceptance:\n\n- shadow mismatches are explicit and bounded;\n- no automatic promotion/cutover occurs;\n- paid providers remain `NONE_APPROVED` unless separately approved;\n- current owner-only local store remains canonical.\n\n### P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness\n\nState: `PLANNED / NOT_STARTED`",
    "### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness\n\nState: `VALIDATED`\nGate: `P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`\nImplementation anchor: `5cb0c4075c709c2f32c62857de7b577d04a90da6`\nContract: `docs/implementation/P18_8_NONPROD_SHADOW_CANARY_CONTRACT.md`\nResult: `docs/implementation/P18_8_NONPROD_SHADOW_CANARY_READINESS_RESULT.md`\nCheckpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-08_P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED.md`\n\nValidated scope:\n\n- provenance-bound owner-local export/snapshot evidence;\n- approved target-schema allowlisting and exact tenant isolation;\n- isolated provider-neutral non-production read-only shadow candidate with no write/promote API;\n- row-count, content, semantic and invariant reconciliation;\n- fatal tenant/schema/invariant mismatch classes separated from explicitly budgetable non-fatal analytical drift;\n- P18.4 concurrency, P18.6 security and P18.7 recovery contract-evidence composition;\n- provider/cost gate with separate owner approval required before provider selection/spend;\n- staged read-only canary design with automatic promotion, canonical cutover, shared activation and production/live transition forbidden.\n\nValidation evidence:\n\n- PR #32 branch CI run `34172333125`, job `101894888146`: `1077 passed in 114.49s / SUCCESS`; dependency check PASS;\n- exact-main x64 run `34172531605`, job `101895457213`: exact `5cb0c4075c709c2f32c62857de7b577d04a90da6`, `1077 passed in 141.19s / SUCCESS`; dependency check PASS;\n- exact-main native ARM64 run `34172531604`, job `101895457340`: exact `5cb0c4075c709c2f32c62857de7b577d04a90da6`, native `aarch64`, `1077 passed in 102.82s / SUCCESS`; dependency check, bootstrap, unattended one-tick and systemd contract PASS;\n- unattended smoke: `execution_count: 0`, `recovered_runs: 0`.\n\nAcceptance boundary:\n\n- P18.8 validates provider-neutral shadow/canary contract readiness only;\n- real datastore/TLS/private reachability/off-host/PITR/provider-cost/live-canary observations remain `NOT_OBSERVED`;\n- current owner-only local store remains canonical;\n- no automatic promotion/cutover occurs;\n- no provider selection or paid-provider commitment was approved;\n- P18.8 did not create/preauthorize migration `033`, deploy shared/public ingress, activate shared runtime or change production/live status.\n\n### P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness\n\nState: `READY_TO_BEGIN`",
)
replace_once(plan, "`P18_8 = READY_TO_BEGIN`", "`P18_8 = VALIDATED`\n\n`P18_9 = READY_TO_BEGIN`")
replace_once(
    plan,
    "The next permitted engineering step is:\n\n`P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness`\n\nTarget validation gate:\n\n`P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`\n\nP18.8 readiness authorizes only the next non-production/shadow engineering step. It does not allocate/create/preauthorize migration `033`, approve or purchase a paid provider, activate shared/public ingress, activate shared runtime, switch canonical storage, authorize canonical cutover or authorize production/live transition.",
    "The next permitted engineering step is:\n\n`P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness`\n\nTarget validation gate:\n\n`PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`\n\nP18.9 validation means activation readiness only. Infrastructure-dependent assertions remain fail-closed unless real evidence exists, and provider/cost approval evidence is required only where applicable. P18.9 does not allocate/create/preauthorize migration `033`, approve or purchase a paid provider, activate shared/public ingress, activate shared runtime, switch canonical storage, authorize canonical cutover or authorize production/live transition. Final activation remains a separate explicit owner decision after fresh launch-time validation.",
)

# Historical P18.7 closure guard must remain valid after later Phase 18 advances.
replace_once(
    p18_7_test,
    "def test_p18_7_current_state_converges_to_p18_8_ready_gate():\n    state = _state()\n    assert state[\"roadmap\"][\"state_sync_version\"] == \"4.32\"\n    assert state[\"roadmap\"][\"current_position\"] == \"PHASE_18_P18_7_VALIDATED_P18_8_READY_GATE\"\n    assert state[\"phases\"][\"18\"] == (\n        \"ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / \"\n        \"P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / \"\n        \"P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_READY / NOT_ACTIVATED\"\n    )\n    assert state[\"activation_gates\"][\"phase18_activation\"] == \"PHASE_18_SHARED_RUNTIME_ACTIVE = NO\"",
    "def test_p18_7_historical_closure_remains_recorded_after_later_phase_advances():\n    state = _state()\n    assert float(state[\"roadmap\"][\"state_sync_version\"]) >= 4.32\n    assert state[\"phase18_p18_7\"][\"state\"] == \"VALIDATED\"\n    assert state[\"phase18_p18_7\"][\"gate\"] == \"P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED\"\n    assert \"P18_7_VALIDATED\" in state[\"phases\"][\"18\"]\n    assert state[\"activation_gates\"][\"phase18_activation\"] == \"PHASE_18_SHARED_RUNTIME_ACTIVE = NO\"",
)
replace_once(
    p18_7_test,
    "def test_p18_7_roadmap_and_plan_converge_without_activation_provider_or_migration():",
    "def test_p18_7_roadmap_and_plan_preserve_validated_gate_without_pinning_current_phase():",
)
replace_once(p18_7_test, "assert _roadmap_minor_version(roadmap) == 32", "assert _roadmap_minor_version(roadmap) >= 32")
replace_once(p18_7_test, "assert \"P18_7_VALIDATED / P18_8_READY / NOT_ACTIVATED\" in roadmap", "assert \"P18_7_VALIDATED\" in roadmap")
replace_once(p18_7_test, "assert \"P18_8 = READY_TO_BEGIN\" in plan", "assert \"P18_8 = VALIDATED\" in plan")

print("P18.8 closure patch applied successfully")
