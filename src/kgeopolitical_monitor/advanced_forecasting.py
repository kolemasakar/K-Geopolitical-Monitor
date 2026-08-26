"""M12.1 durable versioned advanced forecasting baseline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

from .database import initialize_database
from .forecast_preparation import ForecastHorizon
from .operational_monitoring import _normalize_time, utc_now
from .probabilistic_forecasting import ScenarioType


ACTIVE = "ACTIVE"
RESOLVED = "RESOLVED"
INVALIDATED = "INVALIDATED"
CLOSED = "CLOSED"
FORECAST_STATUSES = {ACTIVE, RESOLVED, INVALIDATED, CLOSED}


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def _horizon_value(value: ForecastHorizon | str) -> str:
    raw = value.value if isinstance(value, ForecastHorizon) else str(value).strip()
    allowed = {item.value for item in ForecastHorizon}
    if raw not in allowed:
        raise ValueError(f"unsupported forecast horizon: {raw}")
    return raw


def _scenario_type_value(value: ScenarioType | str) -> str:
    raw = value.value if isinstance(value, ScenarioType) else str(value).strip().lower()
    allowed = {item.value for item in ScenarioType}
    if raw not in allowed:
        raise ValueError(f"unsupported scenario type: {raw}")
    return raw


def forecast_id(target_key: str, horizon: ForecastHorizon | str, evaluation_deadline: datetime) -> str:
    target = _nonempty(target_key, "target_key")
    deadline = _normalize_time(evaluation_deadline)
    return _stable_id("forecast", target, _horizon_value(horizon), deadline.isoformat())


def forecast_version_id(forecast_id_value: str, version_number: int) -> str:
    if version_number <= 0:
        raise ValueError("version_number must be positive")
    return _stable_id("fver", _nonempty(forecast_id_value, "forecast_id"), str(version_number))


def scenario_version_id(forecast_version_id_value: str, scenario_type: ScenarioType | str, label: str) -> str:
    return _stable_id(
        "sver",
        _nonempty(forecast_version_id_value, "forecast_version_id"),
        _scenario_type_value(scenario_type),
        _nonempty(label, "label"),
    )


def _json_ready(value: Any, field_name: str) -> Any:
    try:
        json.dumps(value, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON serializable") from exc
    return value


def _string_tuple(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    normalized = tuple(_nonempty(value, field_name) for value in values)
    return normalized


@dataclass(frozen=True)
class ForecastRecord:
    forecast_id: str
    target_key: str
    question: str
    horizon: str
    evaluation_deadline: datetime
    status: str = ACTIVE
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        target = _nonempty(self.target_key, "target_key")
        question = _nonempty(self.question, "question")
        horizon = _horizon_value(self.horizon)
        deadline = _normalize_time(self.evaluation_deadline)
        status = _nonempty(self.status, "status").upper()
        if status not in FORECAST_STATUSES:
            raise ValueError(f"unsupported forecast status: {status}")
        created = _normalize_time(self.created_at)
        updated = _normalize_time(self.updated_at)
        if updated < created:
            raise ValueError("updated_at must not precede created_at")
        expected = forecast_id(target, horizon, deadline)
        if self.forecast_id != expected:
            raise ValueError("forecast_id must match deterministic forecast identity")
        object.__setattr__(self, "target_key", target)
        object.__setattr__(self, "question", question)
        object.__setattr__(self, "horizon", horizon)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "evaluation_deadline", deadline)
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "updated_at", updated)

    @classmethod
    def create(
        cls,
        target_key: str,
        question: str,
        horizon: ForecastHorizon | str,
        evaluation_deadline: datetime,
        *,
        status: str = ACTIVE,
        created_at: datetime | None = None,
    ) -> "ForecastRecord":
        created = _normalize_time(created_at or utc_now())
        deadline = _normalize_time(evaluation_deadline)
        return cls(
            forecast_id=forecast_id(target_key, horizon, deadline),
            target_key=target_key,
            question=question,
            horizon=_horizon_value(horizon),
            evaluation_deadline=deadline,
            status=status,
            created_at=created,
            updated_at=created,
        )


@dataclass(frozen=True)
class ForecastVersion:
    forecast_version_id: str
    forecast_id: str
    version_number: int
    input_snapshot: dict[str, Any]
    provenance_refs: tuple[str, ...]
    assumptions: tuple[str, ...]
    change_reason: str
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        fid = _nonempty(self.forecast_id, "forecast_id")
        if self.version_number <= 0:
            raise ValueError("version_number must be positive")
        expected = forecast_version_id(fid, self.version_number)
        if self.forecast_version_id != expected:
            raise ValueError("forecast_version_id must match deterministic version identity")
        _json_ready(self.input_snapshot, "input_snapshot")
        provenance = _string_tuple(self.provenance_refs, "provenance_ref")
        assumptions = _string_tuple(self.assumptions, "assumption")
        reason = _nonempty(self.change_reason, "change_reason")
        created = _normalize_time(self.created_at)
        object.__setattr__(self, "forecast_id", fid)
        object.__setattr__(self, "provenance_refs", provenance)
        object.__setattr__(self, "assumptions", assumptions)
        object.__setattr__(self, "change_reason", reason)
        object.__setattr__(self, "created_at", created)

    @classmethod
    def create(
        cls,
        forecast_id_value: str,
        version_number: int,
        *,
        input_snapshot: dict[str, Any],
        provenance_refs: Iterable[str],
        assumptions: Iterable[str],
        change_reason: str,
        created_at: datetime | None = None,
    ) -> "ForecastVersion":
        return cls(
            forecast_version_id=forecast_version_id(forecast_id_value, version_number),
            forecast_id=forecast_id_value,
            version_number=version_number,
            input_snapshot=dict(input_snapshot),
            provenance_refs=tuple(provenance_refs),
            assumptions=tuple(assumptions),
            change_reason=change_reason,
            created_at=_normalize_time(created_at or utc_now()),
        )


@dataclass(frozen=True)
class ScenarioVersion:
    scenario_version_id: str
    forecast_version_id: str
    scenario_type: str
    label: str
    raw_probability: float
    calibrated_probability: float
    scenario_confidence: float
    drivers: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    triggers: tuple[str, ...] = ()
    inhibitors: tuple[str, ...] = ()
    uncertainty_factors: tuple[str, ...] = ()
    invalidation_signals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        version_id = _nonempty(self.forecast_version_id, "forecast_version_id")
        scenario_type = _scenario_type_value(self.scenario_type)
        label = _nonempty(self.label, "label")
        expected = scenario_version_id(version_id, scenario_type, label)
        if self.scenario_version_id != expected:
            raise ValueError("scenario_version_id must match deterministic scenario identity")
        for field_name in ("raw_probability", "calibrated_probability", "scenario_confidence"):
            value = float(getattr(self, field_name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
            object.__setattr__(self, field_name, value)
        for field_name in (
            "drivers",
            "constraints",
            "triggers",
            "inhibitors",
            "uncertainty_factors",
            "invalidation_signals",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name[:-1] if field_name.endswith("s") else field_name),
            )
        object.__setattr__(self, "forecast_version_id", version_id)
        object.__setattr__(self, "scenario_type", scenario_type)
        object.__setattr__(self, "label", label)

    @classmethod
    def create(
        cls,
        forecast_version_id_value: str,
        scenario_type: ScenarioType | str,
        label: str,
        raw_probability: float,
        calibrated_probability: float,
        scenario_confidence: float,
        *,
        drivers: Iterable[str] = (),
        constraints: Iterable[str] = (),
        triggers: Iterable[str] = (),
        inhibitors: Iterable[str] = (),
        uncertainty_factors: Iterable[str] = (),
        invalidation_signals: Iterable[str] = (),
    ) -> "ScenarioVersion":
        return cls(
            scenario_version_id=scenario_version_id(forecast_version_id_value, scenario_type, label),
            forecast_version_id=forecast_version_id_value,
            scenario_type=_scenario_type_value(scenario_type),
            label=label,
            raw_probability=float(raw_probability),
            calibrated_probability=float(calibrated_probability),
            scenario_confidence=float(scenario_confidence),
            drivers=tuple(drivers),
            constraints=tuple(constraints),
            triggers=tuple(triggers),
            inhibitors=tuple(inhibitors),
            uncertainty_factors=tuple(uncertainty_factors),
            invalidation_signals=tuple(invalidation_signals),
        )


def validate_scenario_distribution(scenarios: Iterable[ScenarioVersion], *, tolerance: float = 1e-9) -> tuple[ScenarioVersion, ...]:
    items = tuple(scenarios)
    if not items:
        raise ValueError("forecast version requires at least one scenario")
    version_ids = {item.forecast_version_id for item in items}
    if len(version_ids) != 1:
        raise ValueError("all scenarios must belong to one forecast version")
    identities = {(item.scenario_type, item.label) for item in items}
    if len(identities) != len(items):
        raise ValueError("duplicate scenario identity in forecast version")
    raw_total = sum(item.raw_probability for item in items)
    calibrated_total = sum(item.calibrated_probability for item in items)
    if abs(raw_total - 1.0) > tolerance:
        raise ValueError("raw scenario probabilities must sum to 1")
    if abs(calibrated_total - 1.0) > tolerance:
        raise ValueError("calibrated scenario probabilities must sum to 1")
    return items


class SQLiteAdvancedForecastRepository:
    """Durable immutable forecast-version repository in the project-local SQLite DB."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    def save_forecast(self, forecast: ForecastRecord) -> ForecastRecord:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            existing = connection.execute(
                """
                SELECT target_key, question, horizon, evaluation_deadline, status,
                       created_at, updated_at
                FROM forecasts WHERE forecast_id = ?
                """,
                (forecast.forecast_id,),
            ).fetchone()
            expected = (
                forecast.target_key,
                forecast.question,
                forecast.horizon,
                forecast.evaluation_deadline.isoformat(),
                forecast.status,
                forecast.created_at.isoformat(),
                forecast.updated_at.isoformat(),
            )
            if existing is not None:
                if tuple(existing) != expected:
                    raise ValueError("existing forecast identity conflicts with immutable forecast definition")
                return forecast
            connection.execute(
                """
                INSERT INTO forecasts(
                    forecast_id, target_key, question, horizon, evaluation_deadline,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (forecast.forecast_id, *expected),
            )
        return forecast

    def save_version(
        self,
        version: ForecastVersion,
        scenarios: Iterable[ScenarioVersion],
    ) -> ForecastVersion:
        scenario_items = validate_scenario_distribution(scenarios)
        if any(item.forecast_version_id != version.forecast_version_id for item in scenario_items):
            raise ValueError("scenario forecast_version_id does not match forecast version")

        version_payload = (
            version.forecast_id,
            version.version_number,
            json.dumps(version.input_snapshot, sort_keys=True),
            json.dumps(version.provenance_refs),
            json.dumps(version.assumptions),
            version.change_reason,
            version.created_at.isoformat(),
        )
        scenario_payloads = [
            (
                item.scenario_version_id,
                item.forecast_version_id,
                item.scenario_type,
                item.label,
                item.raw_probability,
                item.calibrated_probability,
                item.scenario_confidence,
                json.dumps(item.drivers),
                json.dumps(item.constraints),
                json.dumps(item.triggers),
                json.dumps(item.inhibitors),
                json.dumps(item.uncertainty_factors),
                json.dumps(item.invalidation_signals),
            )
            for item in scenario_items
        ]

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            if connection.execute(
                "SELECT 1 FROM forecasts WHERE forecast_id = ?",
                (version.forecast_id,),
            ).fetchone() is None:
                raise ValueError("forecast must exist before saving a version")

            existing = connection.execute(
                """
                SELECT forecast_id, version_number, input_snapshot_json,
                       provenance_refs_json, assumptions_json, change_reason, created_at
                FROM forecast_versions WHERE forecast_version_id = ?
                """,
                (version.forecast_version_id,),
            ).fetchone()
            if existing is not None:
                if tuple(existing) != version_payload:
                    raise ValueError("forecast version is immutable")
                persisted = connection.execute(
                    """
                    SELECT scenario_version_id, forecast_version_id, scenario_type, label,
                           raw_probability, calibrated_probability, scenario_confidence,
                           drivers_json, constraints_json, triggers_json, inhibitors_json,
                           uncertainty_factors_json, invalidation_signals_json
                    FROM forecast_scenario_versions
                    WHERE forecast_version_id = ?
                    ORDER BY scenario_version_id
                    """,
                    (version.forecast_version_id,),
                ).fetchall()
                if sorted(tuple(row) for row in persisted) != sorted(scenario_payloads):
                    raise ValueError("forecast version scenario set is immutable")
                return version

            expected_next = int(
                connection.execute(
                    "SELECT COALESCE(MAX(version_number), 0) + 1 FROM forecast_versions WHERE forecast_id = ?",
                    (version.forecast_id,),
                ).fetchone()[0]
            )
            if version.version_number != expected_next:
                raise ValueError(f"forecast version must be monotonic; expected version {expected_next}")

            connection.execute(
                """
                INSERT INTO forecast_versions(
                    forecast_version_id, forecast_id, version_number,
                    input_snapshot_json, provenance_refs_json, assumptions_json,
                    change_reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (version.forecast_version_id, *version_payload),
            )
            connection.executemany(
                """
                INSERT INTO forecast_scenario_versions(
                    scenario_version_id, forecast_version_id, scenario_type, label,
                    raw_probability, calibrated_probability, scenario_confidence,
                    drivers_json, constraints_json, triggers_json, inhibitors_json,
                    uncertainty_factors_json, invalidation_signals_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                scenario_payloads,
            )
        return version

    def next_version_number(self, forecast_id_value: str) -> int:
        with sqlite3.connect(self.database_path) as connection:
            return int(
                connection.execute(
                    "SELECT COALESCE(MAX(version_number), 0) + 1 FROM forecast_versions WHERE forecast_id = ?",
                    (_nonempty(forecast_id_value, "forecast_id"),),
                ).fetchone()[0]
            )

    def get_forecast(self, forecast_id_value: str) -> ForecastRecord | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT forecast_id, target_key, question, horizon, evaluation_deadline,
                       status, created_at, updated_at
                FROM forecasts WHERE forecast_id = ?
                """,
                (forecast_id_value,),
            ).fetchone()
        if row is None:
            return None
        return ForecastRecord(
            forecast_id=row[0],
            target_key=row[1],
            question=row[2],
            horizon=row[3],
            evaluation_deadline=datetime.fromisoformat(row[4]),
            status=row[5],
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
        )

    def list_versions(self, forecast_id_value: str) -> tuple[ForecastVersion, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT forecast_version_id, forecast_id, version_number,
                       input_snapshot_json, provenance_refs_json, assumptions_json,
                       change_reason, created_at
                FROM forecast_versions
                WHERE forecast_id = ?
                ORDER BY version_number
                """,
                (forecast_id_value,),
            ).fetchall()
        return tuple(
            ForecastVersion(
                forecast_version_id=row[0],
                forecast_id=row[1],
                version_number=int(row[2]),
                input_snapshot=json.loads(row[3]),
                provenance_refs=tuple(json.loads(row[4])),
                assumptions=tuple(json.loads(row[5])),
                change_reason=row[6],
                created_at=datetime.fromisoformat(row[7]),
            )
            for row in rows
        )

    def list_scenarios(self, forecast_version_id_value: str) -> tuple[ScenarioVersion, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT scenario_version_id, forecast_version_id, scenario_type, label,
                       raw_probability, calibrated_probability, scenario_confidence,
                       drivers_json, constraints_json, triggers_json, inhibitors_json,
                       uncertainty_factors_json, invalidation_signals_json
                FROM forecast_scenario_versions
                WHERE forecast_version_id = ?
                ORDER BY scenario_type, label, scenario_version_id
                """,
                (forecast_version_id_value,),
            ).fetchall()
        return tuple(
            ScenarioVersion(
                scenario_version_id=row[0],
                forecast_version_id=row[1],
                scenario_type=row[2],
                label=row[3],
                raw_probability=float(row[4]),
                calibrated_probability=float(row[5]),
                scenario_confidence=float(row[6]),
                drivers=tuple(json.loads(row[7])),
                constraints=tuple(json.loads(row[8])),
                triggers=tuple(json.loads(row[9])),
                inhibitors=tuple(json.loads(row[10])),
                uncertainty_factors=tuple(json.loads(row[11])),
                invalidation_signals=tuple(json.loads(row[12])),
            )
            for row in rows
        )


__all__ = [
    "ACTIVE",
    "RESOLVED",
    "INVALIDATED",
    "CLOSED",
    "FORECAST_STATUSES",
    "ForecastRecord",
    "ForecastVersion",
    "ScenarioVersion",
    "SQLiteAdvancedForecastRepository",
    "forecast_id",
    "forecast_version_id",
    "scenario_version_id",
    "validate_scenario_distribution",
]
