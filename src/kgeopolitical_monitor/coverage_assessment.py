"""Phase 11 deterministic operational coverage assessment orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .coverage_dimension_evaluation import CoverageDimensionEvaluator
from .operational_coverage import (
    CoverageRequirementResult,
    CoverageSnapshot,
    OperationalCoverageService,
)
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


@dataclass(frozen=True)
class CoverageAssessment:
    snapshot: CoverageSnapshot
    requirement_results: tuple[CoverageRequirementResult, ...]


class OperationalCoverageAssessmentService:
    """Evaluate one explicit contract and persist one immutable aggregate snapshot."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.coverage = OperationalCoverageService(runtime)
        self.evaluator = CoverageDimensionEvaluator(runtime, self.coverage)

    def assess(
        self,
        coverage_contract_id: str,
        *,
        assessed_at: datetime,
    ) -> CoverageAssessment:
        assessed = _normalize_time(assessed_at)
        drafts = self.evaluator.evaluate_contract(
            coverage_contract_id,
            assessed_at=assessed,
        )
        snapshot = self.coverage.create_snapshot(
            coverage_contract_id,
            drafts,
            assessed_at=assessed,
        )
        persisted = self.coverage.snapshot_results(snapshot.coverage_snapshot_id)
        expected = self.coverage.requirements(coverage_contract_id)
        if len(persisted) != len(expected):
            raise RuntimeError(
                "operational coverage snapshot/result cardinality invariant failed"
            )
        return CoverageAssessment(
            snapshot=snapshot,
            requirement_results=persisted,
        )


__all__ = ["CoverageAssessment", "OperationalCoverageAssessmentService"]
