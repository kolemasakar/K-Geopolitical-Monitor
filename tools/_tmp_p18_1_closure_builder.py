from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected exactly one match, found {count}: {old[:120]!r}"
        )
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# ROADMAP v4.26 convergence.
replace_once("ROADMAP.md", "Version: 4.25", "Version: 4.26")
replace_once(
    "ROADMAP.md",
    "State: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_READY / NOT_ACTIVATED`",
    "State: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_READY / NOT_ACTIVATED`",
)
replace_once(
    "ROADMAP.md",
    """### P18.1 — Identity and Authenticated Tenant Context Foundation
State: `READY_TO_BEGIN`
Gate: `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`

P18.1 is the next permitted engineering step under the already recorded implementation authorization. Concrete identity-provider selection, spending and shared-runtime activation remain separately gated.""",
    """### P18.1 — Identity and Authenticated Tenant Context Foundation
State: `VALIDATED`
Gate: `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`
Implementation anchor: `01abc4f6be77c856e24497ad77c58ab052bb89e2`.
Result: `docs/implementation/P18_1_IDENTITY_TENANT_CONTEXT_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED.md`

Exact implementation validation:
- x64 run `34124491945`, job `101749841571`: `776 passed in 124.31s / SUCCESS`;
- native ARM64 run `34124491899`, job `101749841305`: native `aarch64`, `776 passed in 99.81s / SUCCESS`, bootstrap/unattended/systemd PASS.

Validated foundation: credential validation is provider-neutral; human and service identities are distinct; temporal and revocation validation fail closed; workspace/project scope is derived server-side from authenticated identity and membership; forged, unauthorized and ambiguous tenant scope is rejected; service identities cannot satisfy human/owner authority requirements.

P18.1 did not select an external identity provider, activate shared runtime, create migration `033`, expose public/shared ingress, commit paid-provider spending or perform production/live cutover.

### P18.2 — RBAC and Owner-Only Strategic Gate Enforcement
State: `READY_TO_BEGIN`
Gate: `P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED`

P18.2 is the next permitted engineering step. It may introduce deny-by-default role enforcement and owner-only action gates, but it must not activate shared runtime, select a paid provider, authorize migration `033`, or expose production/shared ingress.""",
)
replace_once(
    "ROADMAP.md",
    "- state synchronization: `v4.25`;",
    "- state synchronization: `v4.26`;",
)
replace_once(
    "ROADMAP.md",
    "- Phase 18: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_READY / NOT_ACTIVATED`;",
    "- Phase 18: `ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_READY / NOT_ACTIVATED`;",
)
replace_once(
    "ROADMAP.md",
    "- P18.1: `READY_TO_BEGIN`;",
    "- P18.1: `VALIDATED`;\n- P18.2: `READY_TO_BEGIN`;",
)
replace_once(
    "ROADMAP.md",
    "Phase 18 architecture and implementation are owner-authorized; P18.0 is validated and P18.1 is ready to begin, while shared-runtime activation/cutover, paid-provider commitments, migration `033` and production/live transition remain explicitly unauthorized.",
    "Phase 18 architecture and implementation are owner-authorized; P18.0 and P18.1 are validated and P18.2 is ready to begin, while shared-runtime activation/cutover, paid-provider commitments, migration `033` and production/live transition remain explicitly unauthorized.",
)

# Machine-readable state v4.26.
state_path = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["roadmap"]["state_sync_version"] = "4.26"
state["roadmap"]["current_position"] = "PHASE_18_P18_1_VALIDATED_P18_2_READY_GATE"
state["phases"]["18"] = (
    "ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / "
    "P18_0_VALIDATED / P18_1_VALIDATED / P18_2_READY / NOT_ACTIVATED"
)
state["phase18_p18_1"] = {
    "state": "VALIDATED",
    "gate": "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED",
    "implementation_anchor": "01abc4f6be77c856e24497ad77c58ab052bb89e2",
    "x64_run_id": 34124491945,
    "x64_job_id": 101749841571,
    "arm64_run_id": 34124491899,
    "arm64_job_id": 101749841305,
    "test_count": 776,
    "next_gate": "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED",
    "p18_2_state": "READY_TO_BEGIN",
}
state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

# Implementation-plan convergence.
PLAN = "docs/implementation/PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
replace_once(
    PLAN,
    "Status: `IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_READY`",
    "Status: `IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_READY`",
)
replace_once(
    PLAN,
    "The plan itself did not authorize implementation. A separate explicit owner decision on 2026-09-07 subsequently set `PHASE_18_IMPLEMENTATION_AUTHORIZED = YES`. P18.0 has since been implemented and validated. P18.1 is now the next permitted engineering step, but shared-runtime activation, canonical cutover, paid providers and production/live operation remain separately gated.",
    "The plan itself did not authorize implementation. A separate explicit owner decision on 2026-09-07 subsequently set `PHASE_18_IMPLEMENTATION_AUTHORIZED = YES`. P18.0 and P18.1 have since been implemented and validated. P18.2 is now the next permitted engineering step, but shared-runtime activation, canonical cutover, paid providers and production/live operation remain separately gated.",
)
replace_once(
    PLAN,
    "P18.0 is formally validated at `P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED`; P18.1 is `READY_TO_BEGIN`.",
    "P18.0 is formally validated at `P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED`; P18.1 is formally validated at `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`; P18.2 is `READY_TO_BEGIN`.",
)
replace_once(
    PLAN,
    """### P18.1 — Identity and Authenticated Tenant Context Foundation

State: `READY_TO_BEGIN`
Gate: `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`

Scope after implementation authorization:

- define standards-based identity adapter contract (OIDC/OAuth2-class or equivalent);
- separate human and service identities;
- bind stable subject identity to explicit workspace membership;
- derive tenant context server-side from authenticated identity and authorized request scope;
- implement short-lived session/token validation interfaces and revocation-aware behavior;
- keep concrete external identity provider selection behind a separate provider gate.

Acceptance:

- unauthenticated access fails closed;
- forged/ambiguous workspace context is rejected;
- service identity cannot impersonate human owner authority;
- no shared owner bearer token is introduced as team authentication.""",
    """### P18.1 — Identity and Authenticated Tenant Context Foundation

State: `VALIDATED`
Gate: `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`
Implementation anchor: `01abc4f6be77c856e24497ad77c58ab052bb89e2`
Result: `docs/implementation/P18_1_IDENTITY_TENANT_CONTEXT_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED.md`

Validated scope:

- provider-neutral identity-validation adapter contract;
- explicit human/service identity and credential separation;
- short-lived temporal validation with mandatory fail-closed revocation status;
- server-side workspace/project membership resolution;
- authenticated tenant context derived only after identity, temporal, revocation and membership checks;
- forged, unauthorized and ambiguous tenant scope rejected;
- service identities cannot satisfy human/owner authority requirements;
- no concrete external identity provider selected.

Validation evidence:

- x64 run `34124491945`, job `101749841571`: `776 passed in 124.31s / SUCCESS`;
- native ARM64 run `34124491899`, job `101749841305`: native `aarch64`, `776 passed in 99.81s / SUCCESS`, bootstrap/unattended/systemd PASS.""",
)
replace_once(
    PLAN,
    "### P18.2 — RBAC and Owner-Only Strategic Gate Enforcement\n\nState: `PLANNED / NOT_STARTED`",
    "### P18.2 — RBAC and Owner-Only Strategic Gate Enforcement\n\nState: `READY_TO_BEGIN`",
)

# P18.1 validation result.
(ROOT / "docs/implementation/P18_1_IDENTITY_TENANT_CONTEXT_RESULT.md").write_text(
    """# P18.1 — Identity and Authenticated Tenant Context — Validation Result

Status: `VALIDATED`
Gate: `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`

Implementation anchor:
`01abc4f6be77c856e24497ad77c58ab052bb89e2`

## Validated Contract

- provider-neutral credential-validation adapter contract;
- explicit human and service identity/credential separation;
- short-lived temporal validation;
- mandatory fail-closed revocation status;
- server-side membership-based workspace/project resolution;
- authenticated `TenantContext` derivation;
- forged, unknown, unauthorized and ambiguous tenant selection rejected;
- service identity cannot satisfy human/owner authority requirements.

## Exact-Head Engineering Validation

x64:
- run `34124491945`;
- job `101749841571`;
- checkout `01abc4f6be77c856e24497ad77c58ab052bb89e2`;
- `pip check`: PASS;
- `776 passed in 124.31s / SUCCESS`.

Native ARM64:
- run `34124491899`;
- job `101749841305`;
- checkout `01abc4f6be77c856e24497ad77c58ab052bb89e2`;
- architecture: `aarch64`;
- `pip check`: PASS;
- `776 passed in 99.81s / SUCCESS`;
- host bootstrap: PASS;
- unattended one-tick smoke: PASS;
- systemd contract: PASS.

## Preserved Boundaries

- canonical runtime storage remains `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers remain `NONE_APPROVED`;
- backend HTTPS remains `NOT_DEPLOYED`;
- production/live remains `NOT_OPERATIONAL`.

## Decision

`P18_1 = VALIDATED`.

`P18_2 = READY_TO_BEGIN` only.

Next gate:
`P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED`.
""",
    encoding="utf-8",
)

# Formal checkpoint.
(ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-07_P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED.md").write_text(
    """# Project Checkpoint — P18.1 Identity and Authenticated Tenant Context Validated

Date: 2026-09-07
Project: K-Geopolitical Monitor
State: `VALIDATED`
Closure token: `P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED`
Implementation anchor: `01abc4f6be77c856e24497ad77c58ab052bb89e2`

## Engineering Evidence

- x64 run `34124491945`, job `101749841571`: `776 passed in 124.31s / SUCCESS`;
- native ARM64 run `34124491899`, job `101749841305`: native `aarch64`, `776 passed in 99.81s / SUCCESS`;
- `pip check`: PASS on both architectures;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick smoke: PASS;
- ARM64 systemd contract: PASS.

## Validated P18.1 Boundary

- authenticated identity is validated through a provider-neutral adapter boundary;
- human and service identities remain distinct;
- temporal and revocation validation fail closed;
- workspace/project tenant context is derived server-side from authenticated identity and authorized membership;
- forged, unauthorized and ambiguous tenant scope is rejected;
- service identities cannot satisfy human/owner authority requirements.

## Preserved Strategic Boundaries

- `PROJECT_LOCAL_ONLY` remains the active canonical runtime;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033` is `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers are `NONE_APPROVED`;
- public/shared ingress is not activated;
- production/live remains `NOT_OPERATIONAL`.

## Next Gate

`P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED`

P18.2 is `READY_TO_BEGIN` only. This checkpoint does not validate or activate P18.2.
""",
    encoding="utf-8",
)

# Formal closure regression guard.
(ROOT / "tests/test_p18_1_formal_closure.py").write_text(
    '''import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_1_IDENTITY_TENANT_CONTEXT_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED.md"


def _state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_p18_1_current_state_converges_to_p18_2_ready_gate():
    state = _state()
    assert state["roadmap"]["state_sync_version"] == "4.26"
    assert state["roadmap"]["current_position"] == "PHASE_18_P18_1_VALIDATED_P18_2_READY_GATE"
    assert state["phases"]["18"] == "ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_READY / NOT_ACTIVATED"
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_1_exact_engineering_evidence_is_recorded():
    p18_1 = _state()["phase18_p18_1"]
    assert p18_1 == {
        "state": "VALIDATED",
        "gate": "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED",
        "implementation_anchor": "01abc4f6be77c856e24497ad77c58ab052bb89e2",
        "x64_run_id": 34124491945,
        "x64_job_id": 101749841571,
        "arm64_run_id": 34124491899,
        "arm64_job_id": 101749841305,
        "test_count": 776,
        "next_gate": "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED",
        "p18_2_state": "READY_TO_BEGIN",
    }


def test_p18_1_roadmap_and_plan_converge_without_activation():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert "Version: 4.26" in roadmap
    assert "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED" in roadmap
    assert "P18.1: `VALIDATED`" in roadmap
    assert "P18.2: `READY_TO_BEGIN`" in roadmap
    assert "P18_1_VALIDATED / P18_2_READY / NOT_ACTIVATED" in roadmap
    assert "State: `VALIDATED`" in plan
    assert "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED" in plan
    assert "Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`" in plan


def test_p18_1_result_and_checkpoint_preserve_safety_boundaries():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")
    for text in (result, checkpoint):
        assert "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED" in text
        assert "01abc4f6be77c856e24497ad77c58ab052bb89e2" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text


def test_p18_1_closure_does_not_create_migration_033():
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
''',
    encoding="utf-8",
)

# Temporary builder artifacts must not survive into the PR tree.
(ROOT / ".github/workflows/_tmp_p18_1_closure_builder.yml").unlink(missing_ok=True)
Path(__file__).unlink()
