"""M13.3 type-specific brief facade over the common report assembler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import sqlite3

from .region_language_coverage import normalize_language_code, normalize_region_code
from .report_assembly import ReportAssembler, ReportAssemblyRequest
from .reporting_environment import (
    ALERT,
    GLOBAL_GEOPOLITICAL_BRIEF,
    REGION,
    REGIONAL_COUNTRY_BRIEF,
    STRATEGIC_ALERT,
    ReportBundle,
    ReportSnapshot,
)


@dataclass(frozen=True)
class BriefSelection:
    finding_ids: tuple[str, ...] = ()
    alert_ids: tuple[str, ...] = ()
    forecast_version_ids: tuple[str, ...] = ()
    graph_node_ids: tuple[str, ...] = ()
    graph_edge_ids: tuple[str, ...] = ()
    coverage_report_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def has_primary_intelligence(self) -> bool:
        return bool(self.finding_ids or self.alert_ids or self.forecast_version_ids)


class BriefReportService:
    """Build approved M13.3 briefs without creating report-specific truth stores."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.assembler = ReportAssembler(self.database_path)

    @staticmethod
    def _require_primary_selection(selection: BriefSelection) -> None:
        if not selection.has_primary_intelligence():
            raise ValueError(
                "brief requires explicit finding, alert or forecast-version selection"
            )

    def _assembly_request(
        self,
        snapshot: ReportSnapshot,
        selection: BriefSelection,
    ) -> ReportAssemblyRequest:
        return ReportAssemblyRequest(
            snapshot=snapshot,
            finding_ids=selection.finding_ids,
            alert_ids=selection.alert_ids,
            coverage_report_ids=selection.coverage_report_ids,
            graph_node_ids=selection.graph_node_ids,
            graph_edge_ids=selection.graph_edge_ids,
            forecast_version_ids=selection.forecast_version_ids,
            assumptions=selection.assumptions,
        )

    def _alert_subject(self, alert_id: str) -> tuple[str, str, str, str]:
        value = str(alert_id).strip()
        if not value:
            raise ValueError("alert_id must not be empty")
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT a.finding_id, a.priority, a.status, f.title, f.summary
                FROM strategic_alerts AS a
                JOIN operational_findings AS f ON f.finding_id = a.finding_id
                WHERE a.alert_id = ?
                """,
                (value,),
            ).fetchone()
        if row is None:
            raise ValueError(f"unknown strategic alert: {value}")
        finding_id, priority, status, finding_title, finding_summary = row
        title = f"Strategic alert: {finding_title}"
        summary = f"{priority} / {status}: {finding_summary}"
        return str(finding_id), title, summary, value

    def strategic_alert_report(
        self,
        alert_id: str,
        *,
        as_of: datetime,
        persist: bool = True,
    ) -> ReportBundle:
        finding_id, title, summary, normalized_alert_id = self._alert_subject(alert_id)
        snapshot = ReportSnapshot.create(
            STRATEGIC_ALERT,
            f"alert:{normalized_alert_id}",
            title,
            summary,
            as_of,
            subject_ref_type=ALERT,
            subject_ref_id=normalized_alert_id,
            created_at=as_of,
            generator_version="m13.3",
        )
        selection = BriefSelection(
            finding_ids=(finding_id,),
            alert_ids=(normalized_alert_id,),
        )
        return self.assembler.assemble(
            self._assembly_request(snapshot, selection),
            persist=persist,
        )

    def global_brief(
        self,
        selection: BriefSelection,
        *,
        title: str,
        summary: str,
        as_of: datetime,
        scope_key: str = "global",
        persist: bool = True,
    ) -> ReportBundle:
        self._require_primary_selection(selection)
        snapshot = ReportSnapshot.create(
            GLOBAL_GEOPOLITICAL_BRIEF,
            scope_key,
            title,
            summary,
            as_of,
            created_at=as_of,
            generator_version="m13.3",
        )
        return self.assembler.assemble(
            self._assembly_request(snapshot, selection),
            persist=persist,
        )

    def _validate_region_language_scope(
        self,
        region_code: str,
        language_codes: tuple[str, ...],
        coverage_report_ids: tuple[str, ...],
    ) -> tuple[str, tuple[str, ...]]:
        region = normalize_region_code(region_code)
        languages = tuple(
            sorted({normalize_language_code(item) for item in language_codes})
        )
        if not languages:
            raise ValueError("regional brief requires at least one language")
        if not coverage_report_ids:
            raise ValueError("regional brief requires region-language coverage metadata")

        with sqlite3.connect(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM region_catalog WHERE region_code = ?",
                (region,),
            ).fetchone() is None:
                raise ValueError(f"unknown region: {region}")
            for language in languages:
                if connection.execute(
                    "SELECT 1 FROM language_catalog WHERE language_code = ?",
                    (language,),
                ).fetchone() is None:
                    raise ValueError(f"unknown language: {language}")

            required_pairs = {f"{region}:{language}" for language in languages}
            for report_id in sorted(set(coverage_report_ids)):
                row = connection.execute(
                    """
                    SELECT required_scopes
                    FROM region_language_coverage_reports
                    WHERE report_id = ?
                    """,
                    (report_id,),
                ).fetchone()
                if row is None:
                    raise ValueError(
                        f"regional brief requires a region-language coverage report: {report_id}"
                    )
                report_scopes = set(json.loads(row[0]))
                if not required_pairs.issubset(report_scopes):
                    missing = sorted(required_pairs - report_scopes)
                    raise ValueError(
                        "coverage report does not cover requested regional scope: "
                        + ", ".join(missing)
                    )
        return region, languages

    def regional_brief(
        self,
        region_code: str,
        language_codes: tuple[str, ...],
        selection: BriefSelection,
        *,
        title: str,
        summary: str,
        as_of: datetime,
        persist: bool = True,
    ) -> ReportBundle:
        self._require_primary_selection(selection)
        region, languages = self._validate_region_language_scope(
            region_code,
            language_codes,
            selection.coverage_report_ids,
        )
        snapshot = ReportSnapshot.create(
            REGIONAL_COUNTRY_BRIEF,
            f"region:{region}|languages:{','.join(languages)}",
            title,
            summary,
            as_of,
            subject_ref_type=REGION,
            subject_ref_id=region,
            created_at=as_of,
            generator_version="m13.3",
        )
        return self.assembler.assemble(
            self._assembly_request(snapshot, selection),
            persist=persist,
        )


__all__ = ["BriefSelection", "BriefReportService"]
