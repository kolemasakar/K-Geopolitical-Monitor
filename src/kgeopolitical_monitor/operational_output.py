"""Project-local operational intelligence findings and ranked output."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from .database import initialize_database
from .operational_monitoring import _normalize_time, utc_now


@dataclass(frozen=True)
class FindingDraft:
    title: str
    summary: str
    importance: float
    confidence: float
    evidence_refs: tuple[str, ...]
    explanation: str

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.summary.strip():
            raise ValueError("finding title and summary must not be empty")
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0 and 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.evidence_refs or any(not ref.strip() for ref in self.evidence_refs):
            raise ValueError("operational finding requires traceable evidence references")
        if not self.explanation.strip():
            raise ValueError("operational finding requires an explanation")


@dataclass(frozen=True)
class OperationalFinding:
    finding_id: str
    run_id: str
    watch_id: str
    title: str
    summary: str
    importance: float
    confidence: float
    evidence_refs: tuple[str, ...]
    explanation: str
    created_at: datetime = field(default_factory=utc_now)


class OperationalOutputStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        initialize_database(str(database_path))

    def save_findings(
        self,
        run_id: str,
        watch_id: str,
        drafts: list[FindingDraft],
        *,
        created_at: datetime | None = None,
    ) -> list[OperationalFinding]:
        timestamp = _normalize_time(created_at or utc_now())
        findings = [
            OperationalFinding(
                finding_id=f"finding-{uuid4().hex}",
                run_id=run_id,
                watch_id=watch_id,
                title=draft.title,
                summary=draft.summary,
                importance=draft.importance,
                confidence=draft.confidence,
                evidence_refs=draft.evidence_refs,
                explanation=draft.explanation,
                created_at=timestamp,
            )
            for draft in drafts
        ]

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executemany(
                """
                INSERT INTO operational_findings(
                    finding_id, run_id, watch_id, title, summary, importance,
                    confidence, evidence_refs, explanation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        finding.finding_id,
                        finding.run_id,
                        finding.watch_id,
                        finding.title,
                        finding.summary,
                        finding.importance,
                        finding.confidence,
                        json.dumps(finding.evidence_refs),
                        finding.explanation,
                        _normalize_time(finding.created_at).isoformat(),
                    )
                    for finding in findings
                ],
            )
        return findings

    def ranked_findings(
        self,
        *,
        watch_id: str | None = None,
        run_id: str | None = None,
        limit: int = 10,
    ) -> list[OperationalFinding]:
        if limit <= 0:
            raise ValueError("limit must be positive")

        clauses: list[str] = []
        params: list[object] = []
        if watch_id is not None:
            clauses.append("watch_id = ?")
            params.append(watch_id)
        if run_id is not None:
            clauses.append("run_id = ?")
            params.append(run_id)

        query = (
            "SELECT finding_id, run_id, watch_id, title, summary, importance, "
            "confidence, evidence_refs, explanation, created_at "
            "FROM operational_findings"
        )
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY importance DESC, confidence DESC, finding_id ASC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            OperationalFinding(
                finding_id=row[0],
                run_id=row[1],
                watch_id=row[2],
                title=row[3],
                summary=row[4],
                importance=float(row[5]),
                confidence=float(row[6]),
                evidence_refs=tuple(json.loads(row[7])),
                explanation=row[8],
                created_at=datetime.fromisoformat(row[9]),
            )
            for row in rows
        ]
