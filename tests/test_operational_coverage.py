from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.operational_coverage import (
    CoverageRequirementResultDraft,
    CoverageRequirementSpec,
    OperationalCoverageService,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    root = tmp_path / "project"
    root.mkdir(exist_ok=True)
    runtime = OperationalMonitoringRuntime(root)
    if runtime.repository.get_watch("watch-global") is None:
        runtime.create_watch(
            "Global watch",
            "Ukraine",
            30,
            watch_id="watch-global",
            created_at=NOW,
        )
    return runtime


def _base_specs():
    return (
        CoverageRequirementSpec(
            "SOURCE_CLASS",
            "Official sources",
            parameters={"minimum_observed": 1},
        ),
        CoverageRequirementSpec(
            "ACTOR",
            "ukraine-government",
            parameters={"reason": "declared but not yet canonically measurable"},
        ),
    )


def test_contract_identity_is_deterministic_and_material_change_versions_definition(
    tmp_path,
):
    runtime = _runtime(tmp_path)
    service = OperationalCoverageService(runtime)

    first = service.create_contract(
        scope_key="GLOBAL",
        name="Global operational coverage",
        watch_id="watch-global",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=1800,
        requirements=_base_specs(),
        created_at=NOW,
    )
    repeated = service.create_contract(
        scope_key="GLOBAL",
        name="Global operational coverage",
        watch_id="watch-global",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=1800,
        requirements=tuple(reversed(_base_specs())),
        created_at=NOW,
    )

    assert repeated.coverage_contract_id == first.coverage_contract_id
    assert {
        item.requirement_id for item in service.requirements(first.coverage_contract_id)
    } == {
        item.requirement_id
        for item in service.requirements(repeated.coverage_contract_id)
    }

    changed = service.create_contract(
        scope_key="GLOBAL",
        name="Global operational coverage",
        watch_id="watch-global",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=1800,
        requirements=(
            *_base_specs(),
            CoverageRequirementSpec("FRESHNESS", "watch-global"),
        ),
        created_at=NOW,
    )

    assert changed.coverage_contract_id != first.coverage_contract_id
    assert len(service.requirements(first.coverage_contract_id)) == 2
    assert len(service.requirements(changed.coverage_contract_id)) == 3


def test_contract_requires_known_watch_valid_dimension_and_required_unit(tmp_path):
    runtime = _runtime(tmp_path)
    service = OperationalCoverageService(runtime)

    with pytest.raises(ValueError, match="watch does not exist"):
        service.create_contract(
            scope_key="GLOBAL",
            name="Invalid watch",
            watch_id="missing-watch",
            assessment_window_seconds=3600,
            freshness_requirement_seconds=1800,
            requirements=(CoverageRequirementSpec("SOURCE_CLASS", "Official sources"),),
            created_at=NOW,
        )

    with pytest.raises(ValueError, match="unsupported coverage dimension"):
        service.create_contract(
            scope_key="GLOBAL",
            name="Invalid dimension",
            watch_id="watch-global",
            assessment_window_seconds=3600,
            freshness_requirement_seconds=1800,
            requirements=(CoverageRequirementSpec("SOURCE_COUNT", "many"),),
            created_at=NOW,
        )

    with pytest.raises(ValueError, match="at least one required unit"):
        service.create_contract(
            scope_key="GLOBAL",
            name="Optional only",
            watch_id="watch-global",
            assessment_window_seconds=3600,
            freshness_requirement_seconds=1800,
            requirements=(
                CoverageRequirementSpec(
                    "SOURCE_CLASS",
                    "Official sources",
                    required=False,
                ),
            ),
            created_at=NOW,
        )


def test_snapshot_metrics_are_deterministic_immutable_and_restart_safe(tmp_path):
    runtime = _runtime(tmp_path)
    service = OperationalCoverageService(runtime)
    contract = service.create_contract(
        scope_key="GLOBAL",
        name="Global operational coverage",
        watch_id="watch-global",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=1800,
        requirements=_base_specs(),
        created_at=NOW,
    )
    requirements = {
        item.dimension: item
        for item in service.requirements(contract.coverage_contract_id)
    }
    results = (
        CoverageRequirementResultDraft(
            requirement_id=requirements["SOURCE_CLASS"].requirement_id,
            status="SATISFIED",
            evidence_refs=("source:consilium-press-releases",),
            explanation="Required official source class is represented.",
            measured_at=NOW,
        ),
        CoverageRequirementResultDraft(
            requirement_id=requirements["ACTOR"].requirement_id,
            status="UNMEASURED",
            evidence_refs=(),
            explanation="No canonical actor coverage domain exists in this baseline.",
            measured_at=NOW,
        ),
    )

    snapshot = service.create_snapshot(
        contract.coverage_contract_id,
        results,
        assessed_at=NOW,
    )
    repeated = service.create_snapshot(
        contract.coverage_contract_id,
        tuple(reversed(results)),
        assessed_at=NOW,
    )

    assert repeated.coverage_snapshot_id == snapshot.coverage_snapshot_id
    assert snapshot.required_count == 2
    assert snapshot.satisfied_count == 1
    assert snapshot.unmeasured_count == 1
    assert snapshot.gap_count == 0
    assert snapshot.unavailable_count == 0
    assert snapshot.stale_count == 0
    assert snapshot.unknown_count == 0
    assert snapshot.coverage_ratio == 0.5
    assert snapshot.coverage_confidence == 0.5
    assert snapshot.limitations == ("ACTOR:ukraine-government:UNMEASURED",)

    persisted_results = service.snapshot_results(snapshot.coverage_snapshot_id)
    assert {item.status for item in persisted_results} == {
        "SATISFIED",
        "UNMEASURED",
    }

    changed_results = (
        results[0],
        CoverageRequirementResultDraft(
            requirement_id=requirements["ACTOR"].requirement_id,
            status="GAP",
            evidence_refs=(),
            explanation="Conflicting reinterpretation must not rewrite the snapshot.",
            measured_at=NOW,
        ),
    )
    with pytest.raises(ValueError, match="immutable"):
        service.create_snapshot(
            contract.coverage_contract_id,
            changed_results,
            assessed_at=NOW,
        )

    restarted = OperationalMonitoringRuntime(tmp_path / "project")
    restarted_service = OperationalCoverageService(restarted)
    restored_contract = restarted_service.get_contract(contract.coverage_contract_id)
    restored_snapshot = restarted_service.get_snapshot(snapshot.coverage_snapshot_id)

    assert restored_contract == contract
    assert restored_snapshot == snapshot
    assert restarted_service.snapshot_history(contract.coverage_contract_id) == (
        snapshot,
    )

    with sqlite3.connect(restarted.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                """
                UPDATE operational_coverage_snapshots
                SET coverage_ratio = 1.0
                WHERE coverage_snapshot_id = ?
                """,
                (snapshot.coverage_snapshot_id,),
            )


def test_snapshot_requires_exact_contract_requirement_set(tmp_path):
    runtime = _runtime(tmp_path)
    service = OperationalCoverageService(runtime)
    first = service.create_contract(
        scope_key="GLOBAL-A",
        name="Coverage A",
        watch_id="watch-global",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=1800,
        requirements=(CoverageRequirementSpec("SOURCE_CLASS", "Official sources"),),
        created_at=NOW,
    )
    second = service.create_contract(
        scope_key="GLOBAL-B",
        name="Coverage B",
        watch_id="watch-global",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=1800,
        requirements=(CoverageRequirementSpec("SOURCE_CLASS", "Regional media"),),
        created_at=NOW,
    )
    first_requirement = service.requirements(first.coverage_contract_id)[0]
    second_requirement = service.requirements(second.coverage_contract_id)[0]

    with pytest.raises(ValueError, match="every contract requirement"):
        service.create_snapshot(
            first.coverage_contract_id,
            (),
            assessed_at=NOW,
        )

    with pytest.raises(ValueError, match="does not belong to contract"):
        service.create_snapshot(
            first.coverage_contract_id,
            (
                CoverageRequirementResultDraft(
                    requirement_id=second_requirement.requirement_id,
                    status="UNKNOWN",
                    evidence_refs=(),
                    explanation="Wrong contract.",
                    measured_at=NOW,
                ),
            ),
            assessed_at=NOW,
        )

    snapshot = service.create_snapshot(
        first.coverage_contract_id,
        (
            CoverageRequirementResultDraft(
                requirement_id=first_requirement.requirement_id,
                status="UNKNOWN",
                evidence_refs=(),
                explanation="No assessment evidence exists yet.",
                measured_at=NOW,
            ),
        ),
        assessed_at=NOW,
    )
    assert snapshot.coverage_ratio == 0.0
    assert snapshot.coverage_confidence == 0.0
    assert snapshot.unknown_count == 1
