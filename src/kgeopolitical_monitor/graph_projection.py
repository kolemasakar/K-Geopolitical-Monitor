"""M11.2 deterministic actor, event and traceability projection helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

from .advanced_graph import GraphNode, SQLiteAdvancedGraphRepository
from .operational_monitoring import _normalize_time


BASELINE_ACTOR_TYPES = (
    "COUNTRY",
    "GOVERNMENT",
    "ORGANIZATION",
    "PERSON",
)


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _same_project_database(
    database_path: str | Path,
    repository: SQLiteAdvancedGraphRepository,
) -> Path:
    requested = Path(database_path).resolve()
    graph_db = repository.database_path.resolve()
    if requested != graph_db:
        raise ValueError("projection database must match the project-local graph database")
    return requested


@dataclass(frozen=True)
class CanonicalActorReference:
    """Explicit reference to an actor owned by an upstream canonical context.

    M11.2 deliberately does not create a second actor Source of Truth. The caller
    supplies the canonical actor reference and the graph stores only its projection.
    """

    actor_id: str
    name: str
    actor_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        actor_id = _nonempty(self.actor_id, "actor_id")
        name = _nonempty(self.name, "name")
        actor_type = _nonempty(self.actor_type, "actor_type").upper()
        json.dumps(self.metadata, sort_keys=True)
        object.__setattr__(self, "actor_id", actor_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "actor_type", actor_type)


def project_actor_references(
    actors: Iterable[CanonicalActorReference],
    repository: SQLiteAdvancedGraphRepository,
    *,
    observed_at: datetime,
) -> tuple[GraphNode, ...]:
    """Project explicit canonical actor references into durable graph nodes."""

    current = _normalize_time(observed_at)
    unique: dict[str, CanonicalActorReference] = {}
    for actor in actors:
        previous = unique.get(actor.actor_id)
        if previous is not None and previous != actor:
            raise ValueError(f"conflicting canonical actor reference: {actor.actor_id}")
        unique[actor.actor_id] = actor

    projected: list[GraphNode] = []
    for actor_id in sorted(unique):
        actor = unique[actor_id]
        attributes = dict(actor.metadata)
        attributes["actor_type"] = actor.actor_type
        node = GraphNode.from_canonical(
            "ACTOR",
            actor.actor_id,
            "ACTOR",
            actor.name,
            attributes=attributes,
            created_at=current,
            updated_at=current,
        )
        repository.save_node(node)
        projected.append(node)
    return tuple(projected)


def project_canonical_events(
    database_path: str | Path,
    repository: SQLiteAdvancedGraphRepository,
    *,
    observed_at: datetime,
    event_ids: Iterable[str] | None = None,
) -> tuple[GraphNode, ...]:
    """Read canonical events and project them without mutating event truth."""

    db = _same_project_database(database_path, repository)
    current = _normalize_time(observed_at)
    requested_ids: tuple[str, ...] | None = None

    query = "SELECT id, title, status, importance FROM events"
    params: tuple[object, ...] = ()
    if event_ids is not None:
        requested_ids = tuple(sorted({_nonempty(value, "event_id") for value in event_ids}))
        if not requested_ids:
            return ()
        placeholders = ",".join("?" for _ in requested_ids)
        query += f" WHERE id IN ({placeholders})"
        params = requested_ids
    query += " ORDER BY id"

    with sqlite3.connect(db) as connection:
        rows = connection.execute(query, params).fetchall()

    if requested_ids is not None:
        found = {row[0] for row in rows}
        missing = [event_id for event_id in requested_ids if event_id not in found]
        if missing:
            raise ValueError(f"canonical event does not exist: {missing[0]}")

    projected: list[GraphNode] = []
    for event_id, title, status, importance in rows:
        node = GraphNode.from_canonical(
            "EVENT",
            str(event_id),
            "EVENT",
            str(title),
            attributes={
                "status": status,
                "importance": importance,
            },
            created_at=current,
            updated_at=current,
        )
        repository.save_node(node)
        projected.append(node)
    return tuple(projected)


def project_live_analysis_claim_references(
    database_path: str | Path,
    repository: SQLiteAdvancedGraphRepository,
    *,
    analysis_run_id: str,
    observed_at: datetime,
) -> tuple[GraphNode, ...]:
    """Project M8 claims for one explicit analysis run only."""

    db = _same_project_database(database_path, repository)
    run_id = _nonempty(analysis_run_id, "analysis_run_id")
    current = _normalize_time(observed_at)

    with sqlite3.connect(db) as connection:
        run = connection.execute(
            "SELECT watch_id FROM live_analysis_runs WHERE analysis_run_id = ?",
            (run_id,),
        ).fetchone()
        if run is None:
            raise ValueError("live analysis run does not exist")
        watch_id = str(run[0])
        rows = connection.execute(
            """
            SELECT claim_id, title, verification_status, confidence, importance,
                   independent_origin_count, source_class_count
            FROM live_analysis_claims
            WHERE analysis_run_id = ?
            ORDER BY claim_id
            """,
            (run_id,),
        ).fetchall()

    projected: list[GraphNode] = []
    for row in rows:
        node = GraphNode.from_canonical(
            "M8_CLAIM",
            str(row[0]),
            "CLAIM",
            str(row[1]),
            attributes={
                "analysis_run_id": run_id,
                "watch_id": watch_id,
                "verification_status": row[2],
                "confidence": float(row[3]),
                "importance": float(row[4]),
                "independent_origin_count": int(row[5]),
                "source_class_count": int(row[6]),
            },
            created_at=current,
            updated_at=current,
        )
        repository.save_node(node)
        projected.append(node)
    return tuple(projected)


def project_operational_finding_references(
    database_path: str | Path,
    repository: SQLiteAdvancedGraphRepository,
    *,
    finding_ids: Iterable[str],
    observed_at: datetime,
) -> tuple[GraphNode, ...]:
    """Project only explicitly requested operational finding references."""

    db = _same_project_database(database_path, repository)
    requested_ids = tuple(sorted({_nonempty(value, "finding_id") for value in finding_ids}))
    if not requested_ids:
        return ()
    current = _normalize_time(observed_at)
    placeholders = ",".join("?" for _ in requested_ids)

    with sqlite3.connect(db) as connection:
        rows = connection.execute(
            f"""
            SELECT finding_id, run_id, watch_id, title, summary, importance,
                   confidence, evidence_refs, explanation
            FROM operational_findings
            WHERE finding_id IN ({placeholders})
            ORDER BY finding_id
            """,
            requested_ids,
        ).fetchall()

    found = {row[0] for row in rows}
    missing = [finding_id for finding_id in requested_ids if finding_id not in found]
    if missing:
        raise ValueError(f"operational finding does not exist: {missing[0]}")

    projected: list[GraphNode] = []
    for row in rows:
        node = GraphNode.from_canonical(
            "OPERATIONAL_FINDING",
            str(row[0]),
            "FINDING",
            str(row[3]),
            attributes={
                "run_id": row[1],
                "watch_id": row[2],
                "summary": row[4],
                "importance": float(row[5]),
                "confidence": float(row[6]),
                "evidence_refs": json.loads(row[7]),
                "explanation": row[8],
            },
            created_at=current,
            updated_at=current,
        )
        repository.save_node(node)
        projected.append(node)
    return tuple(projected)
