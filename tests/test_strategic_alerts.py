import sqlite3
from datetime import datetime, timedelta, timezone

from kgeopolitical_monitor.live_end_to_end import (
    DETECTED,
    PARTLY_VERIFIED,
    LiveEndToEndProcessor,
)
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.strategic_alerts import (
    CRITICAL,
    HIGH,
    INVALIDATED,
    NORMAL,
    OPEN,
    UPDATED,
    StrategicAlertService,
)


NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


class StaticAdapter:
    def __init__(self, source_id, source_name, source_class, reliability, items):
        self.source_id = source_id
        self.source_name = source_name
        self.source_class = source_class
        self.reliability = reliability
        self._items = items

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=item["item_id"],
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title=item["title"],
                summary=item.get("summary", item["title"]),
                original_url=item["url"],
                collected_at=collected_at,
                metadata=item.get("metadata", {}),
                reliability=self.reliability,
            )
            for item in self._items
        ]


def _runtime(tmp_path, watch_id="watch-alert"):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Ukraine strategic alert",
        "Ukraine",
        60,
        watch_id=watch_id,
        created_at=NOW,
    )
    return runtime


def _m8_finding(runtime, *, suffix, origins=2, processed_at=NOW):
    adapters = [
        StaticAdapter(
            f"official-{suffix}",
            f"Official {suffix}",
            "Official sources",
            "official",
            [
                {
                    "item_id": f"official-{suffix}",
                    "title": "Ukraine security agreement",
                    "url": f"https://official.example/{suffix}",
                }
            ],
        )
    ]
    if origins >= 2:
        adapters.append(
            StaticAdapter(
                f"media-{suffix}",
                f"Media {suffix}",
                "International media",
                "medium",
                [
                    {
                        "item_id": f"media-{suffix}",
                        "title": "Ukraine: security agreement",
                        "url": f"https://media.example/{suffix}",
                    }
                ],
            )
        )

    collection = LiveSourceCollector(runtime, adapters).collect("watch-alert", processed_at)
    result = LiveEndToEndProcessor(runtime).process_collection(
        collection.collection_id,
        processed_at=processed_at,
    )
    assert len(result.findings) == 1
    return result.claims[0], result.findings[0]


def test_qualifying_m8_finding_creates_traceable_high_alert(tmp_path):
    runtime = _runtime(tmp_path)
    claim, finding = _m8_finding(runtime, suffix="a", origins=2)
    assert claim.verification_status == PARTLY_VERIFIED

    service = StrategicAlertService(runtime)
    service.configure_watch(
        "watch-alert",
        priority=HIGH,
        minimum_importance=0.5,
        minimum_confidence=0.8,
        minimum_verification_rank=1,
        configured_at=NOW,
    )

    alert = service.evaluate_finding(finding.finding_id, evaluated_at=NOW)

    assert alert is not None
    assert alert.status == OPEN
    assert alert.priority == HIGH
    assert alert.finding_id == finding.finding_id
    assert alert.evidence_refs == finding.evidence_refs
    assert "verification_status=PARTLY_VERIFIED" in alert.explanation
    assert "priority affects alert handling only" in alert.explanation
    history = service.event_history(alert.alert_id)
    assert [event.status for event in history] == [OPEN]


def test_detected_finding_fails_partly_verified_policy(tmp_path):
    runtime = _runtime(tmp_path)
    claim, finding = _m8_finding(runtime, suffix="single", origins=1)
    assert claim.verification_status == DETECTED

    service = StrategicAlertService(runtime)
    service.configure_watch(
        "watch-alert",
        minimum_importance=0.5,
        minimum_confidence=0.5,
        minimum_verification_rank=1,
        configured_at=NOW,
    )

    assert service.evaluate_finding(finding.finding_id, evaluated_at=NOW) is None
    with sqlite3.connect(runtime.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM strategic_alerts").fetchone()[0] == 0


def test_repeated_same_finding_is_idempotent(tmp_path):
    runtime = _runtime(tmp_path)
    _, finding = _m8_finding(runtime, suffix="idempotent", origins=2)
    service = StrategicAlertService(runtime)
    service.configure_watch("watch-alert", configured_at=NOW)

    first = service.evaluate_finding(finding.finding_id, evaluated_at=NOW)
    second = service.evaluate_finding(finding.finding_id, evaluated_at=NOW)

    assert first is not None and second is not None
    assert second.alert_id == first.alert_id
    assert second.status == OPEN
    assert len(service.event_history(first.alert_id)) == 1

    with sqlite3.connect(runtime.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM strategic_alerts").fetchone()[0] == 1


def test_new_cycle_same_title_updates_existing_alert(tmp_path):
    runtime = _runtime(tmp_path)
    _, first_finding = _m8_finding(runtime, suffix="cycle-a", origins=2, processed_at=NOW)
    service = StrategicAlertService(runtime)
    service.configure_watch("watch-alert", priority=HIGH, configured_at=NOW)
    first_alert = service.evaluate_finding(first_finding.finding_id, evaluated_at=NOW)
    assert first_alert is not None

    later = NOW + timedelta(hours=1)
    _, second_finding = _m8_finding(
        runtime,
        suffix="cycle-b",
        origins=2,
        processed_at=later,
    )
    second_alert = service.evaluate_finding(second_finding.finding_id, evaluated_at=later)

    assert second_alert is not None
    assert second_alert.alert_id == first_alert.alert_id
    assert second_alert.finding_id == second_finding.finding_id
    assert second_alert.status == UPDATED
    history = service.event_history(first_alert.alert_id)
    assert [event.status for event in history] == [OPEN, UPDATED]
    assert history[-1].payload["previous_finding_id"] == first_finding.finding_id
    assert history[-1].payload["finding_id"] == second_finding.finding_id


def test_invalidation_is_persistent_idempotent_and_does_not_auto_reopen(tmp_path):
    runtime = _runtime(tmp_path)
    _, finding = _m8_finding(runtime, suffix="invalidate", origins=2)
    service = StrategicAlertService(runtime)
    service.configure_watch("watch-alert", configured_at=NOW)
    opened = service.evaluate_finding(finding.finding_id, evaluated_at=NOW)
    assert opened is not None

    invalidated_at = NOW + timedelta(minutes=5)
    first = service.invalidate(
        opened.alert_id,
        "supporting claim retracted",
        invalidated_at=invalidated_at,
    )
    second = service.invalidate(
        opened.alert_id,
        "supporting claim retracted",
        invalidated_at=invalidated_at,
    )
    reevaluated = service.evaluate_finding(
        finding.finding_id,
        evaluated_at=NOW + timedelta(minutes=10),
    )

    assert first.status == INVALIDATED
    assert second.status == INVALIDATED
    assert first.invalidation_reason == "supporting claim retracted"
    assert reevaluated is not None
    assert reevaluated.status == INVALIDATED
    history = service.event_history(opened.alert_id)
    assert [event.status for event in history] == [OPEN, INVALIDATED]


def test_priority_orders_due_watches_without_changing_evidence_semantics(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    for watch_id in ("watch-normal", "watch-critical", "watch-high"):
        runtime.create_watch(
            watch_id,
            "Ukraine",
            60,
            watch_id=watch_id,
            created_at=NOW,
        )

    service = StrategicAlertService(runtime)
    service.configure_watch("watch-normal", priority=NORMAL, configured_at=NOW)
    service.configure_watch("watch-critical", priority=CRITICAL, configured_at=NOW)
    service.configure_watch("watch-high", priority=HIGH, configured_at=NOW)

    due = service.prioritized_due_watches(NOW)

    assert [item.watch.watch_id for item in due] == [
        "watch-critical",
        "watch-high",
        "watch-normal",
    ]
    assert [item.priority for item in due] == [CRITICAL, HIGH, NORMAL]


def test_policy_requires_existing_watch_and_valid_thresholds(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    service = StrategicAlertService(runtime)

    try:
        service.configure_watch("missing", configured_at=NOW)
    except ValueError as exc:
        assert str(exc) == "watch does not exist"
    else:
        raise AssertionError("missing watch policy must fail")

    runtime.create_watch("watch", "Ukraine", 60, watch_id="watch", created_at=NOW)
    try:
        service.configure_watch("watch", minimum_confidence=1.1, configured_at=NOW)
    except ValueError as exc:
        assert "minimum_confidence" in str(exc)
    else:
        raise AssertionError("invalid confidence threshold must fail")


def test_alert_state_survives_runtime_restart(tmp_path):
    runtime = _runtime(tmp_path)
    _, finding = _m8_finding(runtime, suffix="restart", origins=2)
    service = StrategicAlertService(runtime)
    service.configure_watch("watch-alert", priority=HIGH, configured_at=NOW)
    opened = service.evaluate_finding(finding.finding_id, evaluated_at=NOW)
    assert opened is not None

    restarted_runtime = OperationalMonitoringRuntime(tmp_path / "project")
    restarted = StrategicAlertService(restarted_runtime)
    loaded = restarted.get_alert(opened.alert_id)

    assert loaded == opened
    assert restarted.get_policy("watch-alert") == service.get_policy("watch-alert")
    assert [event.status for event in restarted.event_history(opened.alert_id)] == [OPEN]
    assert restarted.database_path == runtime.database_path


def test_critical_priority_never_bypasses_watch_cadence(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Critical cadence",
        "Ukraine",
        60,
        watch_id="watch-critical",
        created_at=NOW,
    )
    service = StrategicAlertService(runtime)
    service.configure_watch("watch-critical", priority=CRITICAL, configured_at=NOW)

    run = runtime.start_run("watch-critical", run_id="cadence-run", started_at=NOW)
    runtime.complete_run(run.run_id, result_count=0, completed_at=NOW)

    assert service.prioritized_due_watches(NOW + timedelta(minutes=59)) == []
    due = service.prioritized_due_watches(NOW + timedelta(minutes=60))
    assert len(due) == 1
    assert due[0].watch.watch_id == "watch-critical"
    assert due[0].priority == CRITICAL
