"""M13.6 deterministic rendering for persisted reporting snapshots."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .forecast_semantics import forecast_semantic_contract
from .reporting_environment import FORECAST_SCENARIO, ReportBundle, SQLiteReportRepository
from .runtime_storage import RuntimeStoragePolicy


def _canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _canonical_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    return value


def _section_sort_key(section: Any) -> tuple[int, str]:
    return (int(section.section_order), str(section.section_id))


def _reference_sort_key(reference: Any) -> tuple[str, str, str, str, str]:
    return (
        reference.section_id or "",
        reference.reference_kind,
        reference.reference_value,
        reference.reference_role,
        reference.reference_id,
    )


def _canonical_json(value: Any, *, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(
            _canonical_value(value),
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
        )
    return json.dumps(
        _canonical_value(value),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


class ReportRenderer:
    """Read-only deterministic renderer over the canonical M13 report repository."""

    def __init__(self, repository: SQLiteReportRepository):
        self.repository = repository

    def _load(self, report_id: str) -> ReportBundle:
        bundle = self.repository.get_bundle(report_id)
        if bundle is None:
            raise ValueError(f"unknown persisted report: {report_id}")
        return bundle

    @staticmethod
    def structured_bundle(bundle: ReportBundle) -> dict[str, Any]:
        snapshot = bundle.snapshot
        sections = tuple(sorted(bundle.sections, key=_section_sort_key))
        references = tuple(sorted(bundle.references, key=_reference_sort_key))
        has_forecast = any(
            section.presentation_class == FORECAST_SCENARIO for section in sections
        )

        return {
            "snapshot": {
                "report_id": snapshot.report_id,
                "report_type": snapshot.report_type,
                "scope_key": snapshot.scope_key,
                "subject": (
                    None
                    if snapshot.subject_ref_type is None
                    else {
                        "reference_kind": snapshot.subject_ref_type,
                        "reference_value": snapshot.subject_ref_id,
                    }
                ),
                "title": snapshot.title,
                "summary": snapshot.summary,
                "as_of": snapshot.as_of.isoformat(),
                "created_at": snapshot.created_at.isoformat(),
                "generator_version": snapshot.generator_version,
            },
            "forecast_semantics": forecast_semantic_contract() if has_forecast else None,
            "sections": [
                {
                    "section_id": section.section_id,
                    "section_order": int(section.section_order),
                    "section_type": section.section_type,
                    "heading": section.heading,
                    "presentation_class": section.presentation_class,
                    "content": _canonical_value(section.content),
                    "explanation": section.explanation,
                    "created_at": section.created_at.isoformat(),
                }
                for section in sections
            ],
            "references": [
                {
                    "reference_id": reference.reference_id,
                    "section_id": reference.section_id,
                    "reference_kind": reference.reference_kind,
                    "reference_value": reference.reference_value,
                    "reference_role": reference.reference_role,
                    "created_at": reference.created_at.isoformat(),
                }
                for reference in references
            ],
        }

    @classmethod
    def structured_json_bundle(cls, bundle: ReportBundle) -> str:
        return _canonical_json(cls.structured_bundle(bundle))

    @classmethod
    def markdown_bundle(cls, bundle: ReportBundle) -> str:
        data = cls.structured_bundle(bundle)
        snapshot = data["snapshot"]
        lines = [
            f"# {snapshot['title']}",
            "",
            f"- Report ID: `{snapshot['report_id']}`",
            f"- Report type: `{snapshot['report_type']}`",
            f"- Scope: `{snapshot['scope_key']}`",
            f"- As of: `{snapshot['as_of']}`",
            f"- Generator: `{snapshot['generator_version']}`",
        ]
        subject = snapshot["subject"]
        if subject is not None:
            lines.append(
                f"- Subject: `{subject['reference_kind']}:{subject['reference_value']}`"
            )

        lines.extend(["", "## Summary", "", snapshot["summary"]])

        forecast_semantics = data.get("forecast_semantics")
        if isinstance(forecast_semantics, dict):
            lines.extend(
                [
                    "",
                    "## Forecast semantics",
                    "",
                    f"- Contract: `{forecast_semantics['version']}`",
                    "- Raw probability: analytical scenario probability before calibration; not factual or verification confidence.",
                    "- Calibrated probability: calibrated analytical scenario probability; not factual or verification confidence.",
                    "- Scenario confidence: confidence in the scenario assessment; not scenario probability and not claim verification confidence.",
                    "- Forecast metrics never modify verification state, evidence confidence, or independent-origin counts.",
                ]
            )

        for section in data["sections"]:
            lines.extend(
                [
                    "",
                    f"## {section['section_order'] + 1}. {section['heading']}",
                    "",
                    f"Presentation class: `{section['presentation_class']}`",
                    "",
                ]
            )
            content = section["content"]
            if isinstance(content, str):
                lines.append(content)
            else:
                lines.extend(
                    [
                        "```json",
                        _canonical_json(content, pretty=True),
                        "```",
                    ]
                )
            lines.extend(["", f"Explanation: {section['explanation']}"])

        if data["references"]:
            lines.extend(["", "## References", ""])
            for reference in data["references"]:
                section_scope = reference["section_id"] or "REPORT"
                lines.append(
                    "- "
                    f"`{reference['reference_kind']}:{reference['reference_value']}` "
                    f"role `{reference['reference_role']}`; section `{section_scope}`; "
                    f"reference `{reference['reference_id']}`"
                )

        return "\n".join(lines).rstrip() + "\n"

    def structured(self, report_id: str) -> dict[str, Any]:
        return self.structured_bundle(self._load(report_id))

    def structured_json(self, report_id: str) -> str:
        return self.structured_json_bundle(self._load(report_id))

    def markdown(self, report_id: str) -> str:
        return self.markdown_bundle(self._load(report_id))

    def digest(self, report_id: str) -> str:
        return sha256(self.structured_json(report_id).encode("utf-8")).hexdigest()


class ProjectLocalReportRenderer(ReportRenderer):
    """Runtime entry point that enforces the existing project-local DB boundary."""

    @classmethod
    def open(
        cls,
        project_root: str | Path,
        database_path: str | Path | None = None,
    ) -> "ProjectLocalReportRenderer":
        policy = RuntimeStoragePolicy(Path(project_root))
        resolved = policy.resolve_database(database_path)
        return cls(SQLiteReportRepository(resolved))


__all__ = ["ReportRenderer", "ProjectLocalReportRenderer"]
