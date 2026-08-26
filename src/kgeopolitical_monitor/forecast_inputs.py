"""M12.2 provenance-bound immutable forecast input bindings."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

from .advanced_forecasting import ForecastVersion
from .database import initialize_database
from .operational_monitoring import _normalize_time, utc_now


SOURCE_EVIDENCE = "SOURCE_EVIDENCE"
CANONICAL_EVENT = "CANONICAL_EVENT"
GRAPH_RELATIONSHIP = "GRAPH_RELATIONSHIP"
OPERATIONAL_FINDING = "OPERATIONAL_FINDING"
ANALYST_ASSUMPTION = "ANALYST_ASSUMPTION"

FORECAST_INPUT_KINDS = {
    SOURCE_EVIDENCE,
    CANONICAL_EVENT,
    GRAPH_RELATIONSHIP,
    OPERATIONAL_FINDING,
    ANALYST_ASSUMPTION,
}

_DURABLE_REFERENCE_TABLES = {
    SOURCE_EVIDENCE: ("raw_items", "id"),
    CANONICAL_EVENT: ("events", "id"),
    GRAPH_RELATIONSHIP: ("graph_edges", "edge_id"),
    OPERATIONAL_FINDING: ("operational_findings", "finding_id"),
}


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def _json_ready(value: Any, field_name: str) -> Any:
    try:
        json.dumps(value, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON serializable") from exc
    return value


@dataclass(frozen=True)
class ForecastInputRef:
    input_id: str
    forecast_version_id: str
    input_kind: str
    reference_id: str | None = None
    statement: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        version_id = _nonempty(self.forecast_version_id, "forecast_version_id")
        kind = _nonempty(self.input_kind, "input_kind").upper()
        if kind not in FORECAST_INPUT_KINDS:
            raise ValueError(f"unsupported forecast input kind: {kind}")
        _json_ready(self.metadata, "metadata")
        created = _normalize_time(self.created_at)

        if kind == ANALYST_ASSUMPTION:
            if self.reference_id is not None:
                raise ValueError("ANALYST_ASSUMPTION must not use reference_id")
            statement = _nonempty(self.statement or "", "statement")
            identity_value = statement
            object.__setattr__(self, "statement", statement)
        else:
            reference_id = _nonempty(self.reference_id or "", "reference_id")
            if self.statement is not None:
                raise ValueError("durable forecast input must not use statement")
            identity_value = reference_id
            object.__setattr__(self, "reference_id", reference_id)

        expected = _stable_id("fin", version_id, kind, identity_value)
        if self.input_id != expected:
            raise ValueError("input_id must match deterministic forecast input identity")

        object.__setattr__(self, "forecast_version_id", version_id)
        object.__setattr__(self, "input_kind", kind)
        object.__setattr__(self, "created_at", created)

    @classmethod
    def durable(
        cls,
        forecast_version_id: str,
        input_kind: str,
        reference_id: str,
        *,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> "ForecastInputRef":
        kind = _nonempty(input_kind, "input_kind").upper()
        if kind == ANALYST_ASSUMPTION:
            raise ValueError("use assumption() for ANALYST_ASSUMPTION")
        ref = _nonempty(reference_id, "reference_id")
        return cls(
            input_id=_stable_id("fin", forecast_version_id, kind, ref),
            forecast_version_id=forecast_version_id,
            input_kind=kind,
            reference_id=ref,
            metadata=dict(metadata or {}),
            created_at=_normalize_time(created_at or utc_now()),
        )

    @classmethod
    def assumption(
        cls,
        forecast_version_id: str,
        statement: str,
        *,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> "ForecastInputRef":
        text = _nonempty(statement, "statement")
        return cls(
            input_id=_stable_id("fin", forecast_version_id, ANALYST_ASSUMPTION, text),
            forecast_version_id=forecast_version_id,
            input_kind=ANALYST_ASSUMPTION,
            statement=text,
            metadata=dict(metadata or {}),
            created_at=_normalize_time(created_at or utc_now()),
        )


def _sort_inputs(inputs: Iterable[ForecastInputRef]) -> tuple[ForecastInputRef, ...]:
    items = tuple(inputs)
    if not items:
        raise ValueError("forecast version requires at least one typed input")
    version_ids = {item.forecast_version_id for item in items}
    if len(version_ids) != 1:
        raise ValueError("all forecast inputs must belong to one forecast version")
    if len({item.input_id for item in items}) != len(items):
        raise ValueError("duplicate forecast input identity")
    return tuple(
        sorted(
            items,
            key=lambda item: (
                item.input_kind,
                item.reference_id or item.statement or "",
                item.input_id,
            ),
        )
    )


def build_input_snapshot(
    inputs: Iterable[ForecastInputRef],
    *,
    constraints: Iterable[str] = (),
) -> dict[str, Any]:
    items = _sort_inputs(inputs)
    normalized_constraints = tuple(sorted(_nonempty(value, "constraint") for value in constraints))
    return {
        "inputs": [
            {
                "input_kind": item.input_kind,
                "reference_id": item.reference_id,
                "statement": item.statement,
                "metadata": item.metadata,
            }
            for item in items
        ],
        "constraints": list(normalized_constraints),
    }


def provenance_tokens(inputs: Iterable[ForecastInputRef]) -> tuple[str, ...]:
    items = _sort_inputs(inputs)
    tokens: list[str] = []
    for item in items:
        identity = item.reference_id
        if item.input_kind == ANALYST_ASSUMPTION:
            identity = _stable_id("assumption", item.statement or "")
        tokens.append(f"{item.input_kind}:{identity}")
    return tuple(tokens)


def create_forecast_version_with_inputs(
    forecast_id: str,
    version_number: int,
    *,
    inputs: Iterable[ForecastInputRef],
    constraints: Iterable[str] = (),
    change_reason: str,
    created_at: datetime | None = None,
) -> ForecastVersion:
    items = _sort_inputs(inputs)
    assumptions = tuple(
        item.statement or ""
        for item in items
        if item.input_kind == ANALYST_ASSUMPTION
    )
    return ForecastVersion.create(
        forecast_id,
        version_number,
        input_snapshot=build_input_snapshot(items, constraints=constraints),
        provenance_refs=provenance_tokens(items),
        assumptions=assumptions,
        change_reason=change_reason,
        created_at=created_at,
    )


class SQLiteForecastInputRepository:
    """Validate and bind typed provenance to one immutable forecast version."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    def _validate_reference(
        self,
        connection: sqlite3.Connection,
        item: ForecastInputRef,
    ) -> None:
        if item.input_kind == ANALYST_ASSUMPTION:
            return
        table, column = _DURABLE_REFERENCE_TABLES[item.input_kind]
        row = connection.execute(
            f"SELECT 1 FROM {table} WHERE {column} = ?",
            (item.reference_id,),
        ).fetchone()
        if row is None:
            raise ValueError(
                f"unknown canonical reference for {item.input_kind}: {item.reference_id}"
            )

    def bind(
        self,
        version: ForecastVersion,
        inputs: Iterable[ForecastInputRef],
        *,
        constraints: Iterable[str] = (),
    ) -> tuple[ForecastInputRef, ...]:
        items = _sort_inputs(inputs)
        if any(item.forecast_version_id != version.forecast_version_id for item in items):
            raise ValueError("forecast input does not belong to supplied forecast version")

        snapshot = build_input_snapshot(items, constraints=constraints)
        tokens = provenance_tokens(items)
        assumptions = tuple(
            item.statement or ""
            for item in items
            if item.input_kind == ANALYST_ASSUMPTION
        )

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            row = connection.execute(
                """
                SELECT input_snapshot_json, provenance_refs_json, assumptions_json
                FROM forecast_versions
                WHERE forecast_version_id = ?
                """,
                (version.forecast_version_id,),
            ).fetchone()
            if row is None:
                raise ValueError("forecast version must be persisted before binding inputs")

            persisted_snapshot = json.loads(row[0])
            persisted_tokens = tuple(json.loads(row[1]))
            persisted_assumptions = tuple(json.loads(row[2]))
            if persisted_snapshot != snapshot:
                raise ValueError("typed forecast inputs do not match immutable input_snapshot")
            if persisted_tokens != tokens:
                raise ValueError("typed forecast inputs do not match immutable provenance_refs")
            if persisted_assumptions != assumptions:
                raise ValueError("typed forecast assumptions do not match immutable assumptions")

            for item in items:
                self._validate_reference(connection, item)

            payloads = tuple(
                (
                    item.input_id,
                    item.forecast_version_id,
                    item.input_kind,
                    item.reference_id,
                    item.statement,
                    json.dumps(item.metadata, sort_keys=True),
                    item.created_at.isoformat(),
                )
                for item in items
            )
            existing = connection.execute(
                """
                SELECT input_id, forecast_version_id, input_kind, reference_id,
                       statement, metadata_json, created_at
                FROM forecast_version_inputs
                WHERE forecast_version_id = ?
                ORDER BY input_id
                """,
                (version.forecast_version_id,),
            ).fetchall()
            if existing:
                if tuple(sorted(tuple(row) for row in existing)) != tuple(sorted(payloads)):
                    raise ValueError("forecast version input binding is immutable")
                return items

            connection.executemany(
                """
                INSERT INTO forecast_version_inputs(
                    input_id, forecast_version_id, input_kind, reference_id,
                    statement, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                payloads,
            )
        return items

    def list_inputs(self, forecast_version_id: str) -> tuple[ForecastInputRef, ...]:
        version_id = _nonempty(forecast_version_id, "forecast_version_id")
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT input_id, forecast_version_id, input_kind, reference_id,
                       statement, metadata_json, created_at
                FROM forecast_version_inputs
                WHERE forecast_version_id = ?
                ORDER BY input_kind, COALESCE(reference_id, statement), input_id
                """,
                (version_id,),
            ).fetchall()
        return tuple(
            ForecastInputRef(
                input_id=row[0],
                forecast_version_id=row[1],
                input_kind=row[2],
                reference_id=row[3],
                statement=row[4],
                metadata=json.loads(row[5]),
                created_at=datetime.fromisoformat(row[6]),
            )
            for row in rows
        )
