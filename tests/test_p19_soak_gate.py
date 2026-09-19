from __future__ import annotations

import importlib.util
from datetime import timedelta
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "p19_soak_gate.py"
SPEC = importlib.util.spec_from_file_location("p19_soak_gate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
p19 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p19)


def ts(value: str):
    return p19.parse_utc(value)


def test_before_24h_remains_in_progress_with_clean_continuity():
    result = p19.evaluate_soak(
        baseline=ts("2026-09-10T00:19:31Z"),
        now=ts("2026-09-10T20:19:31Z"),
        observations=[
            "2026-09-10T06:27:30Z",
            "2026-09-10T12:28:00Z",
            "2026-09-10T18:28:30Z",
        ],
    )

    assert result["audit_status"] == "PASS"
    assert result["continuity_status"] == "PASS"
    assert result["milestones"]["24h"]["status"] == "IN_PROGRESS"


def test_24h_requires_post_boundary_terminal_observation():
    result = p19.evaluate_soak(
        baseline=ts("2026-09-10T00:19:31Z"),
        now=ts("2026-09-11T00:25:00Z"),
        observations=[
            "2026-09-10T06:27:30Z",
            "2026-09-10T12:27:40Z",
            "2026-09-10T18:27:50Z",
            "2026-09-11T00:18:50Z",
        ],
    )

    assert result["audit_status"] == "PASS"
    assert result["milestones"]["24h"]["status"] == "WAITING_TERMINAL_OBSERVATION"


def test_24h_passes_with_clean_post_boundary_terminal_observation():
    result = p19.evaluate_soak(
        baseline=ts("2026-09-10T00:19:31Z"),
        now=ts("2026-09-11T00:30:00Z"),
        observations=[
            "2026-09-10T06:27:30Z",
            "2026-09-10T12:27:40Z",
            "2026-09-10T18:27:50Z",
            "2026-09-11T00:28:10Z",
        ],
    )

    assert result["audit_status"] == "PASS"
    assert result["milestones"]["24h"]["status"] == "PASS"
    assert result["milestones"]["72h"]["status"] == "IN_PROGRESS"


def test_gap_over_seven_hours_fails_continuity():
    result = p19.evaluate_soak(
        baseline=ts("2026-09-10T00:19:31Z"),
        now=ts("2026-09-10T14:30:00Z"),
        observations=["2026-09-10T06:27:30Z"],
        max_gap=timedelta(hours=7),
    )

    assert result["audit_status"] == "FAIL_CONTINUITY"
    assert result["continuity_status"] == "FAIL_CONTINUITY"


def test_72h_passes_only_after_clean_terminal_observation():
    baseline = ts("2026-09-10T00:19:31Z")
    observations = [baseline + timedelta(hours=6, minutes=8)]
    while observations[-1] < baseline + timedelta(hours=66):
        observations.append(observations[-1] + timedelta(hours=6))
    observations.append(baseline + timedelta(hours=72, minutes=8))

    result = p19.evaluate_soak(
        baseline=baseline,
        now=baseline + timedelta(hours=72, minutes=10),
        observations=observations,
    )

    assert result["milestones"]["24h"]["status"] == "PASS"
    assert result["milestones"]["72h"]["status"] == "PASS"
    assert result["milestones"]["7d"]["status"] == "IN_PROGRESS"


def test_7d_passes_with_clean_full_window():
    baseline = ts("2026-09-10T00:19:31Z")
    observations = []
    current = baseline + timedelta(hours=6, minutes=8)
    while current < baseline + timedelta(hours=168):
        observations.append(current)
        current += timedelta(hours=6)
    observations.append(baseline + timedelta(hours=168, minutes=8))

    result = p19.evaluate_soak(
        baseline=baseline,
        now=baseline + timedelta(hours=168, minutes=10),
        observations=observations,
    )

    assert result["audit_status"] == "PASS"
    assert result["milestones"]["24h"]["status"] == "PASS"
    assert result["milestones"]["72h"]["status"] == "PASS"
    assert result["milestones"]["7d"]["status"] == "PASS"


def test_retired_audit_is_manual_observation_only_while_historical_dispatcher_contract_is_preserved():
    root = Path(__file__).resolve().parents[1]
    dispatcher = (root / ".github/workflows/p19-owner-local-real-soak-dispatch.yml").read_text(
        encoding="utf-8"
    )
    audit = (root / ".github/workflows/p19-owner-local-soak-gate-audit.yml").read_text(
        encoding="utf-8"
    )
    control = (root / ".github/workflows/tailscale-kgm-control.yml").read_text(encoding="utf-8")
    baseline = (root / "ops/p19/real_soak_baseline.txt").read_text(encoding="utf-8").strip()

    target_cadence_hours = 3
    max_gap_hours = 7

    assert "cron: '27 */3 * * *'" in dispatcher
    assert "workflow_dispatch:" in audit
    assert "workflow_run:" not in audit
    assert "cron:" not in audit
    assert "P19_RETIRED_CONTINUITY_AUDIT=OBSERVATION_ONLY" in audit
    assert "--max-gap-hours 7" in audit
    assert target_cadence_hours * 2 < max_gap_hours
    assert "ops/p19/real_soak_baseline.txt" in audit
    assert "ops/p19/real_soak_baseline.txt" in control
    assert baseline.endswith("Z")
