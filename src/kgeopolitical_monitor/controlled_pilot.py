"""Controlled project-local pilot monitoring for M6."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import re
import sqlite3
from typing import Iterable

from .monitoring_cycle import CycleExecution
from .operational_monitoring import COMPLETED, FAILED, MonitoringWatch, OperationalMonitoringRuntime, _normalize_time
from .operational_output import FindingDraft, OperationalFinding, OperationalOutputStore


APPROVED_SOURCE_CLASSES = (
    "Official sources",
    "International media",
    "Regional media",
    "Social platforms",
    "OSINT",
    "Structured data",
    "User-provided information",
)


@dataclass(frozen=True)
class PilotSourceItem:
    item_id: str
    source_id: str
    source_name: str
    source_class: str
    title: str
    content: str
    collected_at: datetime
    importance: float
    confidence: float
    reliability: str = "pilot"

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.item_id, "item_id"),
            (self.source_id, "source_id"),
            (self.source_name, "source_name"),
            (self.title, "title"),
            (self.content, "content"),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.source_class not in APPROVED_SOURCE_CLASSES:
            raise ValueError(f"unsupported source_class: {self.source_class}")
        _normalize_time(self.collected_at)
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0 and 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class PilotCoverageReport:
    run_id: str
    watch_id: str
    examined_count: int
    matched_count: int
    source_classes: tuple[str, ...]
    coverage_confidence: float
    gaps: tuple[str, ...]
    created_at: datetime


class ProjectLocalJsonlSourceAdapter:
    def __init__(self, project_root: str | Path, source_path: str | Path):
        self.project_root = Path(project_root).resolve()
        self.source_root = (self.project_root / "data" / "pilot_sources").resolve()

        raw = Path(source_path)
        candidate = raw if raw.is_absolute() else self.project_root / raw
        candidate = candidate.resolve()

        try:
            candidate.relative_to(self.source_root)
        except ValueError as exc:
            raise ValueError(
                "Controlled pilot source must remain inside data/pilot_sources"
            ) from exc

        if candidate == self.source_root:
            raise ValueError("Controlled pilot source path must identify a file")
        self.source_path = candidate

    def load(self) -> list[PilotSourceItem]:
        if not self.source_path.exists():
            raise FileNotFoundError(f"pilot source file not found: {self.source_path}")

        items: list[PilotSourceItem] = []
        seen_ids: set[str] = set()
        for line_number, raw_line in enumerate(
            self.source_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                item = PilotSourceItem(
                    item_id=str(payload["item_id"]),
                    source_id=str(payload["source_id"]),
                    source_name=str(payload["source_name"]),
                    source_class=str(payload["source_class"]),
                    title=str(payload["title"]),
                    content=str(payload["content"]),
                    collected_at=datetime.fromisoformat(str(payload["collected_at"])),
                    importance=float(payload["importance"]),
                    confidence=float(payload["confidence"]),
                    reliability=str(payload.get("reliability", "pilot")),
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid pilot source item at line {line_number}") from exc
            if item.item_id in seen_ids:
                raise ValueError(f"duplicate pilot item_id: {item.item_id}")
            seen_ids.add(item.item_id)
            items.append(item)

        return sorted(items, key=lambda item: item.item_id)


class PilotIngestionStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path

    def persist(self, items: Iterable[PilotSourceItem]) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            for item in items:
                connection.execute(
                    """
                    INSERT INTO sources(id, name, source_class, reliability)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        source_class = excluded.source_class,
                        reliability = excluded.reliability
                    """,
                    (
                        item.source_id,
                        item.source_name,
                        item.source_class,
                        item.reliability,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO raw_items(id, source_id, title, content, collected_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                    """,
                    (
                        item.item_id,
                        item.source_id,
                        item.title,
                        item.content,
                        _normalize_time(item.collected_at).isoformat(),
                    ),
                )


class PilotCoverageStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path

    def save(self, report: PilotCoverageReport) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO pilot_coverage_reports(
                    run_id, watch_id, examined_count, matched_count,
                    source_classes, coverage_confidence, gaps, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.run_id,
                    report.watch_id,
                    report.examined_count,
                    report.matched_count,
                    json.dumps(report.source_classes),
                    report.coverage_confidence,
                    json.dumps(report.gaps),
                    _normalize_time(report.created_at).isoformat(),
                ),
            )

    def get(self, run_id: str) -> PilotCoverageReport | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT run_id, watch_id, examined_count, matched_count,
                       source_classes, coverage_confidence, gaps, created_at
                FROM pilot_coverage_reports
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            return None
        return PilotCoverageReport(
            run_id=row[0],
            watch_id=row[1],
            examined_count=int(row[2]),
            matched_count=int(row[3]),
            source_classes=tuple(json.loads(row[4])),
            coverage_confidence=float(row[5]),
            gaps=tuple(json.loads(row[6])),
            created_at=datetime.fromisoformat(row[7]),
        )


def _matches_watch(item: PilotSourceItem, watch: MonitoringWatch) -> bool:
    terms = [term for term in re.split(r"\s+", watch.query.lower().strip()) if term]
    searchable = f"{item.title}\n{item.content}".lower()
    return bool(terms) and all(term in searchable for term in terms)


def _coverage_report(
    *,
    run_id: str,
    watch_id: str,
    items: list[PilotSourceItem],
    matched_count: int,
    required_source_classes: tuple[str, ...],
    created_at: datetime,
) -> PilotCoverageReport:
    observed = tuple(sorted({item.source_class for item in items}))
    missing = tuple(sorted(set(required_source_classes) - set(observed)))
    confidence = (
        (len(required_source_classes) - len(missing)) / len(required_source_classes)
        if required_source_classes
        else 1.0
    )
    return PilotCoverageReport(
        run_id=run_id,
        watch_id=watch_id,
        examined_count=len(items),
        matched_count=matched_count,
        source_classes=observed,
        coverage_confidence=confidence,
        gaps=missing,
        created_at=_normalize_time(created_at),
    )


class ControlledPilotRunner:
    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        adapter: ProjectLocalJsonlSourceAdapter,
        *,
        required_source_classes: tuple[str, ...],
    ):
        unsupported = set(required_source_classes) - set(APPROVED_SOURCE_CLASSES)
        if unsupported:
            raise ValueError(f"unsupported required source classes: {sorted(unsupported)}")
        if not required_source_classes:
            raise ValueError("controlled pilot requires at least one source class")

        self.runtime = runtime
        self.adapter = adapter
        self.required_source_classes = tuple(dict.fromkeys(required_source_classes))
        self.ingestion = PilotIngestionStore(runtime.database_path)
        self.output = OperationalOutputStore(runtime.database_path)
        self.coverage = PilotCoverageStore(runtime.database_path)

    def execute_due(self, now: datetime) -> list[CycleExecution]:
        current = _normalize_time(now)
        executions: list[CycleExecution] = []

        for watch in self.runtime.due_watches(current):
            run = self.runtime.start_run(watch.watch_id, started_at=current)
            try:
                items = self.adapter.load()
                self.ingestion.persist(items)
                matched = [item for item in items if _matches_watch(item, watch)]
                drafts = [
                    FindingDraft(
                        title=item.title,
                        summary=item.content,
                        importance=item.importance,
                        confidence=item.confidence,
                        evidence_refs=(
                            f"raw_item:{item.item_id}",
                            f"source:{item.source_id}",
                        ),
                        explanation=(
                            f"Controlled pilot match for watch {watch.watch_id}; "
                            f"source={item.source_name}; class={item.source_class}."
                        ),
                    )
                    for item in matched
                ]
                findings = self.output.save_findings(
                    run.run_id,
                    watch.watch_id,
                    drafts,
                    created_at=current,
                )
                self.coverage.save(
                    _coverage_report(
                        run_id=run.run_id,
                        watch_id=watch.watch_id,
                        items=items,
                        matched_count=len(matched),
                        required_source_classes=self.required_source_classes,
                        created_at=current,
                    )
                )
                self.runtime.complete_run(
                    run.run_id,
                    result_count=len(findings),
                    completed_at=current,
                )
                executions.append(
                    CycleExecution(
                        watch_id=watch.watch_id,
                        run_id=run.run_id,
                        status=COMPLETED,
                        result_count=len(findings),
                        retry_count=run.retry_count,
                    )
                )
            except Exception as exc:
                error = str(exc).strip() or exc.__class__.__name__
                self.runtime.fail_run(run.run_id, error, completed_at=current)
                executions.append(
                    CycleExecution(
                        watch_id=watch.watch_id,
                        run_id=run.run_id,
                        status=FAILED,
                        result_count=0,
                        retry_count=run.retry_count,
                        error=error,
                    )
                )

        return executions

    def ranked_findings(
        self,
        *,
        watch_id: str | None = None,
        run_id: str | None = None,
        limit: int = 10,
    ) -> list[OperationalFinding]:
        return self.output.ranked_findings(
            watch_id=watch_id,
            run_id=run_id,
            limit=limit,
        )
