"""M13.1 canonical immutable project-local reporting contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

from .database import initialize_database
from .operational_monitoring import _normalize_time


STRATEGIC_ALERT = "STRATEGIC_ALERT"
GLOBAL_GEOPOLITICAL_BRIEF = "GLOBAL_GEOPOLITICAL_BRIEF"
REGIONAL_COUNTRY_BRIEF = "REGIONAL_COUNTRY_BRIEF"
STORYLINE_REPORT = "STORYLINE_REPORT"
EVENT_DOSSIER = "EVENT_DOSSIER"
FORECAST_REPORT = "FORECAST_REPORT"
STRATEGIC_OUTLOOK = "STRATEGIC_OUTLOOK"

REPORT_TYPES = {
    STRATEGIC_ALERT,
    GLOBAL_GEOPOLITICAL_BRIEF,
    REGIONAL_COUNTRY_BRIEF,
    STORYLINE_REPORT,
    EVENT_DOSSIER,
    FORECAST_REPORT,
    STRATEGIC_OUTLOOK,
}

OBSERVED_FACT = "OBSERVED_FACT"
VERIFICATION_STATE = "VERIFICATION_STATE"
ANALYTICAL_CONTEXT = "ANALYTICAL_CONTEXT"
GRAPH_INFERENCE = "GRAPH_INFERENCE"
FORECAST_SCENARIO = "FORECAST_SCENARIO"
ANALYST_ASSUMPTION = "ANALYST_ASSUMPTION"
COVERAGE_METADATA = "COVERAGE_METADATA"

PRESENTATION_CLASSES = {
    OBSERVED_FACT,
    VERIFICATION_STATE,
    ANALYTICAL_CONTEXT,
    GRAPH_INFERENCE,
    FORECAST_SCENARIO,
    ANALYST_ASSUMPTION,
    COVERAGE_METADATA,
}

SOURCE = "SOURCE"
RAW_ITEM = "RAW_ITEM"
CLAIM = "CLAIM"
EVENT = "EVENT"
FINDING = "FINDING"
ALERT = "ALERT"
GRAPH_NODE = "GRAPH_NODE"
GRAPH_EDGE = "GRAPH_EDGE"
FORECAST = "FORECAST"
FORECAST_VERSION = "FORECAST_VERSION"
SCENARIO_VERSION = "SCENARIO_VERSION"
REGION = "REGION"
LANGUAGE = "LANGUAGE"
COVERAGE_REPORT = "COVERAGE_REPORT"

REFERENCE_KINDS = {
    SOURCE,
    RAW_ITEM,
    CLAIM,
    EVENT,
    FINDING,
    ALERT,
    GRAPH_NODE,
    GRAPH_EDGE,
    FORECAST,
    FORECAST_VERSION,
    SCENARIO_VERSION,
    REGION,
    LANGUAGE,
    COVERAGE_REPORT,
    ANALYST_ASSUMPTION,
}

_SUBJECT_POLICY: dict[str, set[str] | None] = {
    STRATEGIC_ALERT: {ALERT},
    GLOBAL_GEOPOLITICAL_BRIEF: None,
    REGIONAL_COUNTRY_BRIEF: {REGION},
    STORYLINE_REPORT: None,
    EVENT_DOSSIER: {EVENT},
    FORECAST_REPORT: {FORECAST, FORECAST_VERSION},
    STRATEGIC_OUTLOOK: None,
}

_REFERENCE_TABLES: dict[str, tuple[tuple[str, str], ...]] = {
    SOURCE: (("sources", "id"),),
    RAW_ITEM: (("raw_items", "id"),),
    CLAIM: (("claims", "id"), ("live_analysis_claims", "claim_id")),
    EVENT: (("events", "id"),),
    FINDING: (("operational_findings", "finding_id"),),
    ALERT: (("strategic_alerts", "alert_id"),),
    GRAPH_NODE: (("graph_nodes", "node_id"),),
    GRAPH_EDGE: (("graph_edges", "edge_id"),),
    FORECAST: (("forecasts", "forecast_id"),),
    FORECAST_VERSION: (("forecast_versions", "forecast_version_id"),),
    SCENARIO_VERSION: (("forecast_scenario_versions", "scenario_version_id"),),
    REGION: (("region_catalog", "region_code"),),
    LANGUAGE: (("language_catalog", "language_code"),),
    COVERAGE_REPORT: (
        ("region_language_coverage_reports", "report_id"),
        ("pilot_coverage_reports", "run_id"),
    ),
}


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise ValueError("report content must be JSON serializable") from exc


def _report_type(value: str) -> str:
    normalized = _nonempty(value, "report_type").upper()
    if normalized not in REPORT_TYPES:
        raise ValueError(f"unsupported report type: {normalized}")
    return normalized


def _presentation_class(value: str) -> str:
    normalized = _nonempty(value, "presentation_class").upper()
    if normalized not in PRESENTATION_CLASSES:
        raise ValueError(f"unsupported presentation class: {normalized}")
    return normalized


def _reference_kind(value: str) -> str:
    normalized = _nonempty(value, "reference_kind").upper()
    if normalized not in REFERENCE_KINDS:
        raise ValueError(f"unsupported report reference kind: {normalized}")
    return normalized


def report_id(
    report_type_value: str,
    scope_key: str,
    subject_ref_type: str | None,
    subject_ref_id: str | None,
    as_of: datetime,
) -> str:
    normalized_type = _report_type(report_type_value)
    scope = _nonempty(scope_key, "scope_key")
    timestamp = _normalize_time(as_of)
    subject_type = "" if subject_ref_type is None else _reference_kind(subject_ref_type)
    subject_id = "" if subject_ref_id is None else _nonempty(subject_ref_id, "subject_ref_id")
    return _stable_id(
        "report",
        normalized_type,
        scope,
        subject_type,
        subject_id,
        timestamp.isoformat(),
    )


def section_id(report_id_value: str, order: int, section_type: str, heading: str) -> str:
    if order < 0:
        raise ValueError("section_order must not be negative")
    return _stable_id(
        "report-section",
        _nonempty(report_id_value, "report_id"),
        str(order),
        _nonempty(section_type, "section_type"),
        _nonempty(heading, "heading"),
    )


def reference_id(
    report_id_value: str,
    section_id_value: str | None,
    reference_kind_value: str,
    reference_value: str,
    reference_role: str,
) -> str:
    return _stable_id(
        "report-ref",
        _nonempty(report_id_value, "report_id"),
        section_id_value or "",
        _reference_kind(reference_kind_value),
        _nonempty(reference_value, "reference_value"),
        _nonempty(reference_role, "reference_role").upper(),
    )


@dataclass(frozen=True)
class ReportSnapshot:
    report_id: str
    report_type: str
    scope_key: str
    subject_ref_type: str | None
    subject_ref_id: str | None
    title: str
    summary: str
    as_of: datetime
    created_at: datetime
    generator_version: str

    def __post_init__(self) -> None:
        report_type_value = _report_type(self.report_type)
        scope = _nonempty(self.scope_key, "scope_key")
        title = _nonempty(self.title, "title")
        summary = _nonempty(self.summary, "summary")
        generator = _nonempty(self.generator_version, "generator_version")
        as_of = _normalize_time(self.as_of)
        created_at = _normalize_time(self.created_at)

        policy = _SUBJECT_POLICY[report_type_value]
        subject_type = self.subject_ref_type
        subject_id = self.subject_ref_id
        if policy is None:
            if subject_type is not None or subject_id is not None:
                raise ValueError(f"{report_type_value} uses scope-only subject semantics")
        else:
            if subject_type is None or subject_id is None:
                raise ValueError(f"{report_type_value} requires a canonical subject reference")
            subject_type = _reference_kind(subject_type)
            subject_id = _nonempty(subject_id, "subject_ref_id")
            if subject_type not in policy:
                raise ValueError(f"invalid subject reference type for {report_type_value}: {subject_type}")

        expected = report_id(report_type_value, scope, subject_type, subject_id, as_of)
        if self.report_id != expected:
            raise ValueError("report_id must match deterministic report identity")

        object.__setattr__(self, "report_type", report_type_value)
        object.__setattr__(self, "scope_key", scope)
        object.__setattr__(self, "subject_ref_type", subject_type)
        object.__setattr__(self, "subject_ref_id", subject_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "as_of", as_of)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "generator_version", generator)

    @classmethod
    def create(
        cls,
        report_type: str,
        scope_key: str,
        title: str,
        summary: str,
        as_of: datetime,
        *,
        subject_ref_type: str | None = None,
        subject_ref_id: str | None = None,
        created_at: datetime | None = None,
        generator_version: str = "m13.1",
    ) -> "ReportSnapshot":
        normalized_as_of = _normalize_time(as_of)
        return cls(
            report_id=report_id(report_type, scope_key, subject_ref_type, subject_ref_id, normalized_as_of),
            report_type=report_type,
            scope_key=scope_key,
            subject_ref_type=subject_ref_type,
            subject_ref_id=subject_ref_id,
            title=title,
            summary=summary,
            as_of=normalized_as_of,
            created_at=_normalize_time(created_at or normalized_as_of),
            generator_version=generator_version,
        )


@dataclass(frozen=True)
class ReportSection:
    section_id: str
    report_id: str
    section_order: int
    section_type: str
    heading: str
    presentation_class: str
    content: Any
    explanation: str
    created_at: datetime

    def __post_init__(self) -> None:
        if self.section_order < 0:
            raise ValueError("section_order must not be negative")
        report_id_value = _nonempty(self.report_id, "report_id")
        section_type = _nonempty(self.section_type, "section_type").upper()
        heading = _nonempty(self.heading, "heading")
        presentation = _presentation_class(self.presentation_class)
        explanation = _nonempty(self.explanation, "explanation")
        _canonical_json(self.content)
        created_at = _normalize_time(self.created_at)
        expected = section_id(report_id_value, self.section_order, section_type, heading)
        if self.section_id != expected:
            raise ValueError("section_id must match deterministic report section identity")
        object.__setattr__(self, "report_id", report_id_value)
        object.__setattr__(self, "section_type", section_type)
        object.__setattr__(self, "heading", heading)
        object.__setattr__(self, "presentation_class", presentation)
        object.__setattr__(self, "explanation", explanation)
        object.__setattr__(self, "created_at", created_at)

    @classmethod
    def create(
        cls,
        report_id_value: str,
        section_order: int,
        section_type: str,
        heading: str,
        presentation_class: str,
        content: Any,
        explanation: str,
        *,
        created_at: datetime,
    ) -> "ReportSection":
        normalized_type = _nonempty(section_type, "section_type").upper()
        normalized_heading = _nonempty(heading, "heading")
        return cls(
            section_id=section_id(report_id_value, section_order, normalized_type, normalized_heading),
            report_id=report_id_value,
            section_order=section_order,
            section_type=normalized_type,
            heading=normalized_heading,
            presentation_class=presentation_class,
            content=content,
            explanation=explanation,
            created_at=created_at,
        )


@dataclass(frozen=True)
class ReportReference:
    reference_id: str
    report_id: str
    section_id: str | None
    reference_kind: str
    reference_value: str
    reference_role: str
    created_at: datetime

    def __post_init__(self) -> None:
        report_id_value = _nonempty(self.report_id, "report_id")
        section_id_value = None if self.section_id is None else _nonempty(self.section_id, "section_id")
        kind = _reference_kind(self.reference_kind)
        value = _nonempty(self.reference_value, "reference_value")
        role = _nonempty(self.reference_role, "reference_role").upper()
        created_at = _normalize_time(self.created_at)
        expected = reference_id(report_id_value, section_id_value, kind, value, role)
        if self.reference_id != expected:
            raise ValueError("reference_id must match deterministic report reference identity")
        object.__setattr__(self, "report_id", report_id_value)
        object.__setattr__(self, "section_id", section_id_value)
        object.__setattr__(self, "reference_kind", kind)
        object.__setattr__(self, "reference_value", value)
        object.__setattr__(self, "reference_role", role)
        object.__setattr__(self, "created_at", created_at)

    @classmethod
    def create(
        cls,
        report_id_value: str,
        reference_kind: str,
        reference_value: str,
        reference_role: str,
        *,
        section_id: str | None = None,
        created_at: datetime,
    ) -> "ReportReference":
        return cls(
            reference_id=reference_id(
                report_id_value,
                section_id,
                reference_kind,
                reference_value,
                reference_role,
            ),
            report_id=report_id_value,
            section_id=section_id,
            reference_kind=reference_kind,
            reference_value=reference_value,
            reference_role=reference_role,
            created_at=created_at,
        )


@dataclass(frozen=True)
class ReportBundle:
    snapshot: ReportSnapshot
    sections: tuple[ReportSection, ...] = field(default_factory=tuple)
    references: tuple[ReportReference, ...] = field(default_factory=tuple)


class SQLiteReportRepository:
    """Immutable project-local report snapshot repository."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    @staticmethod
    def _reference_exists(
        connection: sqlite3.Connection,
        kind: str,
        value: str,
    ) -> bool:
        if kind == ANALYST_ASSUMPTION:
            return True
        for table, column in _REFERENCE_TABLES[kind]:
            if connection.execute(
                f"SELECT 1 FROM {table} WHERE {column} = ?",
                (value,),
            ).fetchone() is not None:
                return True
        return False

    def _validate_subject(self, connection: sqlite3.Connection, snapshot: ReportSnapshot) -> None:
        if snapshot.subject_ref_type is None:
            return
        if not self._reference_exists(connection, snapshot.subject_ref_type, snapshot.subject_ref_id or ""):
            raise ValueError(
                f"unknown canonical report subject: {snapshot.subject_ref_type}:{snapshot.subject_ref_id}"
            )

    def _validate_reference(self, connection: sqlite3.Connection, reference: ReportReference) -> None:
        if not self._reference_exists(connection, reference.reference_kind, reference.reference_value):
            raise ValueError(
                f"unknown canonical report reference: {reference.reference_kind}:{reference.reference_value}"
            )

    def save_bundle(self, bundle: ReportBundle) -> ReportBundle:
        snapshot = bundle.snapshot
        sections = tuple(sorted(bundle.sections, key=lambda item: (item.section_order, item.section_id)))
        references = tuple(
            sorted(
                bundle.references,
                key=lambda item: (
                    item.section_id or "",
                    item.reference_kind,
                    item.reference_value,
                    item.reference_role,
                    item.reference_id,
                ),
            )
        )
        if len({item.section_id for item in sections}) != len(sections):
            raise ValueError("duplicate report section identity")
        if len({item.section_order for item in sections}) != len(sections):
            raise ValueError("duplicate report section order")
        if any(item.report_id != snapshot.report_id for item in sections):
            raise ValueError("report section belongs to a different report")
        section_ids = {item.section_id for item in sections}
        if len({item.reference_id for item in references}) != len(references):
            raise ValueError("duplicate report reference identity")
        for reference in references:
            if reference.report_id != snapshot.report_id:
                raise ValueError("report reference belongs to a different report")
            if reference.section_id is not None and reference.section_id not in section_ids:
                raise ValueError("report reference section is not part of the supplied report")

        normalized = ReportBundle(snapshot, sections, references)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            self._validate_subject(connection, snapshot)
            for reference in references:
                self._validate_reference(connection, reference)

            existing = connection.execute(
                "SELECT 1 FROM report_snapshots WHERE report_id = ?",
                (snapshot.report_id,),
            ).fetchone()
            if existing is not None:
                persisted = self.get_bundle(snapshot.report_id)
                if persisted != normalized:
                    raise ValueError("report snapshot is immutable")
                return normalized

            connection.execute(
                """
                INSERT INTO report_snapshots(
                    report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
                    title, summary, as_of, created_at, generator_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.report_id,
                    snapshot.report_type,
                    snapshot.scope_key,
                    snapshot.subject_ref_type,
                    snapshot.subject_ref_id,
                    snapshot.title,
                    snapshot.summary,
                    snapshot.as_of.isoformat(),
                    snapshot.created_at.isoformat(),
                    snapshot.generator_version,
                ),
            )
            connection.executemany(
                """
                INSERT INTO report_sections(
                    section_id, report_id, section_order, section_type, heading,
                    presentation_class, content_json, explanation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.section_id,
                        item.report_id,
                        item.section_order,
                        item.section_type,
                        item.heading,
                        item.presentation_class,
                        _canonical_json(item.content),
                        item.explanation,
                        item.created_at.isoformat(),
                    )
                    for item in sections
                ],
            )
            connection.executemany(
                """
                INSERT INTO report_references(
                    reference_id, report_id, section_id, reference_kind,
                    reference_value, reference_role, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.reference_id,
                        item.report_id,
                        item.section_id,
                        item.reference_kind,
                        item.reference_value,
                        item.reference_role,
                        item.created_at.isoformat(),
                    )
                    for item in references
                ],
            )
        return normalized

    def get_bundle(self, report_id_value: str) -> ReportBundle | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
                       title, summary, as_of, created_at, generator_version
                FROM report_snapshots WHERE report_id = ?
                """,
                (report_id_value,),
            ).fetchone()
            if row is None:
                return None
            section_rows = connection.execute(
                """
                SELECT section_id, report_id, section_order, section_type, heading,
                       presentation_class, content_json, explanation, created_at
                FROM report_sections WHERE report_id = ?
                ORDER BY section_order, section_id
                """,
                (report_id_value,),
            ).fetchall()
            reference_rows = connection.execute(
                """
                SELECT reference_id, report_id, section_id, reference_kind,
                       reference_value, reference_role, created_at
                FROM report_references WHERE report_id = ?
                ORDER BY COALESCE(section_id, ''), reference_kind, reference_value,
                         reference_role, reference_id
                """,
                (report_id_value,),
            ).fetchall()

        snapshot = ReportSnapshot(
            report_id=row[0],
            report_type=row[1],
            scope_key=row[2],
            subject_ref_type=row[3],
            subject_ref_id=row[4],
            title=row[5],
            summary=row[6],
            as_of=datetime.fromisoformat(row[7]),
            created_at=datetime.fromisoformat(row[8]),
            generator_version=row[9],
        )
        sections = tuple(
            ReportSection(
                section_id=item[0],
                report_id=item[1],
                section_order=int(item[2]),
                section_type=item[3],
                heading=item[4],
                presentation_class=item[5],
                content=json.loads(item[6]),
                explanation=item[7],
                created_at=datetime.fromisoformat(item[8]),
            )
            for item in section_rows
        )
        references = tuple(
            ReportReference(
                reference_id=item[0],
                report_id=item[1],
                section_id=item[2],
                reference_kind=item[3],
                reference_value=item[4],
                reference_role=item[5],
                created_at=datetime.fromisoformat(item[6]),
            )
            for item in reference_rows
        )
        return ReportBundle(snapshot, sections, references)


__all__ = [
    "STRATEGIC_ALERT",
    "GLOBAL_GEOPOLITICAL_BRIEF",
    "REGIONAL_COUNTRY_BRIEF",
    "STORYLINE_REPORT",
    "EVENT_DOSSIER",
    "FORECAST_REPORT",
    "STRATEGIC_OUTLOOK",
    "REPORT_TYPES",
    "OBSERVED_FACT",
    "VERIFICATION_STATE",
    "ANALYTICAL_CONTEXT",
    "GRAPH_INFERENCE",
    "FORECAST_SCENARIO",
    "ANALYST_ASSUMPTION",
    "COVERAGE_METADATA",
    "PRESENTATION_CLASSES",
    "REFERENCE_KINDS",
    "SOURCE",
    "RAW_ITEM",
    "CLAIM",
    "EVENT",
    "FINDING",
    "ALERT",
    "GRAPH_NODE",
    "GRAPH_EDGE",
    "FORECAST",
    "FORECAST_VERSION",
    "SCENARIO_VERSION",
    "REGION",
    "LANGUAGE",
    "COVERAGE_REPORT",
    "ReportSnapshot",
    "ReportSection",
    "ReportReference",
    "ReportBundle",
    "SQLiteReportRepository",
    "report_id",
    "section_id",
    "reference_id",
]
