from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.coverage_assessment import OperationalCoverageAssessmentService
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_coverage import (
    CoverageRequirementSpec,
    OperationalCoverageService,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


NOW = datetime(2026, 8, 26, 18, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Coverage watch",
        "Ukraine",
        30,
        watch_id="watch-coverage",
        created_at=NOW - timedelta(hours=6),
    )
    return runtime


def _success_adapter(source_id, source_name, source_class):
    class Adapter:
        def fetch(self, watch, collected_at):
            return [
                LiveSourceItem(
                    item_id=f"item-{source_id}-{int(collected_at.timestamp())}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title="Ukraine coverage update",
                    summary="Coverage assessment fixture.",
                    original_url=f"https://example.org/{source_id}",
                    collected_at=collected_at,
                )
            ]

    adapter = Adapter()
    adapter.source_id = source_id
    adapter.source_name = source_name
    adapter.source_class = source_class
    return adapter


def _failing_adapter(source_id, source_name, source_class):
    class Adapter:
        def fetch(self, watch, collected_at):
            raise RuntimeError(f"{source_id} unavailable")

    adapter = Adapter()
    adapter.source_id = source_id
    adapter.source_name = source_name
    adapter.source_class = source_class
    return adapter


def test_assessment_persists_exact_status_breakdown_ratio_and_confidence(tmp_path):
    runtime = _runtime(tmp_path)

    LiveSourceCollector(
        runtime,
        [
            _success_adapter("source-success", "Success Source", "Official sources"),
            _failing_adapter("source-fail", "Fail Source", "Structured data"),
            _failing_adapter("source-regional", "Regional Source", "Regional media"),
        ],
    ).collect("watch-coverage", NOW)

    stale_time = NOW - timedelta(minutes=30)
    LiveSourceCollector(
        runtime,
        [_success_adapter("source-stale", "Stale Source", "Official sources")],
    ).collect("watch-coverage", stale_time)

    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key="GLOBAL:coverage-metrics-test",
        name="Coverage metrics acceptance",
        watch_id="watch-coverage",
        assessment_window_seconds=7200,
        freshness_requirement_seconds=900,
        requirements=(
            CoverageRequirementSpec("SOURCE_ID", "source-success"),
            CoverageRequirementSpec("SOURCE_ID", "source-fail"),
            CoverageRequirementSpec("SOURCE_ID", "source-stale"),
            CoverageRequirementSpec("SOURCE_ID", "source-unknown"),
            CoverageRequirementSpec("SOURCE_CLASS", "Regional media"),
            CoverageRequirementSpec("ACTOR", "actor:unsupported"),
        ),
        created_at=NOW - timedelta(hours=4),
    )

    assessment_service = OperationalCoverageAssessmentService(runtime)
    assessment = assessment_service.assess(
        contract.coverage_contract_id,
        assessed_at=NOW,
    )
    repeated = assessment_service.assess(
        contract.coverage_contract_id,
        assessed_at=NOW,
    )

    snapshot = assessment.snapshot
    assert repeated.snapshot == snapshot
    assert snapshot.required_count == 6
    assert snapshot.satisfied_count == 1
    assert snapshot.gap_count == 1
    assert snapshot.unavailable_count == 1
    assert snapshot.stale_count == 1
    assert snapshot.unknown_count == 1
    assert snapshot.unmeasured_count == 1
    assert snapshot.coverage_ratio == pytest.approx(1 / 6)
    assert snapshot.coverage_confidence == pytest.approx(4 / 6)

    statuses = {item.status for item in assessment.requirement_results}
    assert statuses == {
        "SATISFIED",
        "GAP",
        "UNAVAILABLE",
        "STALE",
        "UNKNOWN",
        "UNMEASURED",
    }
    assert len(assessment.requirement_results) == 6
    assert all(item.explanation.strip() for item in assessment.requirement_results)

    measurable_with_evidence = {
        item.status: item
        for item in assessment.requirement_results
        if item.status in {"SATISFIED", "GAP", "UNAVAILABLE", "STALE"}
    }
    assert all(item.evidence_refs for item in measurable_with_evidence.values())
    assert snapshot.coverage_confidence > snapshot.coverage_ratio


def test_multiple_successful_sources_in_one_class_do_not_inflate_coverage_units(tmp_path):
    runtime = _runtime(tmp_path)
    LiveSourceCollector(
        runtime,
        [
            _success_adapter("official-a", "Official A", "Official sources"),
            _success_adapter("official-b", "Official B", "Official sources"),
            _success_adapter("official-c", "Official C", "Official sources"),
        ],
    ).collect("watch-coverage", NOW)

    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key="GLOBAL:source-class-unit",
        name="Source class unit acceptance",
        watch_id="watch-coverage",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=900,
        requirements=(CoverageRequirementSpec("SOURCE_CLASS", "Official sources"),),
        created_at=NOW - timedelta(hours=1),
    )

    assessment = OperationalCoverageAssessmentService(runtime).assess(
        contract.coverage_contract_id,
        assessed_at=NOW,
    )

    assert assessment.snapshot.required_count == 1
    assert assessment.snapshot.satisfied_count == 1
    assert assessment.snapshot.coverage_ratio == 1.0
    assert assessment.snapshot.coverage_confidence == 1.0
    assert len(assessment.requirement_results) == 1
    assert assessment.requirement_results[0].status == "SATISFIED"
