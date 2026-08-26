"""M13.5 forecast report and strategic outlook facade."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3

from .forecast_query import AdvancedForecastQuery
from .report_assembly import ReportAssembler, ReportAssemblyRequest
from .reporting_environment import (
    ANALYTICAL_CONTEXT,
    FORECAST,
    FORECAST_REPORT,
    FORECAST_SCENARIO,
    FORECAST_VERSION,
    SCENARIO_VERSION,
    STRATEGIC_OUTLOOK,
    ReportBundle,
    ReportReference,
    ReportSection,
    ReportSnapshot,
    SQLiteReportRepository,
)


@dataclass(frozen=True)
class ForecastReportSelection:
    finding_ids: tuple[str, ...] = ()
    graph_node_ids: tuple[str, ...] = ()
    graph_edge_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategicOutlookSelection:
    forecast_version_ids: tuple[str, ...]
    finding_ids: tuple[str, ...] = ()
    graph_node_ids: tuple[str, ...] = ()
    graph_edge_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not tuple(value for value in self.forecast_version_ids if str(value).strip()):
            raise ValueError("strategic outlook requires at least one explicit forecast version")


class ForecastReportingService:
    """Present durable M12 forecasts without promoting forecasts to facts."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.assembler = ReportAssembler(self.database_path)
        self.query = AdvancedForecastQuery(self.database_path)
        self.repository = SQLiteReportRepository(self.database_path)

    @staticmethod
    def _unique(values) -> tuple[str, ...]:
        return tuple(sorted({str(value).strip() for value in values if str(value).strip()}))

    def _version_identity(self, version_id: str) -> tuple[str, int]:
        normalized = str(version_id).strip()
        if not normalized:
            raise ValueError("forecast_version_id must not be empty")
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT forecast_id, version_number FROM forecast_versions WHERE forecast_version_id = ?",
                (normalized,),
            ).fetchone()
        if row is None:
            raise ValueError(f"unknown forecast version: {normalized}")
        return str(row[0]), int(row[1])

    def _scenario_sections(
        self,
        snapshot: ReportSnapshot,
        version_ids: tuple[str, ...],
        start_order: int,
    ) -> tuple[list[ReportSection], list[ReportReference]]:
        uncertainty = []
        invalidation = []
        scenario_refs = []
        for version_id in self._unique(version_ids):
            forecast_id, version_number = self._version_identity(version_id)
            scenarios = self.query.forecasts.list_scenarios(version_id)
            if not scenarios:
                raise ValueError(f"forecast version has no persisted scenarios: {version_id}")
            for scenario in scenarios:
                uncertainty.append(
                    {
                        "forecast_id": forecast_id,
                        "forecast_version_id": version_id,
                        "version_number": version_number,
                        "scenario_version_id": scenario.scenario_version_id,
                        "scenario_type": scenario.scenario_type,
                        "scenario_label": scenario.label,
                        "uncertainty_factors": list(scenario.uncertainty_factors),
                    }
                )
                invalidation.append(
                    {
                        "forecast_id": forecast_id,
                        "forecast_version_id": version_id,
                        "version_number": version_number,
                        "scenario_version_id": scenario.scenario_version_id,
                        "scenario_type": scenario.scenario_type,
                        "scenario_label": scenario.label,
                        "invalidation_signals": list(scenario.invalidation_signals),
                    }
                )
                scenario_refs.append((scenario.scenario_version_id, version_id, forecast_id))

        sections = []
        references = []
        for offset, (section_type, heading, content, explanation) in enumerate(
            (
                (
                    "UNCERTAINTY",
                    "Forecast uncertainty",
                    {"scenarios": uncertainty},
                    "Uncertainty factors are scenario analytics and do not alter source-evidence confidence or verification state.",
                ),
                (
                    "INVALIDATION_SIGNALS",
                    "Invalidation signals",
                    {"scenarios": invalidation},
                    "Invalidation signals identify conditions that would weaken a scenario; they are not observed facts unless separately evidenced.",
                ),
            )
        ):
            section = ReportSection.create(
                snapshot.report_id,
                start_order + offset,
                section_type,
                heading,
                FORECAST_SCENARIO,
                content,
                explanation,
                created_at=snapshot.created_at,
            )
            sections.append(section)
            for scenario_id, version_id, forecast_id in scenario_refs:
                for kind, value, role in (
                    (FORECAST, forecast_id, "FORECAST_CONTEXT"),
                    (FORECAST_VERSION, version_id, "FORECAST_VERSION_CONTEXT"),
                    (SCENARIO_VERSION, scenario_id, "SCENARIO_CONTEXT"),
                ):
                    references.append(
                        ReportReference.create(
                            snapshot.report_id,
                            kind,
                            value,
                            role,
                            section_id=section.section_id,
                            created_at=snapshot.created_at,
                        )
                    )
        return sections, references

    def _outcome_section(
        self,
        snapshot: ReportSnapshot,
        forecast_id: str,
        start_order: int,
    ) -> tuple[ReportSection | None, list[ReportReference]]:
        history = self.query.outcome_history(forecast_id)
        if not history:
            return None, []
        payload = []
        scenario_ids = []
        version_ids = []
        for view in history:
            outcome = view.outcome
            evaluations = []
            for item in view.evaluations:
                evaluations.append(
                    {
                        "evaluation_id": item.evaluation_id,
                        "forecast_version_id": item.forecast_version_id,
                        "scenario_version_id": item.scenario_version_id,
                        "scenario_type": item.scenario_type,
                        "scenario_label": item.scenario_label,
                        "raw_probability": item.raw_probability,
                        "calibrated_probability": item.calibrated_probability,
                        "observed_value": item.observed_value,
                        "brier_score_raw": item.brier_score_raw,
                        "brier_score_calibrated": item.brier_score_calibrated,
                        "calibration_error_raw": item.calibration_error_raw,
                        "calibration_error_calibrated": item.calibration_error_calibrated,
                        "sample_count": item.sample_count,
                        "evaluated_at": item.evaluated_at.isoformat(),
                    }
                )
                scenario_ids.append(item.scenario_version_id)
                version_ids.append(item.forecast_version_id)
            payload.append(
                {
                    "outcome_id": outcome.outcome_id,
                    "resolved_at": outcome.resolved_at.isoformat(),
                    "outcome_state": outcome.outcome_state,
                    "observed_scenario_type": outcome.observed_scenario_type,
                    "evidence_refs": list(outcome.evidence_refs),
                    "explanation": outcome.explanation,
                    "evaluations": evaluations,
                }
            )
        section = ReportSection.create(
            snapshot.report_id,
            start_order,
            "OUTCOME_EVALUATION",
            "Outcome and evaluation history",
            ANALYTICAL_CONTEXT,
            {"history": payload},
            "Historical evaluation is retrospective analytical performance metadata and does not rewrite the immutable forecast snapshot that was evaluated.",
            created_at=snapshot.created_at,
        )
        refs = [
            ReportReference.create(
                snapshot.report_id,
                FORECAST,
                forecast_id,
                "EVALUATED_FORECAST",
                section_id=section.section_id,
                created_at=snapshot.created_at,
            )
        ]
        for version_id in self._unique(version_ids):
            refs.append(
                ReportReference.create(
                    snapshot.report_id,
                    FORECAST_VERSION,
                    version_id,
                    "EVALUATED_VERSION",
                    section_id=section.section_id,
                    created_at=snapshot.created_at,
                )
            )
        for scenario_id in self._unique(scenario_ids):
            refs.append(
                ReportReference.create(
                    snapshot.report_id,
                    SCENARIO_VERSION,
                    scenario_id,
                    "EVALUATED_SCENARIO",
                    section_id=section.section_id,
                    created_at=snapshot.created_at,
                )
            )
        return section, refs

    def _calibration_section(
        self,
        snapshot: ReportSnapshot,
        forecast_id: str,
        start_order: int,
    ) -> tuple[ReportSection | None, list[ReportReference]]:
        history = self.query.calibration_history(forecast_id)
        if not history:
            return None, []
        payload = []
        for view in history:
            run = view.run
            payload.append(
                {
                    "calibration_id": run.calibration_id,
                    "method": run.calibration_method,
                    "method_version": run.calibration_method_version,
                    "horizon": run.cohort.horizon,
                    "scenario_type": run.cohort.scenario_type,
                    "sample_count": run.sample_count,
                    "raw_mean_probability": run.raw_mean_probability,
                    "calibrated_mean_probability": run.calibrated_mean_probability,
                    "observed_frequency": run.observed_frequency,
                    "raw_brier_mean": run.raw_brier_mean,
                    "calibrated_brier_mean": run.calibrated_brier_mean,
                    "raw_calibration_error_mean": run.raw_calibration_error_mean,
                    "calibrated_calibration_error_mean": run.calibrated_calibration_error_mean,
                    "created_at": run.created_at.isoformat(),
                    "buckets": [
                        {
                            "probability_basis": item.probability_basis,
                            "bucket_index": item.bucket_index,
                            "bucket_lower": item.bucket_lower,
                            "bucket_upper": item.bucket_upper,
                            "sample_count": item.sample_count,
                            "mean_probability": item.mean_probability,
                            "observed_frequency": item.observed_frequency,
                            "mean_brier_score": item.mean_brier_score,
                            "mean_calibration_error": item.mean_calibration_error,
                        }
                        for item in view.buckets
                    ],
                }
            )
        section = ReportSection.create(
            snapshot.report_id,
            start_order,
            "CALIBRATION_HISTORY",
            "Calibration history",
            ANALYTICAL_CONTEXT,
            {"history": payload},
            "Calibration history describes empirical model performance and does not change source verification confidence or past forecast-version probabilities.",
            created_at=snapshot.created_at,
        )
        reference = ReportReference.create(
            snapshot.report_id,
            FORECAST,
            forecast_id,
            "CALIBRATION_CONTEXT",
            section_id=section.section_id,
            created_at=snapshot.created_at,
        )
        return section, [reference]

    def _augment(
        self,
        base: ReportBundle,
        *,
        version_ids: tuple[str, ...],
        include_history_for_forecast: str | None,
        persist: bool,
    ) -> ReportBundle:
        sections = list(base.sections)
        references = list(base.references)
        scenario_sections, scenario_refs = self._scenario_sections(
            base.snapshot,
            version_ids,
            len(sections),
        )
        sections.extend(scenario_sections)
        references.extend(scenario_refs)

        if include_history_for_forecast is not None:
            outcome, outcome_refs = self._outcome_section(
                base.snapshot,
                include_history_for_forecast,
                len(sections),
            )
            if outcome is not None:
                sections.append(outcome)
                references.extend(outcome_refs)
            calibration, calibration_refs = self._calibration_section(
                base.snapshot,
                include_history_for_forecast,
                len(sections),
            )
            if calibration is not None:
                sections.append(calibration)
                references.extend(calibration_refs)

        bundle = ReportBundle(base.snapshot, tuple(sections), tuple(references))
        return self.repository.save_bundle(bundle) if persist else bundle

    def forecast_report(
        self,
        forecast_version_id: str,
        selection: ForecastReportSelection,
        *,
        title: str,
        summary: str,
        as_of: datetime,
        persist: bool = True,
    ) -> ReportBundle:
        forecast_id, version_number = self._version_identity(forecast_version_id)
        snapshot = ReportSnapshot.create(
            FORECAST_REPORT,
            f"forecast:{forecast_id}|version:{version_number}",
            title,
            summary,
            as_of,
            subject_ref_type=FORECAST_VERSION,
            subject_ref_id=forecast_version_id,
            created_at=as_of,
            generator_version="m13.5",
        )
        base = self.assembler.assemble(
            ReportAssemblyRequest(
                snapshot=snapshot,
                finding_ids=selection.finding_ids,
                graph_node_ids=selection.graph_node_ids,
                graph_edge_ids=selection.graph_edge_ids,
                forecast_version_ids=(forecast_version_id,),
                assumptions=selection.assumptions,
            ),
            persist=False,
        )
        return self._augment(
            base,
            version_ids=(forecast_version_id,),
            include_history_for_forecast=forecast_id,
            persist=persist,
        )

    def strategic_outlook(
        self,
        selection: StrategicOutlookSelection,
        *,
        title: str,
        summary: str,
        as_of: datetime,
        scope_key: str = "global:strategic-outlook",
        persist: bool = True,
    ) -> ReportBundle:
        versions = self._unique(selection.forecast_version_ids)
        for version_id in versions:
            self._version_identity(version_id)
        snapshot = ReportSnapshot.create(
            STRATEGIC_OUTLOOK,
            scope_key,
            title,
            summary,
            as_of,
            created_at=as_of,
            generator_version="m13.5",
        )
        base = self.assembler.assemble(
            ReportAssemblyRequest(
                snapshot=snapshot,
                finding_ids=selection.finding_ids,
                graph_node_ids=selection.graph_node_ids,
                graph_edge_ids=selection.graph_edge_ids,
                forecast_version_ids=versions,
                assumptions=selection.assumptions,
            ),
            persist=False,
        )
        return self._augment(
            base,
            version_ids=versions,
            include_history_for_forecast=None,
            persist=persist,
        )


__all__ = [
    "ForecastReportSelection",
    "StrategicOutlookSelection",
    "ForecastReportingService",
]
