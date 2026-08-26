"""Phase 11 durable operational coverage contract and snapshot foundation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from hashlib import sha256
import json
import sqlite3
from typing import Iterable, Mapping

from .operational_monitoring import (
    OperationalMonitoringRuntime,
    _normalize_time,
    utc_now,
)


MEASURABLE_DIMENSIONS = {
    "SOURCE_CLASS",
    "SOURCE_ID",
    "SOURCE_AVAILABILITY",
    "REGION_LANGUAGE",
    "FRESHNESS",
}

DECLARABLE_DIMENSIONS = MEASURABLE_DIMENSIONS | {
    "TIME_WINDOW",
    "REGION",
    "COUNTRY",
    "ACTOR",
    "STORYLINE",
    "EVENT_CATEGORY",
    "LANGUAGE",
    "IMPORTANCE_THRESHOLD",
    "VERIFICATION_REQUIREMENT",
    "CROSS_CHECK_REQUIREMENT",
    "FORECAST_REQUIREMENT",
    "REPORT_DEPTH",
}

RESULT_STATUSES = {
    "SATISFIED",
    "GAP",
    "UNAVAILABLE",
    "STALE",
    "UNKNOWN",
    "UNMEASURED",
}

KNOWN_ASSESSMENT_STATUSES = {
    "SATISFIED",
    "GAP",
    "UNAVAILABLE",
    "STALE",
}


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_id(prefix: str, payload: object) -> str:
    digest = sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _normalize_nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_dimension(value: str) -> str:
    dimension = _normalize_nonempty(value, "dimension").upper()
    if dimension not in DECLARABLE_DIMENSIONS:
        raise ValueError(f"unsupported coverage dimension: {dimension}")
    return dimension


def _normalize_status(value: str) -> str:
    status = _normalize_nonempty(value, "status").upper()
    if status not in RESULT_STATUSES:
        raise ValueError(f"unsupported coverage result status: {status}")
    return status


def _normalize_parameters(value: Mapping[str, object] | None) -> dict[str, object]:
    parameters = dict(value or {})
    try:
        encoded = _canonical_json(parameters)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError("coverage requirement parameters must be JSON-serializable") from exc
    if not isinstance(decoded, dict):
        raise ValueError("coverage requirement parameters must be an object")
    return decoded


@dataclass(frozen=True)
class CoverageRequirementSpec:
    dimension: str
    requirement_key: str
    required: bool = True
    parameters: Mapping[str, object] = field(default_factory=dict)

    def normalized_payload(self) -> dict[str, object]:
        return {
            "dimension": _normalize_dimension(self.dimension),
            "requirement_key": _normalize_nonempty(
                self.requirement_key, "requirement_key"
            ),
            "required": bool(self.required),
            "parameters": _normalize_parameters(self.parameters),
        }


@dataclass(frozen=True)
class CoverageContract:
    coverage_contract_id: str
    scope_key: str
    name: str
    watch_id: str | None
    assessment_window_seconds: int
    freshness_requirement_seconds: int
    active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CoverageRequirement:
    requirement_id: str
    coverage_contract_id: str
    dimension: str
    requirement_key: str
    required: bool
    parameters: dict[str, object]
    created_at: datetime


@dataclass(frozen=True)
class CoverageRequirementResultDraft:
    requirement_id: str
    status: str
    evidence_refs: tuple[str, ...]
    explanation: str
    measured_at: datetime

    def normalized_payload(self) -> dict[str, object]:
        references = tuple(
            sorted(
                {
                    _normalize_nonempty(reference, "evidence_ref")
                    for reference in self.evidence_refs
                }
            )
        )
        return {
            "requirement_id": _normalize_nonempty(
                self.requirement_id, "requirement_id"
            ),
            "status": _normalize_status(self.status),
            "evidence_refs": references,
            "explanation": _normalize_nonempty(self.explanation, "explanation"),
            "measured_at": _normalize_time(self.measured_at),
        }


@dataclass(frozen=True)
class CoverageRequirementResult:
    coverage_snapshot_id: str
    requirement_id: str
    status: str
    evidence_refs: tuple[str, ...]
    explanation: str
    measured_at: datetime


@dataclass(frozen=True)
class CoverageSnapshot:
    coverage_snapshot_id: str
    coverage_contract_id: str
    assessed_at: datetime
    window_start: datetime
    window_end: datetime
    required_count: int
    satisfied_count: int
    gap_count: int
    unavailable_count: int
    stale_count: int
    unknown_count: int
    unmeasured_count: int
    coverage_ratio: float
    coverage_confidence: float
    limitations: tuple[str, ...]
    created_at: datetime


class OperationalCoverageService:
    """Persist immutable coverage contracts and deterministic assessment snapshots."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path

    def create_contract(
        self,
        *,
        scope_key: str,
        name: str,
        assessment_window_seconds: int,
        freshness_requirement_seconds: int,
        requirements: Iterable[CoverageRequirementSpec],
        watch_id: str | None = None,
        active: bool = True,
        created_at: datetime | None = None,
    ) -> CoverageContract:
        scope = _normalize_nonempty(scope_key, "scope_key")
        contract_name = _normalize_nonempty(name, "name")
        watch = _normalize_nonempty(watch_id, "watch_id") if watch_id is not None else None
        if watch is not None and self.runtime.repository.get_watch(watch) is None:
            raise ValueError("watch does not exist")
        if assessment_window_seconds <= 0:
            raise ValueError("assessment_window_seconds must be positive")
        if freshness_requirement_seconds <= 0:
            raise ValueError("freshness_requirement_seconds must be positive")

        normalized_specs = [item.normalized_payload() for item in requirements]
        if not normalized_specs:
            raise ValueError("coverage contract requires at least one requirement")

        identity_keys: set[tuple[str, str]] = set()
        for item in normalized_specs:
            key = (str(item["dimension"]), str(item["requirement_key"]))
            if key in identity_keys:
                raise ValueError(
                    "coverage contract contains duplicate dimension/requirement_key"
                )
            identity_keys.add(key)

        normalized_specs.sort(
            key=lambda item: (
                str(item["dimension"]),
                str(item["requirement_key"]),
                _canonical_json(item["parameters"]),
                bool(item["required"]),
            )
        )
        required_count = sum(bool(item["required"]) for item in normalized_specs)
        if required_count == 0:
            raise ValueError("coverage contract requires at least one required unit")

        definition = {
            "scope_key": scope,
            "name": contract_name,
            "watch_id": watch,
            "assessment_window_seconds": int(assessment_window_seconds),
            "freshness_requirement_seconds": int(freshness_requirement_seconds),
            "requirements": normalized_specs,
        }
        coverage_contract_id = _stable_id("coverage-contract", definition)
        timestamp = _normalize_time(created_at or utc_now())

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            existing = connection.execute(
                """
                SELECT scope_key, name, watch_id, assessment_window_seconds,
                       freshness_requirement_seconds, active, created_at, updated_at
                FROM operational_coverage_contracts
                WHERE coverage_contract_id = ?
                """,
                (coverage_contract_id,),
            ).fetchone()

            if existing is None:
                connection.execute(
                    """
                    INSERT INTO operational_coverage_contracts(
                        coverage_contract_id, scope_key, name, watch_id,
                        assessment_window_seconds, freshness_requirement_seconds,
                        active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        coverage_contract_id,
                        scope,
                        contract_name,
                        watch,
                        int(assessment_window_seconds),
                        int(freshness_requirement_seconds),
                        int(bool(active)),
                        timestamp.isoformat(),
                        timestamp.isoformat(),
                    ),
                )
                for item in normalized_specs:
                    requirement_payload = {
                        "coverage_contract_id": coverage_contract_id,
                        **item,
                    }
                    requirement_id = _stable_id(
                        "coverage-requirement", requirement_payload
                    )
                    connection.execute(
                        """
                        INSERT INTO operational_coverage_requirements(
                            requirement_id, coverage_contract_id, dimension,
                            requirement_key, required, parameters_json, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            requirement_id,
                            coverage_contract_id,
                            item["dimension"],
                            item["requirement_key"],
                            int(bool(item["required"])),
                            _canonical_json(item["parameters"]),
                            timestamp.isoformat(),
                        ),
                    )
            else:
                persisted_specs = [
                    {
                        "dimension": row[0],
                        "requirement_key": row[1],
                        "required": bool(row[2]),
                        "parameters": json.loads(row[3]),
                    }
                    for row in connection.execute(
                        """
                        SELECT dimension, requirement_key, required, parameters_json
                        FROM operational_coverage_requirements
                        WHERE coverage_contract_id = ?
                        ORDER BY dimension, requirement_key, parameters_json, required
                        """,
                        (coverage_contract_id,),
                    ).fetchall()
                ]
                if persisted_specs != normalized_specs:
                    raise RuntimeError("coverage contract identity collision")

        contract = self.get_contract(coverage_contract_id)
        if contract is None:
            raise RuntimeError("failed to persist coverage contract")
        return contract

    def get_contract(self, coverage_contract_id: str) -> CoverageContract | None:
        contract_id = _normalize_nonempty(
            coverage_contract_id, "coverage_contract_id"
        )
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT coverage_contract_id, scope_key, name, watch_id,
                       assessment_window_seconds, freshness_requirement_seconds,
                       active, created_at, updated_at
                FROM operational_coverage_contracts
                WHERE coverage_contract_id = ?
                """,
                (contract_id,),
            ).fetchone()
        if row is None:
            return None
        return CoverageContract(
            coverage_contract_id=row[0],
            scope_key=row[1],
            name=row[2],
            watch_id=row[3],
            assessment_window_seconds=int(row[4]),
            freshness_requirement_seconds=int(row[5]),
            active=bool(row[6]),
            created_at=datetime.fromisoformat(row[7]),
            updated_at=datetime.fromisoformat(row[8]),
        )

    def requirements(
        self, coverage_contract_id: str
    ) -> tuple[CoverageRequirement, ...]:
        contract_id = _normalize_nonempty(
            coverage_contract_id, "coverage_contract_id"
        )
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT requirement_id, coverage_contract_id, dimension,
                       requirement_key, required, parameters_json, created_at
                FROM operational_coverage_requirements
                WHERE coverage_contract_id = ?
                ORDER BY dimension, requirement_key, requirement_id
                """,
                (contract_id,),
            ).fetchall()
        return tuple(
            CoverageRequirement(
                requirement_id=row[0],
                coverage_contract_id=row[1],
                dimension=row[2],
                requirement_key=row[3],
                required=bool(row[4]),
                parameters=json.loads(row[5]),
                created_at=datetime.fromisoformat(row[6]),
            )
            for row in rows
        )

    def create_snapshot(
        self,
        coverage_contract_id: str,
        results: Iterable[CoverageRequirementResultDraft],
        *,
        assessed_at: datetime,
    ) -> CoverageSnapshot:
        contract = self.get_contract(coverage_contract_id)
        if contract is None:
            raise ValueError("coverage contract does not exist")
        assessed = _normalize_time(assessed_at)
        window_end = assessed
        window_start = assessed - timedelta(
            seconds=contract.assessment_window_seconds
        )

        requirements = self.requirements(contract.coverage_contract_id)
        requirement_by_id = {item.requirement_id: item for item in requirements}
        if not requirement_by_id:
            raise ValueError("coverage contract has no requirements")

        normalized_results: dict[str, dict[str, object]] = {}
        for result in results:
            item = result.normalized_payload()
            requirement_id = str(item["requirement_id"])
            requirement = requirement_by_id.get(requirement_id)
            if requirement is None:
                raise ValueError(
                    "coverage result requirement does not belong to contract"
                )
            if requirement_id in normalized_results:
                raise ValueError("duplicate coverage result requirement_id")
            measured_at = item["measured_at"]
            if not isinstance(measured_at, datetime):
                raise TypeError("normalized measured_at must be datetime")
            if measured_at > assessed:
                raise ValueError("coverage result measured_at cannot be after assessed_at")
            normalized_results[requirement_id] = item

        missing = sorted(set(requirement_by_id) - set(normalized_results))
        if missing:
            raise ValueError(
                "coverage snapshot requires one result for every contract requirement"
            )

        required_results = [
            normalized_results[item.requirement_id]
            for item in requirements
            if item.required
        ]
        if not required_results:
            raise ValueError("coverage contract has no required units")

        counts = {status: 0 for status in RESULT_STATUSES}
        for item in required_results:
            counts[str(item["status"])] += 1

        required_count = len(required_results)
        satisfied_count = counts["SATISFIED"]
        known_count = sum(counts[status] for status in KNOWN_ASSESSMENT_STATUSES)
        coverage_ratio = satisfied_count / required_count
        coverage_confidence = known_count / required_count

        limitations = tuple(
            sorted(
                f"{requirement_by_id[requirement_id].dimension}:"
                f"{requirement_by_id[requirement_id].requirement_key}:"
                f"{normalized_results[requirement_id]['status']}"
                for requirement_id in normalized_results
                if requirement_by_id[requirement_id].required
                and normalized_results[requirement_id]["status"] != "SATISFIED"
            )
        )

        temporal_identity = {
            "coverage_contract_id": contract.coverage_contract_id,
            "assessed_at": assessed.isoformat(),
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
        }
        coverage_snapshot_id = _stable_id("coverage-snapshot", temporal_identity)

        snapshot_payload = {
            "coverage_snapshot_id": coverage_snapshot_id,
            "coverage_contract_id": contract.coverage_contract_id,
            "assessed_at": assessed.isoformat(),
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "required_count": required_count,
            "satisfied_count": satisfied_count,
            "gap_count": counts["GAP"],
            "unavailable_count": counts["UNAVAILABLE"],
            "stale_count": counts["STALE"],
            "unknown_count": counts["UNKNOWN"],
            "unmeasured_count": counts["UNMEASURED"],
            "coverage_ratio": coverage_ratio,
            "coverage_confidence": coverage_confidence,
            "limitations": limitations,
            "results": [
                {
                    "requirement_id": requirement_id,
                    "status": normalized_results[requirement_id]["status"],
                    "evidence_refs": normalized_results[requirement_id]["evidence_refs"],
                    "explanation": normalized_results[requirement_id]["explanation"],
                    "measured_at": normalized_results[requirement_id][
                        "measured_at"
                    ].isoformat(),
                }
                for requirement_id in sorted(normalized_results)
            ],
        }

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            existing = connection.execute(
                """
                SELECT coverage_contract_id, assessed_at, window_start, window_end,
                       required_count, satisfied_count, gap_count,
                       unavailable_count, stale_count, unknown_count,
                       unmeasured_count, coverage_ratio, coverage_confidence,
                       limitations_json, created_at
                FROM operational_coverage_snapshots
                WHERE coverage_snapshot_id = ?
                """,
                (coverage_snapshot_id,),
            ).fetchone()

            if existing is None:
                connection.execute(
                    """
                    INSERT INTO operational_coverage_snapshots(
                        coverage_snapshot_id, coverage_contract_id, assessed_at,
                        window_start, window_end, required_count, satisfied_count,
                        gap_count, unavailable_count, stale_count, unknown_count,
                        unmeasured_count, coverage_ratio, coverage_confidence,
                        limitations_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        coverage_snapshot_id,
                        contract.coverage_contract_id,
                        assessed.isoformat(),
                        window_start.isoformat(),
                        window_end.isoformat(),
                        required_count,
                        satisfied_count,
                        counts["GAP"],
                        counts["UNAVAILABLE"],
                        counts["STALE"],
                        counts["UNKNOWN"],
                        counts["UNMEASURED"],
                        coverage_ratio,
                        coverage_confidence,
                        _canonical_json(limitations),
                        assessed.isoformat(),
                    ),
                )
                for item in snapshot_payload["results"]:
                    connection.execute(
                        """
                        INSERT INTO operational_coverage_requirement_results(
                            coverage_snapshot_id, requirement_id, status,
                            evidence_refs_json, explanation, measured_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            coverage_snapshot_id,
                            item["requirement_id"],
                            item["status"],
                            _canonical_json(item["evidence_refs"]),
                            item["explanation"],
                            item["measured_at"],
                        ),
                    )
            else:
                persisted = self._snapshot_payload(
                    connection, coverage_snapshot_id
                )
                if persisted != snapshot_payload:
                    raise ValueError(
                        "coverage snapshot is immutable for this contract and assessed_at"
                    )

        snapshot = self.get_snapshot(coverage_snapshot_id)
        if snapshot is None:
            raise RuntimeError("failed to persist coverage snapshot")
        return snapshot

    def _snapshot_payload(
        self, connection: sqlite3.Connection, coverage_snapshot_id: str
    ) -> dict[str, object]:
        row = connection.execute(
            """
            SELECT coverage_contract_id, assessed_at, window_start, window_end,
                   required_count, satisfied_count, gap_count,
                   unavailable_count, stale_count, unknown_count,
                   unmeasured_count, coverage_ratio, coverage_confidence,
                   limitations_json
            FROM operational_coverage_snapshots
            WHERE coverage_snapshot_id = ?
            """,
            (coverage_snapshot_id,),
        ).fetchone()
        if row is None:
            raise ValueError("coverage snapshot does not exist")
        result_rows = connection.execute(
            """
            SELECT requirement_id, status, evidence_refs_json, explanation, measured_at
            FROM operational_coverage_requirement_results
            WHERE coverage_snapshot_id = ?
            ORDER BY requirement_id
            """,
            (coverage_snapshot_id,),
        ).fetchall()
        return {
            "coverage_snapshot_id": coverage_snapshot_id,
            "coverage_contract_id": row[0],
            "assessed_at": row[1],
            "window_start": row[2],
            "window_end": row[3],
            "required_count": int(row[4]),
            "satisfied_count": int(row[5]),
            "gap_count": int(row[6]),
            "unavailable_count": int(row[7]),
            "stale_count": int(row[8]),
            "unknown_count": int(row[9]),
            "unmeasured_count": int(row[10]),
            "coverage_ratio": float(row[11]),
            "coverage_confidence": float(row[12]),
            "limitations": tuple(json.loads(row[13])),
            "results": [
                {
                    "requirement_id": item[0],
                    "status": item[1],
                    "evidence_refs": tuple(json.loads(item[2])),
                    "explanation": item[3],
                    "measured_at": item[4],
                }
                for item in result_rows
            ],
        }

    def get_snapshot(self, coverage_snapshot_id: str) -> CoverageSnapshot | None:
        snapshot_id = _normalize_nonempty(
            coverage_snapshot_id, "coverage_snapshot_id"
        )
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT coverage_snapshot_id, coverage_contract_id, assessed_at,
                       window_start, window_end, required_count, satisfied_count,
                       gap_count, unavailable_count, stale_count, unknown_count,
                       unmeasured_count, coverage_ratio, coverage_confidence,
                       limitations_json, created_at
                FROM operational_coverage_snapshots
                WHERE coverage_snapshot_id = ?
                """,
                (snapshot_id,),
            ).fetchone()
        if row is None:
            return None
        return CoverageSnapshot(
            coverage_snapshot_id=row[0],
            coverage_contract_id=row[1],
            assessed_at=datetime.fromisoformat(row[2]),
            window_start=datetime.fromisoformat(row[3]),
            window_end=datetime.fromisoformat(row[4]),
            required_count=int(row[5]),
            satisfied_count=int(row[6]),
            gap_count=int(row[7]),
            unavailable_count=int(row[8]),
            stale_count=int(row[9]),
            unknown_count=int(row[10]),
            unmeasured_count=int(row[11]),
            coverage_ratio=float(row[12]),
            coverage_confidence=float(row[13]),
            limitations=tuple(json.loads(row[14])),
            created_at=datetime.fromisoformat(row[15]),
        )

    def snapshot_results(
        self, coverage_snapshot_id: str
    ) -> tuple[CoverageRequirementResult, ...]:
        snapshot_id = _normalize_nonempty(
            coverage_snapshot_id, "coverage_snapshot_id"
        )
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT coverage_snapshot_id, requirement_id, status,
                       evidence_refs_json, explanation, measured_at
                FROM operational_coverage_requirement_results
                WHERE coverage_snapshot_id = ?
                ORDER BY requirement_id
                """,
                (snapshot_id,),
            ).fetchall()
        return tuple(
            CoverageRequirementResult(
                coverage_snapshot_id=row[0],
                requirement_id=row[1],
                status=row[2],
                evidence_refs=tuple(json.loads(row[3])),
                explanation=row[4],
                measured_at=datetime.fromisoformat(row[5]),
            )
            for row in rows
        )

    def snapshot_history(
        self, coverage_contract_id: str
    ) -> tuple[CoverageSnapshot, ...]:
        contract_id = _normalize_nonempty(
            coverage_contract_id, "coverage_contract_id"
        )
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT coverage_snapshot_id
                FROM operational_coverage_snapshots
                WHERE coverage_contract_id = ?
                ORDER BY assessed_at, coverage_snapshot_id
                """,
                (contract_id,),
            ).fetchall()
        snapshots = [
            self.get_snapshot(row[0])
            for row in rows
        ]
        return tuple(item for item in snapshots if item is not None)


__all__ = [
    "DECLARABLE_DIMENSIONS",
    "KNOWN_ASSESSMENT_STATUSES",
    "MEASURABLE_DIMENSIONS",
    "RESULT_STATUSES",
    "CoverageContract",
    "CoverageRequirement",
    "CoverageRequirementResult",
    "CoverageRequirementResultDraft",
    "CoverageRequirementSpec",
    "CoverageSnapshot",
    "OperationalCoverageService",
]
