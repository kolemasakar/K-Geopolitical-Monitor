from datetime import datetime, timedelta, timezone

from kgeopolitical_monitor.coverage_source_availability import (
    SourceAvailabilityCoverageEvaluator,
)
from kgeopolitical_monitor.live_sources import LiveSourceCollector
from kgeopolitical_monitor.operational_coverage import (
    CoverageRequirementSpec,
    OperationalCoverageService,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


NOW = datetime(2026, 8, 26, 14, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-a",
        created_at=NOW - timedelta(hours=4),
    )
    runtime.create_watch(
        "Other watch",
        "Other",
        60,
        watch_id="watch-b",
        created_at=NOW - timedelta(hours=4),
    )
    return runtime


def _contract(runtime, source_id, *, window=3600, freshness=900, watch_id="watch-a"):
    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key=f"SOURCE:{source_id}:{watch_id}",
        name=f"Availability for {source_id}",
        watch_id=watch_id,
        assessment_window_seconds=window,
        freshness_requirement_seconds=freshness,
        requirements=(CoverageRequirementSpec("SOURCE_ID", source_id),),
        created_at=NOW - timedelta(hours=3),
    )
    requirement = coverage.requirements(contract.coverage_contract_id)[0]
    return coverage, contract, requirement


def test_fresh_zero_item_success_is_satisfied(tmp_path):
    runtime = _runtime(tmp_path)

    class EmptyAdapter:
        source_id = "source-zero"
        source_name = "Zero Result Source"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return []

    collector = LiveSourceCollector(runtime, [EmptyAdapter()])
    collection = collector.collect("watch-a", NOW)
    coverage, contract, requirement = _contract(runtime, "source-zero")
    evaluator = SourceAvailabilityCoverageEvaluator(runtime, coverage)

    result = evaluator.evaluate_requirement(
        contract.coverage_contract_id,
        requirement.requirement_id,
        assessed_at=NOW,
    )
    snapshot = coverage.create_snapshot(
        contract.coverage_contract_id,
        (result,),
        assessed_at=NOW,
    )

    assert result.status == "SATISFIED"
    assert f"collection:{collection.collection_id}" in result.evidence_refs
    assert "zero-item" in result.explanation.lower()
    assert snapshot.satisfied_count == 1
    assert snapshot.coverage_ratio == 1.0
    assert snapshot.coverage_confidence == 1.0


def test_fresh_failed_source_is_unavailable(tmp_path):
    runtime = _runtime(tmp_path)

    class FailingAdapter:
        source_id = "source-fail"
        source_name = "Failing Source"
        source_class = "Structured data"

        def fetch(self, watch, collected_at):
            raise RuntimeError("provider unavailable")

    collector = LiveSourceCollector(runtime, [FailingAdapter()])
    collection = collector.collect("watch-a", NOW)
    coverage, contract, requirement = _contract(runtime, "source-fail")
    evaluator = SourceAvailabilityCoverageEvaluator(runtime, coverage)

    result = evaluator.evaluate_requirement(
        contract.coverage_contract_id,
        requirement.requirement_id,
        assessed_at=NOW,
    )

    assert collection.status == "FAILED"
    assert result.status == "UNAVAILABLE"
    assert "provider unavailable" in result.explanation
    assert result.measured_at == NOW


def test_in_window_but_not_fresh_source_attempt_is_stale(tmp_path):
    runtime = _runtime(tmp_path)
    attempt_time = NOW - timedelta(minutes=30)

    class StableAdapter:
        source_id = "source-stale"
        source_name = "Stale Source"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return []

    collector = LiveSourceCollector(runtime, [StableAdapter()])
    collection = collector.collect("watch-a", attempt_time)
    coverage, contract, requirement = _contract(
        runtime,
        "source-stale",
        window=3600,
        freshness=900,
    )
    evaluator = SourceAvailabilityCoverageEvaluator(runtime, coverage)

    result = evaluator.evaluate_requirement(
        contract.coverage_contract_id,
        requirement.requirement_id,
        assessed_at=NOW,
    )

    assert collection.status == "COMPLETED"
    assert result.status == "STALE"
    assert result.measured_at == attempt_time
    assert "older than the 900s freshness requirement" in result.explanation


def test_no_source_attempt_in_assessment_window_is_unknown(tmp_path):
    runtime = _runtime(tmp_path)
    old_time = NOW - timedelta(hours=2)

    class OldAdapter:
        source_id = "source-old"
        source_name = "Old Source"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return []

    collector = LiveSourceCollector(runtime, [OldAdapter()])
    collector.collect("watch-a", old_time)
    coverage, contract, requirement = _contract(
        runtime,
        "source-old",
        window=3600,
        freshness=900,
    )
    evaluator = SourceAvailabilityCoverageEvaluator(runtime, coverage)

    result = evaluator.evaluate_requirement(
        contract.coverage_contract_id,
        requirement.requirement_id,
        assessed_at=NOW,
    )

    assert result.status == "UNKNOWN"
    assert result.evidence_refs == ("source:source-old",)
    assert result.measured_at == NOW


def test_watch_scoped_source_attempt_does_not_leak_between_watches(tmp_path):
    runtime = _runtime(tmp_path)

    class SharedAdapter:
        source_id = "source-shared"
        source_name = "Shared Source"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return []

    collector = LiveSourceCollector(runtime, [SharedAdapter()])
    collector.collect("watch-b", NOW)
    coverage, contract, requirement = _contract(
        runtime,
        "source-shared",
        watch_id="watch-a",
    )
    evaluator = SourceAvailabilityCoverageEvaluator(runtime, coverage)

    result = evaluator.evaluate_requirement(
        contract.coverage_contract_id,
        requirement.requirement_id,
        assessed_at=NOW,
    )

    assert result.status == "UNKNOWN"
