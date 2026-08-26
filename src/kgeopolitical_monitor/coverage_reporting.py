"""Phase 11 historical coverage query and M13 reporting integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import sqlite3

from .operational_coverage import (
    CoverageContract,
    CoverageRequirement,
    CoverageRequirementResult,
    CoverageSnapshot,
    OperationalCoverageService,
)
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time
from .region_language_coverage import normalize_language_code, normalize_region_code
from .report_assembly import ReportAssembler, ReportAssemblyRequest
from .reporting_environment import (
    COVERAGE_REPORT,
    GLOBAL_GEOPOLITICAL_BRIEF,
    REGION,
    REGIONAL_COUNTRY_BRIEF,
    ReportBundle,
    ReportSnapshot,
    SQLiteReportRepository,
)


@dataclass(frozen=True)
class CoverageSnapshotView:
    contract: CoverageContract
    snapshot: CoverageSnapshot
    requirements: tuple[CoverageRequirement, ...]
    results: tuple[CoverageRequirementResult, ...]

    @property
    def unknown_requirements(self) -> tuple[str, ...]:
        return tuple(
            item.requirement_id for item in self.results if item.status == "UNKNOWN"
        )

    @property
    def unmeasured_requirements(self) -> tuple[str, ...]:
        return tuple(
            item.requirement_id for item in self.results if item.status == "UNMEASURED"
        )


class OperationalCoverageQuery:
    """Read-only history/query facade over immutable Phase 11 coverage state."""

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        coverage: OperationalCoverageService | None = None,
    ):
        self.runtime = runtime
        self.coverage = coverage or OperationalCoverageService(runtime)

    def snapshot_view(self, coverage_snapshot_id: str) -> CoverageSnapshotView:
        snapshot = self.coverage.get_snapshot(coverage_snapshot_id)
        if snapshot is None:
            raise ValueError("coverage snapshot does not exist")
        contract = self.coverage.get_contract(snapshot.coverage_contract_id)
        if contract is None:
            raise RuntimeError("coverage snapshot references a missing contract")
        requirements = self.coverage.requirements(contract.coverage_contract_id)
        results = self.coverage.snapshot_results(snapshot.coverage_snapshot_id)
        if {item.requirement_id for item in requirements} != {
            item.requirement_id for item in results
        }:
            raise RuntimeError("coverage snapshot result set is incomplete")
        return CoverageSnapshotView(contract, snapshot, requirements, results)

    def history(self, coverage_contract_id: str) -> tuple[CoverageSnapshotView, ...]:
        contract = self.coverage.get_contract(coverage_contract_id)
        if contract is None:
            raise ValueError("coverage contract does not exist")
        return tuple(
            self.snapshot_view(snapshot.coverage_snapshot_id)
            for snapshot in self.coverage.snapshot_history(contract.coverage_contract_id)
        )

    def latest_snapshot(
        self, coverage_contract_id: str
    ) -> CoverageSnapshotView | None:
        history = self.history(coverage_contract_id)
        return history[-1] if history else None


class CoverageAwareReportRepository(SQLiteReportRepository):
    """M13 repository validation extended to canonical Phase 11 snapshots."""

    @staticmethod
    def _reference_exists(
        connection: sqlite3.Connection,
        kind: str,
        value: str,
    ) -> bool:
        if kind == COVERAGE_REPORT:
            if connection.execute(
                """
                SELECT 1
                FROM operational_coverage_snapshots
                WHERE coverage_snapshot_id = ?
                """,
                (value,),
            ).fetchone() is not None:
                return True
        return SQLiteReportRepository._reference_exists(connection, kind, value)


class CoverageReportAssembler(ReportAssembler):
    """Use the canonical M13 report store while adding Phase 11 coverage payloads."""

    def __init__(self, database_path: str | Path):
        super().__init__(database_path)
        self.repository = CoverageAwareReportRepository(self.database_path)

    def _phase11_payload(self, coverage_snapshot_id: str) -> dict[str, object] | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT snapshot.coverage_snapshot_id,
                       snapshot.coverage_contract_id,
                       contract.scope_key,
                       contract.name,
                       contract.watch_id,
                       contract.assessment_window_seconds,
                       contract.freshness_requirement_seconds,
                       snapshot.assessed_at,
                       snapshot.window_start,
                       snapshot.window_end,
                       snapshot.required_count,
                       snapshot.satisfied_count,
                       snapshot.gap_count,
                       snapshot.unavailable_count,
                       snapshot.stale_count,
                       snapshot.unknown_count,
                       snapshot.unmeasured_count,
                       snapshot.coverage_ratio,
                       snapshot.coverage_confidence,
                       snapshot.limitations_json,
                       snapshot.created_at
                FROM operational_coverage_snapshots AS snapshot
                JOIN operational_coverage_contracts AS contract
                  ON contract.coverage_contract_id = snapshot.coverage_contract_id
                WHERE snapshot.coverage_snapshot_id = ?
                """,
                (coverage_snapshot_id,),
            ).fetchone()
            if row is None:
                return None
            result_rows = connection.execute(
                """
                SELECT requirement.requirement_id,
                       requirement.dimension,
                       requirement.requirement_key,
                       requirement.required,
                       requirement.parameters_json,
                       result.status,
                       result.evidence_refs_json,
                       result.explanation,
                       result.measured_at
                FROM operational_coverage_requirement_results AS result
                JOIN operational_coverage_requirements AS requirement
                  ON requirement.requirement_id = result.requirement_id
                WHERE result.coverage_snapshot_id = ?
                ORDER BY requirement.dimension,
                         requirement.requirement_key,
                         requirement.requirement_id
                """,
                (coverage_snapshot_id,),
            ).fetchall()

        requirement_results = [
            {
                "requirement_id": item[0],
                "dimension": item[1],
                "requirement_key": item[2],
                "required": bool(item[3]),
                "parameters": json.loads(item[4]),
                "status": item[5],
                "evidence_refs": json.loads(item[6]),
                "explanation": item[7],
                "measured_at": item[8],
            }
            for item in result_rows
        ]
        unknown = [
            f"{item['dimension']}:{item['requirement_key']}"
            for item in requirement_results
            if item["required"] and item["status"] == "UNKNOWN"
        ]
        unmeasured = [
            f"{item['dimension']}:{item['requirement_key']}"
            for item in requirement_results
            if item["required"] and item["status"] == "UNMEASURED"
        ]
        return {
            "coverage_report_id": row[0],
            "coverage_snapshot_id": row[0],
            "coverage_contract_id": row[1],
            "scope_key": row[2],
            "name": row[3],
            "watch_id": row[4],
            "assessment_window_seconds": int(row[5]),
            "freshness_requirement_seconds": int(row[6]),
            "assessed_at": row[7],
            "window_start": row[8],
            "window_end": row[9],
            "required_count": int(row[10]),
            "satisfied_count": int(row[11]),
            "gap_count": int(row[12]),
            "unavailable_count": int(row[13]),
            "stale_count": int(row[14]),
            "unknown_count": int(row[15]),
            "unmeasured_count": int(row[16]),
            "coverage_ratio": float(row[17]),
            "coverage_confidence": float(row[18]),
            "limitations": json.loads(row[19]),
            "created_at": row[20],
            "unknown_requirements": unknown,
            "unmeasured_requirements": unmeasured,
            "requirement_results": requirement_results,
        }

    def _coverage_payloads(self, ids: tuple[str, ...]):
        phase11_payloads: list[dict[str, object]] = []
        phase11_refs: list[tuple[str, str, str]] = []
        legacy_ids: list[str] = []
        for coverage_id in ids:
            payload = self._phase11_payload(coverage_id)
            if payload is None:
                legacy_ids.append(coverage_id)
            else:
                phase11_payloads.append(payload)
                phase11_refs.append((COVERAGE_REPORT, coverage_id, "COVERAGE_INPUT"))

        legacy_payloads, legacy_refs = super()._coverage_payloads(tuple(legacy_ids))
        payloads = tuple(
            sorted(
                [*legacy_payloads, *phase11_payloads],
                key=lambda item: str(item["coverage_report_id"]),
            )
        )
        refs = tuple(
            sorted(
                {*legacy_refs, *phase11_refs},
                key=lambda item: (item[0], item[1], item[2]),
            )
        )
        return payloads, refs


class CoverageReportingService:
    """Create coverage-focused Global/Regional reports in the canonical M13 store."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path
        self.query = OperationalCoverageQuery(runtime)
        self.assembler = CoverageReportAssembler(self.database_path)

    def global_report(
        self,
        coverage_snapshot_id: str,
        *,
        title: str,
        summary: str,
        as_of: datetime,
        scope_key: str | None = None,
        persist: bool = True,
    ) -> ReportBundle:
        view = self.query.snapshot_view(coverage_snapshot_id)
        timestamp = _normalize_time(as_of)
        snapshot = ReportSnapshot.create(
            GLOBAL_GEOPOLITICAL_BRIEF,
            scope_key or view.contract.scope_key,
            title,
            summary,
            timestamp,
            created_at=timestamp,
            generator_version="p11.5",
        )
        return self.assembler.assemble(
            ReportAssemblyRequest(
                snapshot=snapshot,
                coverage_report_ids=(view.snapshot.coverage_snapshot_id,),
            ),
            persist=persist,
        )

    def regional_report(
        self,
        coverage_snapshot_id: str,
        region_code: str,
        language_codes: tuple[str, ...],
        *,
        title: str,
        summary: str,
        as_of: datetime,
        persist: bool = True,
    ) -> ReportBundle:
        view = self.query.snapshot_view(coverage_snapshot_id)
        region = normalize_region_code(region_code)
        languages = tuple(
            sorted({normalize_language_code(item) for item in language_codes})
        )
        if not languages:
            raise ValueError("regional coverage report requires at least one language")

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

        declared = {
            item.requirement_key
            for item in view.requirements
            if item.required and item.dimension == "REGION_LANGUAGE"
        }
        requested = {f"{region}:{language}" for language in languages}
        missing = sorted(requested - declared)
        if missing:
            raise ValueError(
                "coverage snapshot contract does not declare requested regional scope: "
                + ", ".join(missing)
            )

        timestamp = _normalize_time(as_of)
        snapshot = ReportSnapshot.create(
            REGIONAL_COUNTRY_BRIEF,
            f"region:{region}|languages:{','.join(languages)}",
            title,
            summary,
            timestamp,
            subject_ref_type=REGION,
            subject_ref_id=region,
            created_at=timestamp,
            generator_version="p11.5",
        )
        return self.assembler.assemble(
            ReportAssemblyRequest(
                snapshot=snapshot,
                coverage_report_ids=(view.snapshot.coverage_snapshot_id,),
            ),
            persist=persist,
        )


__all__ = [
    "CoverageAwareReportRepository",
    "CoverageReportAssembler",
    "CoverageReportingService",
    "CoverageSnapshotView",
    "OperationalCoverageQuery",
]
