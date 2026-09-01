import sqlite3
from datetime import datetime, timezone

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_portfolio import SourcePortfolioService


NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def _service(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path)
    service = SourcePortfolioService(runtime)
    service.register_source_identity(
        "example-official",
        source_name="Example Official Source",
        source_class="Official sources",
        reliability="unassessed",
    )
    return runtime, service


def _record(service, **overrides):
    values = {
        "source_name": "Example Official Source",
        "publisher_name": "Example Government",
        "source_class": "Official sources",
        "source_role": "OFFICIAL",
        "region_scope": ("EUROPE", "GLOBAL"),
        "language_scope": ("en",),
        "access_mode": "PUBLIC_ANONYMOUS",
        "cost_mode": "FREE",
        "authentication_mode": "NONE",
        "expected_freshness_minutes": 120,
        "collection_cadence_minutes": 30,
        "adapter_id": "example-rss",
        "adapter_version": "1.0",
        "outbound_domains": ("news.example.gov",),
        "outbound_protocols": ("HTTPS",),
        "fallback_source_ids": (),
        "availability_state": "ACTIVE",
        "data_classification": "PUBLIC",
        "origin_characteristics": "Official publisher; may contain first-party statements.",
        "independence_constraints": (
            "Official statements prove what the actor said, not automatically the "
            "underlying event claim."
        ),
        "terms_notes": "Public read-only feed.",
        "owner": "KGM",
        "reviewer": "owner",
        "review_status": "APPROVED",
        "reviewed_at": NOW,
        "created_at": NOW,
    }
    values.update(overrides)
    return service.record_version("example-official", **values)


def test_source_identity_registration_is_idempotent_and_fail_closed(tmp_path):
    _, service = _service(tmp_path)

    service.register_source_identity(
        "example-official",
        source_name="Example Official Source",
        source_class="Official sources",
    )

    with pytest.raises(ValueError, match="conflicts"):
        service.register_source_identity(
            "example-official",
            source_name="Different Name",
            source_class="Official sources",
        )

    with pytest.raises(ValueError, match="unsupported source_class"):
        service.register_source_identity(
            "bad-source",
            source_name="Bad",
            source_class="Unapproved class",
        )


def test_source_portfolio_versioning_current_and_history(tmp_path):
    _, service = _service(tmp_path)

    first = _record(service)
    second = _record(
        service,
        expected_freshness_minutes=60,
        collection_cadence_minutes=15,
        reviewed_at=datetime(2026, 9, 1, 13, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 9, 1, 13, 0, tzinfo=timezone.utc),
    )

    assert first.portfolio_version == 1
    assert first.supersedes_entry_id is None
    assert second.portfolio_version == 2
    assert second.supersedes_entry_id == first.portfolio_entry_id
    assert service.current("example-official") == second
    assert service.history("example-official") == (first, second)


def test_source_portfolio_normalizes_multi_value_fields_deterministically(tmp_path):
    _, service = _service(tmp_path)

    record = _record(
        service,
        region_scope=("GLOBAL", "EUROPE", "GLOBAL"),
        language_scope=("en", "uk", "en"),
        outbound_domains=("NEWS.EXAMPLE.GOV", "news.example.gov"),
        outbound_protocols=("https", "HTTPS"),
        fallback_source_ids=("fallback-b", "fallback-a", "fallback-b"),
    )

    assert record.region_scope == ("EUROPE", "GLOBAL")
    assert record.language_scope == ("en", "uk")
    assert record.outbound_domains == ("news.example.gov",)
    assert record.outbound_protocols == ("HTTPS",)
    assert record.fallback_source_ids == ("fallback-a", "fallback-b")


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {"access_mode": "PUBLIC_ANONYMOUS", "authentication_mode": "API_KEY"},
            "PUBLIC_ANONYMOUS",
        ),
        (
            {"access_mode": "PUBLIC_CREDENTIALED", "authentication_mode": "NONE"},
            "requires explicit authentication",
        ),
        (
            {"outbound_domains": ("https://news.example.gov/feed",)},
            "exact hostnames",
        ),
        (
            {"outbound_protocols": ("HTTP",)},
            "unsupported outbound protocol",
        ),
        (
            {"fallback_source_ids": ("example-official",)},
            "own fallback",
        ),
        (
            {"review_status": "PLANNED", "availability_state": "ACTIVE"},
            "operational availability",
        ),
        (
            {"data_classification": "SENSITIVE"},
            "restricted/sensitive",
        ),
        (
            {"adapter_id": "NOT_ASSIGNED"},
            "requires assigned adapter",
        ),
    ],
)
def test_source_portfolio_fail_closed_validation(tmp_path, overrides, message):
    _, service = _service(tmp_path)
    with pytest.raises(ValueError, match=message):
        _record(service, **overrides)


def test_paid_source_cannot_be_approved_without_separate_paid_provider_approval(tmp_path):
    _, service = _service(tmp_path)

    with pytest.raises(ValueError, match="separate paid-provider approval"):
        _record(service, cost_mode="PAID")

    approved = _record(
        service,
        cost_mode="PAID",
        paid_provider_approved=True,
    )
    assert approved.cost_mode == "PAID"
    assert approved.paid_provider_approved is True


def test_planned_paid_source_can_be_documented_without_activation(tmp_path):
    _, service = _service(tmp_path)

    planned = _record(
        service,
        cost_mode="PAID",
        review_status="PLANNED",
        availability_state="PLANNED",
        adapter_id="NOT_ASSIGNED",
        adapter_version="NOT_ASSIGNED",
    )

    assert planned.review_status == "PLANNED"
    assert planned.availability_state == "PLANNED"
    assert planned.paid_provider_approved is False
    assert planned.activates_collection is False


def test_portfolio_metadata_cannot_promote_truth_independence_or_coverage(tmp_path):
    _, service = _service(tmp_path)
    record = _record(service)

    assert record.activates_collection is False
    assert record.establishes_independence is False
    assert record.changes_claim_truth is False
    assert record.changes_verification_state is False
    assert record.changes_coverage_confidence is False


def test_source_portfolio_rows_are_sql_immutable(tmp_path):
    runtime, service = _service(tmp_path)
    record = _record(service)

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                """
                UPDATE source_portfolio_versions
                SET publisher_name = 'Tampered'
                WHERE portfolio_entry_id = ?
                """,
                (record.portfolio_entry_id,),
            )

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "DELETE FROM source_portfolio_versions WHERE portfolio_entry_id = ?",
                (record.portfolio_entry_id,),
            )


def test_current_entries_returns_latest_version_per_source(tmp_path):
    runtime, service = _service(tmp_path)
    _record(service)
    latest = _record(
        service,
        expected_freshness_minutes=30,
        reviewed_at=datetime(2026, 9, 1, 14, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 9, 1, 14, 0, tzinfo=timezone.utc),
    )

    second = SourcePortfolioService(runtime)
    second.register_source_identity(
        "example-media",
        source_name="Example Media",
        source_class="International media",
    )
    second_record = second.record_version(
        "example-media",
        source_name="Example Media",
        publisher_name="Example Media Group",
        source_class="International media",
        source_role="MEDIA",
        region_scope=("GLOBAL",),
        language_scope=("en",),
        access_mode="PUBLIC_ANONYMOUS",
        cost_mode="FREE",
        authentication_mode="NONE",
        expected_freshness_minutes=60,
        collection_cadence_minutes=30,
        adapter_id="example-json",
        adapter_version="1.0",
        outbound_domains=("api.example.media",),
        availability_state="ACTIVE",
        data_classification="PUBLIC",
        origin_characteristics="Publisher may contain original and cited reporting.",
        independence_constraints="Underlying origin must be assessed per item.",
        owner="KGM",
        reviewer="owner",
        review_status="APPROVED",
        reviewed_at=NOW,
        created_at=NOW,
    )

    assert service.current_entries() == (second_record, latest)
