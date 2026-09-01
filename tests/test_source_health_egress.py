from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from kgeopolitical_monitor.live_sources import (
    LiveSourceIngestionStore,
    LiveSourceItem,
    SourceCollectionAuditStore,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_health_egress import (
    SourceHealthEgressService,
    classify_attempt_error,
    install_phase12_health_probe_governance,
)
from kgeopolitical_monitor.source_portfolio import SourcePortfolioService


NOW = datetime(2026, 9, 1, 17, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "P12.5 health watch",
        "Ukraine",
        60,
        watch_id="watch-p125",
        created_at=NOW,
    )
    install_phase12_health_probe_governance(runtime, reviewed_at=NOW)
    return runtime


def _adapter(record):
    return SimpleNamespace(
        source_id=record.source_id,
        source_name=record.source_name,
        source_class=record.source_class,
    )


def _record_attempt(runtime, record, *, at, status="SUCCESS", item_count=0, error=None, collection_id="c1"):
    audit = SourceCollectionAuditStore(runtime.database_path)
    audit.start(collection_id, "watch-p125", at)
    return audit.record_source_attempt(
        collection_id,
        _adapter(record),
        status=status,
        item_count=item_count,
        attempted_at=at,
        error=error,
    )


def _persist_item(runtime, record, *, collection_id, collected_at, published_at_raw):
    LiveSourceIngestionStore(runtime.database_path).persist(
        collection_id,
        [
            LiveSourceItem(
                item_id=f"item-{record.source_id}-{int(collected_at.timestamp())}",
                source_id=record.source_id,
                source_name=record.source_name,
                source_class=record.source_class,
                title="Fixture source item",
                summary="Fixture source content",
                original_url=f"https://example.test/{record.source_id}",
                collected_at=collected_at,
                metadata={"published_at_raw": published_at_raw},
                reliability="fixture",
            )
        ],
    )


def test_phase12_health_probe_governance_has_ten_exact_public_paths(tmp_path):
    runtime = _runtime(tmp_path)
    records = SourcePortfolioService(runtime).current_entries()
    assert len(records) == 10
    assert all(record.review_status == "APPROVED" for record in records)
    assert all(record.access_mode == "PUBLIC_ANONYMOUS" for record in records)
    assert all(record.cost_mode == "FREE" for record in records)
    assert all(record.authentication_mode == "NONE" for record in records)
    assert all(record.outbound_protocols == ("HTTPS",) for record in records)
    assert all(record.paid_provider_approved is False for record in records)


def test_egress_inventory_is_exact_and_deduplicated_by_snapshot_properties(tmp_path):
    runtime = _runtime(tmp_path)
    snapshot = SourceHealthEgressService(runtime).snapshot(assessed_at=NOW)

    assert len(snapshot.egress_entries) == 10
    assert len(snapshot.unique_outbound_hosts) == 10
    assert snapshot.unique_outbound_protocols == ("HTTPS",)
    assert "www.europarl.europa.eu" in snapshot.unique_outbound_hosts
    assert "api.gdeltproject.org" in snapshot.unique_outbound_hosts
    assert "meduza.io" in snapshot.unique_outbound_hosts
    assert all(entry.changes_verification_state is False for entry in snapshot.egress_entries)


def test_sources_without_attempts_remain_unmeasured_not_inferred(tmp_path):
    runtime = _runtime(tmp_path)
    snapshot = SourceHealthEgressService(runtime).snapshot(assessed_at=NOW)

    assert snapshot.measured_source_count == 0
    assert snapshot.unmeasured_source_count == 10
    assert {a.operational_state for a in snapshot.assessments} == {"UNMEASURED"}
    assert {a.measurement_freshness for a in snapshot.assessments} == {"UNMEASURED"}
    assert {a.content_freshness for a in snapshot.assessments} == {"UNKNOWN"}


def test_successful_current_attempt_and_recent_publisher_timestamp_are_separate_dimensions(tmp_path):
    runtime = _runtime(tmp_path)
    record = SourcePortfolioService(runtime).current("consilium-press-releases")
    assert record is not None
    at = NOW - timedelta(minutes=5)
    _record_attempt(runtime, record, at=at, status="SUCCESS", item_count=1, collection_id="current-success")
    _persist_item(
        runtime,
        record,
        collection_id="current-success",
        collected_at=at,
        published_at_raw="Tue, 01 Sep 2026 16:50:00 GMT",
    )

    assessment = SourceHealthEgressService(runtime).assess_source(record, assessed_at=NOW)
    assert assessment.operational_state == "HEALTHY"
    assert assessment.measurement_freshness == "CURRENT"
    assert assessment.content_freshness == "FRESH"
    assert assessment.content_timestamp_basis == "published_at_raw"
    assert assessment.last_attempt_status == "SUCCESS"
    assert assessment.error_class == "NONE"
    assert assessment.changes_claim_truth is False
    assert assessment.changes_verification_state is False
    assert assessment.establishes_independence is False
    assert assessment.changes_coverage_confidence is False


def test_old_successful_measurement_is_stale_without_becoming_transport_failure(tmp_path):
    runtime = _runtime(tmp_path)
    record = SourcePortfolioService(runtime).current("gdelt-doc-2")
    assert record is not None
    old = NOW - timedelta(minutes=181)
    _record_attempt(runtime, record, at=old, status="SUCCESS", item_count=1, collection_id="old-success")
    _persist_item(
        runtime,
        record,
        collection_id="old-success",
        collected_at=old,
        published_at_raw="2026-09-01T13:00:00Z",
    )

    assessment = SourceHealthEgressService(runtime).assess_source(record, assessed_at=NOW)
    assert assessment.operational_state == "STALE"
    assert assessment.measurement_freshness == "STALE"
    assert assessment.last_attempt_status == "SUCCESS"
    assert assessment.error_class == "NONE"
    assert assessment.content_freshness == "STALE"


def test_failed_current_parser_attempt_is_unavailable_with_distinct_error_class(tmp_path):
    runtime = _runtime(tmp_path)
    record = SourcePortfolioService(runtime).current("eu-parliament-press-releases")
    assert record is not None
    _record_attempt(
        runtime,
        record,
        at=NOW - timedelta(minutes=1),
        status="FAILED",
        item_count=0,
        error="P12.2 feed payload is not valid XML",
        collection_id="parser-failure",
    )

    assessment = SourceHealthEgressService(runtime).assess_source(record, assessed_at=NOW)
    assert assessment.portfolio_availability_state == "DEGRADED"
    assert assessment.operational_state == "UNAVAILABLE"
    assert assessment.measurement_freshness == "CURRENT"
    assert assessment.content_freshness == "UNKNOWN"
    assert assessment.error_class == "PARSER"


def test_degraded_portfolio_with_successful_current_probe_remains_degraded(tmp_path):
    runtime = _runtime(tmp_path)
    record = SourcePortfolioService(runtime).current("eu-parliament-press-releases")
    assert record is not None
    _record_attempt(
        runtime,
        record,
        at=NOW,
        status="SUCCESS",
        item_count=0,
        collection_id="degraded-success",
    )

    assessment = SourceHealthEgressService(runtime).assess_source(record, assessed_at=NOW)
    assert assessment.portfolio_availability_state == "DEGRADED"
    assert assessment.operational_state == "DEGRADED"
    assert assessment.measurement_freshness == "CURRENT"


def test_error_classes_do_not_conflate_transport_parser_and_governance():
    assert classify_attempt_error(None) == "NONE"
    assert classify_attempt_error("live source network error: reset") == "TRANSPORT"
    assert classify_attempt_error("feed payload is not valid XML") == "PARSER"
    assert classify_attempt_error("portfolio adapter identity/version mismatch") == "GOVERNANCE"
    assert classify_attempt_error("unexpected fixture issue") == "UNKNOWN"
