"""M13.2 common deterministic report assembly and provenance adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from typing import Iterable

from .forecast_query import AdvancedForecastQuery
from .reporting_environment import (
    ANALYTICAL_CONTEXT,
    ANALYST_ASSUMPTION,
    ALERT,
    CLAIM,
    COVERAGE_METADATA,
    COVERAGE_REPORT,
    FINDING,
    FORECAST,
    FORECAST_SCENARIO,
    FORECAST_VERSION,
    GRAPH_EDGE,
    GRAPH_INFERENCE,
    GRAPH_NODE,
    RAW_ITEM,
    SCENARIO_VERSION,
    SOURCE,
    ReportBundle,
    ReportReference,
    ReportSection,
    ReportSnapshot,
    SQLiteReportRepository,
)


@dataclass(frozen=True)
class ReportAssemblyRequest:
    snapshot: ReportSnapshot
    finding_ids: tuple[str, ...] = ()
    alert_ids: tuple[str, ...] = ()
    coverage_report_ids: tuple[str, ...] = ()
    graph_node_ids: tuple[str, ...] = ()
    graph_edge_ids: tuple[str, ...] = ()
    forecast_version_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()


class ReportAssembler:
    """Assemble existing durable outputs into one immutable reporting contract."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.repository = SQLiteReportRepository(self.database_path)
        self.forecast_query = AdvancedForecastQuery(self.database_path)

    @staticmethod
    def _unique(values: Iterable[str]) -> tuple[str, ...]:
        return tuple(sorted({str(value).strip() for value in values if str(value).strip()}))

    def _finding_payloads(self, ids: tuple[str, ...]):
        if not ids:
            return (), (), ()
        placeholders = ",".join("?" for _ in ids)
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT finding_id, title, summary, importance, confidence,
                       evidence_refs, explanation, created_at
                FROM operational_findings
                WHERE finding_id IN ({placeholders})
                ORDER BY importance DESC, confidence DESC, finding_id
                """,
                ids,
            ).fetchall()
        found = {row[0] for row in rows}
        missing = sorted(set(ids) - found)
        if missing:
            raise ValueError(f"unknown finding reference(s): {', '.join(missing)}")

        payloads = []
        references = []
        source_refs: set[tuple[str, str]] = set()
        for row in rows:
            evidence_refs = tuple(json.loads(row[5]))
            payloads.append(
                {
                    "finding_id": row[0],
                    "title": row[1],
                    "summary": row[2],
                    "importance": float(row[3]),
                    "confidence": float(row[4]),
                    "evidence_refs": list(evidence_refs),
                    "explanation": row[6],
                    "created_at": row[7],
                }
            )
            references.append((FINDING, row[0], "ANALYTICAL_INPUT"))
            for token in evidence_refs:
                if token.startswith("claim:"):
                    source_refs.add((CLAIM, token.split(":", 1)[1]))
                elif token.startswith("raw_item:"):
                    raw_id = token.split(":", 1)[1]
                    source_refs.add((RAW_ITEM, raw_id))
                    with sqlite3.connect(self.database_path) as connection:
                        source_row = connection.execute(
                            "SELECT source_id FROM raw_items WHERE id = ?",
                            (raw_id,),
                        ).fetchone()
                    if source_row is not None and source_row[0]:
                        source_refs.add((SOURCE, str(source_row[0])))
        return tuple(payloads), tuple(references), tuple(sorted(source_refs))

    def _alert_payloads(self, ids: tuple[str, ...]):
        if not ids:
            return (), ()
        placeholders = ",".join("?" for _ in ids)
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT alert_id, finding_id, trigger_type, priority, status,
                       first_triggered_at, last_updated_at, evidence_refs,
                       explanation, invalidation_reason
                FROM strategic_alerts
                WHERE alert_id IN ({placeholders})
                ORDER BY CASE priority WHEN 'CRITICAL' THEN 2 WHEN 'HIGH' THEN 1 ELSE 0 END DESC,
                         alert_id
                """,
                ids,
            ).fetchall()
        found = {row[0] for row in rows}
        missing = sorted(set(ids) - found)
        if missing:
            raise ValueError(f"unknown alert reference(s): {', '.join(missing)}")
        payloads = tuple(
            {
                "alert_id": row[0],
                "finding_id": row[1],
                "trigger_type": row[2],
                "priority": row[3],
                "status": row[4],
                "first_triggered_at": row[5],
                "last_updated_at": row[6],
                "evidence_refs": list(json.loads(row[7])),
                "explanation": row[8],
                "invalidation_reason": row[9],
            }
            for row in rows
        )
        refs = tuple(
            item
            for row in rows
            for item in ((ALERT, row[0], "ALERT_INPUT"), (FINDING, row[1], "ALERT_FINDING"))
        )
        return payloads, refs

    def _coverage_payloads(self, ids: tuple[str, ...]):
        payloads = []
        refs = []
        for report_id in ids:
            with sqlite3.connect(self.database_path) as connection:
                row = connection.execute(
                    """
                    SELECT report_id, watch_id, required_scopes, observed_scopes,
                           observed_regions, observed_languages, missing_scopes,
                           coverage_ratio, created_at
                    FROM region_language_coverage_reports WHERE report_id = ?
                    """,
                    (report_id,),
                ).fetchone()
                if row is not None:
                    payloads.append(
                        {
                            "coverage_report_id": row[0],
                            "watch_id": row[1],
                            "required_scopes": json.loads(row[2]),
                            "observed_scopes": json.loads(row[3]),
                            "observed_regions": json.loads(row[4]),
                            "observed_languages": json.loads(row[5]),
                            "missing_scopes": json.loads(row[6]),
                            "coverage_ratio": float(row[7]),
                            "created_at": row[8],
                        }
                    )
                    refs.append((COVERAGE_REPORT, report_id, "COVERAGE_INPUT"))
                    continue
                pilot = connection.execute(
                    """
                    SELECT run_id, watch_id, examined_count, matched_count,
                           source_classes, coverage_confidence, gaps, created_at
                    FROM pilot_coverage_reports WHERE run_id = ?
                    """,
                    (report_id,),
                ).fetchone()
            if pilot is None:
                raise ValueError(f"unknown coverage report reference: {report_id}")
            payloads.append(
                {
                    "coverage_report_id": pilot[0],
                    "watch_id": pilot[1],
                    "examined_count": int(pilot[2]),
                    "matched_count": int(pilot[3]),
                    "source_classes": json.loads(pilot[4]),
                    "coverage_confidence": float(pilot[5]),
                    "gaps": json.loads(pilot[6]),
                    "created_at": pilot[7],
                }
            )
            refs.append((COVERAGE_REPORT, report_id, "COVERAGE_INPUT"))
        return tuple(sorted(payloads, key=lambda item: item["coverage_report_id"])), tuple(refs)

    def _graph_payload(self, node_ids: tuple[str, ...], edge_ids: tuple[str, ...]):
        nodes = []
        edges = []
        refs = []
        with sqlite3.connect(self.database_path) as connection:
            for node_id in node_ids:
                row = connection.execute(
                    """
                    SELECT node_id, node_kind, canonical_ref_type, canonical_ref_id,
                           label, attributes_json
                    FROM graph_nodes WHERE node_id = ?
                    """,
                    (node_id,),
                ).fetchone()
                if row is None:
                    raise ValueError(f"unknown graph node reference: {node_id}")
                nodes.append(
                    {
                        "node_id": row[0],
                        "node_kind": row[1],
                        "canonical_ref_type": row[2],
                        "canonical_ref_id": row[3],
                        "label": row[4],
                        "attributes": json.loads(row[5]),
                    }
                )
                refs.append((GRAPH_NODE, node_id, "GRAPH_CONTEXT"))
            for edge_id in edge_ids:
                row = connection.execute(
                    """
                    SELECT edge_id, source_node_id, target_node_id, relation_type,
                           relation_class, confidence, status, valid_from, valid_to,
                           explanation
                    FROM graph_edges WHERE edge_id = ?
                    """,
                    (edge_id,),
                ).fetchone()
                if row is None:
                    raise ValueError(f"unknown graph edge reference: {edge_id}")
                evidence = connection.execute(
                    """
                    SELECT evidence_ref, evidence_role FROM graph_edge_evidence
                    WHERE edge_id = ? ORDER BY evidence_role, evidence_ref
                    """,
                    (edge_id,),
                ).fetchall()
                edges.append(
                    {
                        "edge_id": row[0],
                        "source_node_id": row[1],
                        "target_node_id": row[2],
                        "relation_type": row[3],
                        "relation_class": row[4],
                        "confidence": float(row[5]),
                        "status": row[6],
                        "valid_from": row[7],
                        "valid_to": row[8],
                        "explanation": row[9],
                        "evidence": [
                            {"evidence_ref": item[0], "evidence_role": item[1]}
                            for item in evidence
                        ],
                    }
                )
                refs.append((GRAPH_EDGE, edge_id, "GRAPH_CONTEXT"))
        return {"nodes": nodes, "edges": edges}, tuple(refs)

    def _forecast_payloads(self, version_ids: tuple[str, ...]):
        payloads = []
        refs = []
        for version_id in version_ids:
            explanation = self.forecast_query.explain_version(version_id)
            with sqlite3.connect(self.database_path) as connection:
                row = connection.execute(
                    "SELECT forecast_id, version_number FROM forecast_versions WHERE forecast_version_id = ?",
                    (version_id,),
                ).fetchone()
            if row is None:
                raise ValueError(f"unknown forecast version reference: {version_id}")
            scenarios = self.forecast_query.forecasts.list_scenarios(version_id)
            payloads.append(
                {
                    "forecast_id": row[0],
                    "forecast_version_id": version_id,
                    "version_number": int(row[1]),
                    "scenarios": [
                        {
                            "scenario_version_id": item.scenario_version_id,
                            "scenario_type": item.scenario_type,
                            "label": item.label,
                            "raw_probability": item.raw_probability,
                            "calibrated_probability": item.calibrated_probability,
                            "scenario_confidence": item.scenario_confidence,
                            "drivers": list(item.drivers),
                            "constraints": list(item.constraints),
                            "triggers": list(item.triggers),
                            "inhibitors": list(item.inhibitors),
                            "uncertainty_factors": list(item.uncertainty_factors),
                            "invalidation_signals": list(item.invalidation_signals),
                        }
                        for item in scenarios
                    ],
                    "provenance_explanation": explanation.text,
                    "source_evidence_refs": list(explanation.source_evidence_refs),
                    "graph_relationship_refs": list(explanation.graph_relationship_refs),
                }
            )
            refs.append((FORECAST, row[0], "FORECAST_INPUT"))
            refs.append((FORECAST_VERSION, version_id, "FORECAST_VERSION"))
            refs.extend((SCENARIO_VERSION, item.scenario_version_id, "SCENARIO") for item in scenarios)
            refs.extend((RAW_ITEM, raw_id, "FORECAST_SOURCE_EVIDENCE") for raw_id in explanation.source_evidence_refs)
            refs.extend((GRAPH_EDGE, edge_id, "FORECAST_GRAPH_CONTEXT") for edge_id in explanation.graph_relationship_refs)
        return tuple(sorted(payloads, key=lambda item: (item["forecast_id"], item["version_number"]))), tuple(refs)

    def assemble(self, request: ReportAssemblyRequest, *, persist: bool = True) -> ReportBundle:
        finding_ids = self._unique(request.finding_ids)
        alert_ids = self._unique(request.alert_ids)
        coverage_ids = self._unique(request.coverage_report_ids)
        node_ids = self._unique(request.graph_node_ids)
        edge_ids = self._unique(request.graph_edge_ids)
        forecast_ids = self._unique(request.forecast_version_ids)
        assumptions = self._unique(request.assumptions)

        finding_payloads, finding_refs, source_refs = self._finding_payloads(finding_ids)
        alert_payloads, alert_refs = self._alert_payloads(alert_ids)
        coverage_payloads, coverage_refs = self._coverage_payloads(coverage_ids)
        graph_payload, graph_refs = self._graph_payload(node_ids, edge_ids)
        forecast_payloads, forecast_refs = self._forecast_payloads(forecast_ids)

        sections = []
        reference_specs = []
        order = 0

        def add_section(section_type, heading, presentation_class, content, explanation, specs):
            nonlocal order
            section = ReportSection.create(
                request.snapshot.report_id,
                order,
                section_type,
                heading,
                presentation_class,
                content,
                explanation,
                created_at=request.snapshot.created_at,
            )
            sections.append(section)
            for kind, value, role in specs:
                reference_specs.append((section.section_id, kind, value, role))
            order += 1

        if finding_payloads:
            add_section(
                "FINDINGS",
                "Key findings",
                ANALYTICAL_CONTEXT,
                {"findings": list(finding_payloads)},
                "Persisted operational findings are presented without changing their importance, confidence or evidence state.",
                finding_refs,
            )
        if alert_payloads:
            add_section(
                "ALERTS",
                "Strategic alerts",
                ANALYTICAL_CONTEXT,
                {"alerts": list(alert_payloads)},
                "Persisted alert lifecycle and priority are presentation inputs only and do not modify evidence confidence.",
                alert_refs,
            )
        if coverage_payloads:
            add_section(
                "COVERAGE",
                "Coverage",
                COVERAGE_METADATA,
                {"coverage_reports": list(coverage_payloads)},
                "Coverage metadata describes observed scope and gaps and does not create source independence.",
                coverage_refs,
            )
        if graph_payload["nodes"] or graph_payload["edges"]:
            add_section(
                "RELATIONSHIPS",
                "Relationship analysis",
                GRAPH_INFERENCE,
                graph_payload,
                "Graph relationships are analytical inferences and are not independent source evidence.",
                graph_refs,
            )
        if forecast_payloads:
            add_section(
                "FORECAST",
                "Forecast",
                FORECAST_SCENARIO,
                {"forecasts": list(forecast_payloads)},
                "Forecast probabilities and scenario confidence are analytical outputs and are not evidence confidence.",
                forecast_refs,
            )
        if assumptions:
            specs = tuple((ANALYST_ASSUMPTION, value, "ASSUMPTION") for value in assumptions)
            add_section(
                "ASSUMPTIONS",
                "Assumptions",
                ANALYST_ASSUMPTION,
                {"assumptions": list(assumptions)},
                "Analyst assumptions are explicit analytical inputs and are not source evidence.",
                specs,
            )
        if source_refs:
            add_section(
                "SOURCES",
                "Sources and evidence",
                ANALYTICAL_CONTEXT,
                {
                    "references": [
                        {"reference_kind": kind, "reference_value": value}
                        for kind, value in source_refs
                    ]
                },
                "Source and raw-item references preserve report provenance without altering verification state.",
                tuple((kind, value, "PROVENANCE") for kind, value in source_refs),
            )

        if not sections:
            raise ValueError("report assembly requires at least one validated input")

        references = tuple(
            ReportReference.create(
                request.snapshot.report_id,
                kind,
                value,
                role,
                section_id=section_id,
                created_at=request.snapshot.created_at,
            )
            for section_id, kind, value, role in reference_specs
        )
        bundle = ReportBundle(request.snapshot, tuple(sections), references)
        return self.repository.save_bundle(bundle) if persist else bundle


__all__ = ["ReportAssemblyRequest", "ReportAssembler"]
