from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "p19_milestone_evidence.py"
SPEC = importlib.util.spec_from_file_location("p19_milestone_evidence", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
p19e = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = p19e
SPEC.loader.exec_module(p19e)


DEPLOYED_SHA = "b31b2136b5fe982d0b63b0135479b1549041906c"
CANONICAL_SHA = "5714a76aaf12c77993ed5a02165c02a48d953758"


def audit(*, status="PASS", terminal="2026-09-12T07:40:00Z", gap=3.9):
    return {
        "schema_version": "kgm.p19_soak_gate.v1",
        "baseline_utc": "2026-09-11T07:38:44Z",
        "evaluated_at_utc": "2026-09-12T07:41:00Z",
        "max_allowed_gap_hours": 7.0,
        "qualifying_observation_count_after_baseline": 8,
        "latest_observation_utc": terminal or "2026-09-12T07:38:00Z",
        "current_max_gap_hours": gap,
        "continuity_status": "PASS",
        "audit_status": "PASS",
        "milestones": {
            "24h": {
                "hours": 24,
                "boundary_utc": "2026-09-12T07:38:44Z",
                "status": status,
                "terminal_observation_utc": terminal,
            },
            "72h": {
                "hours": 72,
                "boundary_utc": "2026-09-14T07:38:44Z",
                "status": "IN_PROGRESS",
                "terminal_observation_utc": None,
            },
            "7d": {
                "hours": 168,
                "boundary_utc": "2026-09-18T07:38:44Z",
                "status": "IN_PROGRESS",
                "terminal_observation_utc": None,
            },
        },
    }


def metadata(**overrides):
    values = {
        "attempt_id": "P19_ATTEMPT_2",
        "audit_run_id": "34599999999",
        "audit_job_id": "103299999999",
        "artifact_id": "10269999999",
        "failed_control_count": 0,
        "deployed_runtime_sha": DEPLOYED_SHA,
        "canonical_repository_sha": CANONICAL_SHA,
        "service_before": "active",
        "service_after": "active",
        "runtime_db_read": "denied",
        "arbitrary_root_escalation": "denied",
        "restart_performed": False,
        "control_run_ids": ("34570000001", "34570000002"),
    }
    values.update(overrides)
    return p19e.EvidenceMetadata.build(**values)


def test_accepts_complete_24h_evidence_and_renders_required_fields():
    rendered = p19e.render_markdown(audit(), milestone="24h", metadata=metadata())

    assert "MILESTONE_RESULT = PASS" in rendered
    assert "BASELINE_UTC = 2026-09-11T07:38:44Z" in rendered
    assert "BOUNDARY_UTC = 2026-09-12T07:38:44Z" in rendered
    assert "TERMINAL_OBSERVATION_UTC = 2026-09-12T07:40:00Z" in rendered
    assert f"DEPLOYED_RUNTIME_SHA = {DEPLOYED_SHA}" in rendered
    assert f"CANONICAL_REPOSITORY_SHA_AT_CLOSURE = {CANONICAL_SHA}" in rendered
    assert "RESTART_PERFORMED = NO" in rendered


def test_rejects_milestone_without_terminal_pass():
    with pytest.raises(ValueError, match="milestone 24h is not PASS"):
        p19e.render_markdown(
            audit(status="WAITING_TERMINAL_OBSERVATION", terminal=None),
            milestone="24h",
            metadata=metadata(),
        )


def test_rejects_terminal_before_boundary_even_if_input_status_says_pass():
    with pytest.raises(ValueError, match="terminal observation precedes"):
        p19e.render_markdown(
            audit(terminal="2026-09-12T07:38:00Z"),
            milestone="24h",
            metadata=metadata(),
        )


def test_rejects_evidence_gap_over_bound():
    with pytest.raises(ValueError, match="gap exceeds"):
        p19e.render_markdown(audit(gap=7.01), milestone="24h", metadata=metadata())


def test_rejects_failed_control_count():
    with pytest.raises(ValueError, match="failed qualifying control count"):
        p19e.render_markdown(
            audit(),
            milestone="24h",
            metadata=metadata(failed_control_count=1),
        )


def test_rejects_non_active_service_boundary():
    with pytest.raises(ValueError, match="service_after must be active"):
        p19e.render_markdown(
            audit(),
            milestone="24h",
            metadata=metadata(service_after="failed"),
        )


def test_rejects_security_assertion_regression():
    with pytest.raises(ValueError, match="runtime DB read assertion"):
        p19e.render_markdown(
            audit(),
            milestone="24h",
            metadata=metadata(runtime_db_read="allowed"),
        )


def test_rejects_restart_during_closure_health_observation():
    with pytest.raises(ValueError, match="must not perform restart"):
        p19e.render_markdown(
            audit(),
            milestone="24h",
            metadata=metadata(restart_performed=True),
        )


def test_rejects_invalid_sha_metadata():
    with pytest.raises(ValueError, match="40-character lowercase hex SHA"):
        metadata(deployed_runtime_sha="not-a-sha")
