from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


MILESTONES = {"24h", "72h", "7d"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def parse_utc(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _positive_id(value: str | int, field: str) -> str:
    text = str(value).strip()
    _require(text.isdigit() and int(text) > 0, f"{field} must be a positive integer")
    return text


def _sha(value: str, field: str) -> str:
    text = value.strip().lower()
    _require(bool(SHA_RE.fullmatch(text)), f"{field} must be a 40-character lowercase hex SHA")
    return text


@dataclass(frozen=True)
class EvidenceMetadata:
    attempt_id: str
    audit_run_id: str
    audit_job_id: str
    artifact_id: str
    failed_control_count: int
    deployed_runtime_sha: str
    canonical_repository_sha: str
    service_before: str
    service_after: str
    runtime_db_read: str
    arbitrary_root_escalation: str
    restart_performed: bool
    control_run_ids: tuple[str, ...]

    @classmethod
    def build(
        cls,
        *,
        attempt_id: str,
        audit_run_id: str | int,
        audit_job_id: str | int,
        artifact_id: str | int,
        failed_control_count: int,
        deployed_runtime_sha: str,
        canonical_repository_sha: str,
        service_before: str,
        service_after: str,
        runtime_db_read: str,
        arbitrary_root_escalation: str,
        restart_performed: bool,
        control_run_ids: Iterable[str | int],
    ) -> "EvidenceMetadata":
        attempt = attempt_id.strip()
        _require(bool(attempt), "attempt_id must be non-empty")
        _require(failed_control_count >= 0, "failed_control_count must be non-negative")

        controls = tuple(_positive_id(item, "control_run_id") for item in control_run_ids)
        _require(bool(controls), "at least one control_run_id is required")

        return cls(
            attempt_id=attempt,
            audit_run_id=_positive_id(audit_run_id, "audit_run_id"),
            audit_job_id=_positive_id(audit_job_id, "audit_job_id"),
            artifact_id=_positive_id(artifact_id, "artifact_id"),
            failed_control_count=failed_control_count,
            deployed_runtime_sha=_sha(deployed_runtime_sha, "deployed_runtime_sha"),
            canonical_repository_sha=_sha(canonical_repository_sha, "canonical_repository_sha"),
            service_before=service_before.strip(),
            service_after=service_after.strip(),
            runtime_db_read=runtime_db_read.strip(),
            arbitrary_root_escalation=arbitrary_root_escalation.strip(),
            restart_performed=restart_performed,
            control_run_ids=controls,
        )


def validate_milestone(audit: dict[str, object], *, milestone: str, metadata: EvidenceMetadata) -> dict[str, object]:
    _require(milestone in MILESTONES, f"unsupported milestone: {milestone}")
    _require(audit.get("schema_version") == "kgm.p19_soak_gate.v1", "unexpected audit schema_version")
    _require(audit.get("audit_status") == "PASS", "P19_SOAK_AUDIT must be PASS")
    _require(audit.get("continuity_status") == "PASS", "P19_CONTINUITY_STATUS must be PASS")

    milestones = audit.get("milestones")
    _require(isinstance(milestones, dict), "audit milestones must be an object")
    milestone_data = milestones.get(milestone)
    _require(isinstance(milestone_data, dict), f"missing milestone data for {milestone}")
    _require(milestone_data.get("status") == "PASS", f"milestone {milestone} is not PASS")

    boundary_text = milestone_data.get("boundary_utc")
    terminal_text = milestone_data.get("terminal_observation_utc")
    _require(isinstance(boundary_text, str) and boundary_text, "missing boundary_utc")
    _require(isinstance(terminal_text, str) and terminal_text, "missing terminal_observation_utc")
    boundary = parse_utc(boundary_text)
    terminal = parse_utc(terminal_text)
    _require(terminal >= boundary, "terminal observation precedes milestone boundary")

    max_gap = audit.get("current_max_gap_hours")
    max_allowed = audit.get("max_allowed_gap_hours")
    _require(isinstance(max_gap, (int, float)), "current_max_gap_hours must be numeric")
    _require(isinstance(max_allowed, (int, float)), "max_allowed_gap_hours must be numeric")
    _require(float(max_gap) <= float(max_allowed), "observed evidence gap exceeds allowed maximum")

    _require(metadata.failed_control_count == 0, "failed qualifying control count must be zero")
    _require(metadata.service_before == "active", "service_before must be active")
    _require(metadata.service_after == "active", "service_after must be active")
    _require(metadata.runtime_db_read == "denied", "runtime DB read assertion must be denied")
    _require(metadata.arbitrary_root_escalation == "denied", "arbitrary root escalation assertion must be denied")
    _require(not metadata.restart_performed, "automatic/closure health observation must not perform restart")

    count = audit.get("qualifying_observation_count_after_baseline")
    _require(isinstance(count, int) and count >= 1, "at least one post-baseline qualifying observation is required")

    baseline = audit.get("baseline_utc")
    _require(isinstance(baseline, str) and baseline, "missing baseline_utc")
    parse_utc(baseline)

    return milestone_data


def render_markdown(audit: dict[str, object], *, milestone: str, metadata: EvidenceMetadata) -> str:
    milestone_data = validate_milestone(audit, milestone=milestone, metadata=metadata)
    control_runs = ", ".join(metadata.control_run_ids)

    fields = [
        ("ATTEMPT_ID", metadata.attempt_id),
        ("MILESTONE", milestone),
        ("BASELINE_UTC", str(audit["baseline_utc"])),
        ("BOUNDARY_UTC", str(milestone_data["boundary_utc"])),
        ("TERMINAL_OBSERVATION_UTC", str(milestone_data["terminal_observation_utc"])),
        ("AUDIT_RUN_ID", metadata.audit_run_id),
        ("AUDIT_JOB_ID", metadata.audit_job_id),
        ("ARTIFACT_ID", metadata.artifact_id),
        ("QUALIFYING_OBSERVATION_COUNT_AFTER_BASELINE", str(audit["qualifying_observation_count_after_baseline"])),
        ("FAILED_CONTROL_COUNT", str(metadata.failed_control_count)),
        ("MAX_OBSERVED_GAP_HOURS", str(audit["current_max_gap_hours"])),
        ("MAX_ALLOWED_GAP_HOURS", str(audit["max_allowed_gap_hours"])),
        ("CONTROL_RUN_IDS", control_runs),
        ("DEPLOYED_RUNTIME_SHA", metadata.deployed_runtime_sha),
        ("CANONICAL_REPOSITORY_SHA_AT_CLOSURE", metadata.canonical_repository_sha),
        ("SERVICE_BEFORE", metadata.service_before),
        ("SERVICE_AFTER", metadata.service_after),
        ("RUNTIME_DB_READ", metadata.runtime_db_read),
        ("ARBITRARY_ROOT_ESCALATION", metadata.arbitrary_root_escalation),
        ("RESTART_PERFORMED", "YES" if metadata.restart_performed else "NO"),
        ("P19_SOAK_AUDIT", str(audit["audit_status"])),
        ("P19_CONTINUITY_STATUS", str(audit["continuity_status"])),
        ("MILESTONE_RESULT", str(milestone_data["status"])),
    ]

    lines = [
        f"# Phase 19 {milestone} Real-Soak Evidence",
        "",
        "Status: `ACCEPTED_MILESTONE_EVIDENCE`",
        "",
        "```text",
    ]
    lines.extend(f"{key} = {value}" for key, value in fields)
    lines.extend(
        [
            "```",
            "",
            "This record was generated from a P19 soak-audit JSON document and explicit closure metadata.",
            "Generation is offline and does not mutate runtime, baseline, cadence, trust path, or GitHub Actions state.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and render durable P19 milestone evidence.")
    parser.add_argument("--audit-json", required=True, type=Path)
    parser.add_argument("--milestone", required=True, choices=sorted(MILESTONES))
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--audit-run-id", required=True)
    parser.add_argument("--audit-job-id", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--failed-control-count", required=True, type=int)
    parser.add_argument("--deployed-runtime-sha", required=True)
    parser.add_argument("--canonical-repository-sha", required=True)
    parser.add_argument("--service-before", required=True)
    parser.add_argument("--service-after", required=True)
    parser.add_argument("--runtime-db-read", required=True)
    parser.add_argument("--arbitrary-root-escalation", required=True)
    parser.add_argument("--restart-performed", required=True, choices=("yes", "no"))
    parser.add_argument("--control-run-id", required=True, action="append")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    audit = json.loads(args.audit_json.read_text(encoding="utf-8"))
    metadata = EvidenceMetadata.build(
        attempt_id=args.attempt_id,
        audit_run_id=args.audit_run_id,
        audit_job_id=args.audit_job_id,
        artifact_id=args.artifact_id,
        failed_control_count=args.failed_control_count,
        deployed_runtime_sha=args.deployed_runtime_sha,
        canonical_repository_sha=args.canonical_repository_sha,
        service_before=args.service_before,
        service_after=args.service_after,
        runtime_db_read=args.runtime_db_read,
        arbitrary_root_escalation=args.arbitrary_root_escalation,
        restart_performed=args.restart_performed == "yes",
        control_run_ids=args.control_run_id,
    )

    try:
        rendered = render_markdown(audit, milestone=args.milestone, metadata=metadata)
    except ValueError as exc:
        raise SystemExit(f"P19_MILESTONE_EVIDENCE=REJECTED: {exc}") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print("P19_MILESTONE_EVIDENCE=PASS")
    print(f"P19_MILESTONE={args.milestone}")
    print(f"P19_EVIDENCE_OUTPUT={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
