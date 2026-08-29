from datetime import datetime, timezone
import sqlite3

from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.translation_foundation import (
    AMBIGUOUS,
    FAILED,
    SUCCESS,
    UNAVAILABLE,
    UNSUPPORTED,
    DeterministicTranslationAdapter,
    TranslationAdapterResult,
    TranslationService,
)


NOW = datetime(2026, 8, 29, 9, 0, tzinfo=timezone.utc)


class StaticAdapter:
    def __init__(self, source_id, url, summary="Оригінальний текст"):
        self.source_id = source_id
        self.source_name = source_id
        self.source_class = "Official sources"
        self.reliability = "official"
        self.url = url
        self.summary = summary

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=f"item-{self.source_id}",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Спільне повідомлення",
                summary=self.summary,
                original_url=self.url,
                collected_at=collected_at,
                reliability=self.reliability,
            )
        ]


class RaisingTranslationAdapter:
    method = "LOCAL_TEST_FAILURE"
    provider = None
    provider_version = "1"

    def translate(self, text, *, source_language, target_language):
        raise RuntimeError("translator crashed")


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Translation test",
        "translation",
        60,
        watch_id="watch-translation",
        created_at=NOW,
    )
    return runtime


def _collect_one(runtime):
    return LiveSourceCollector(
        runtime,
        [StaticAdapter("source-a", "https://publisher.example/story")],
    ).collect("watch-translation", NOW)


def test_translation_preserves_original_and_origin_and_versions_retranslation(tmp_path):
    runtime = _runtime(tmp_path)
    _collect_one(runtime)
    service = TranslationService(runtime)

    first = service.translate_raw_item(
        "item-source-a",
        "UK",
        "EN",
        DeterministicTranslationAdapter(
            {("uk", "en", "Оригінальний текст"): "Original text"}
        ),
        translated_at=NOW,
    )
    second = service.translate_raw_item(
        "item-source-a",
        "uk",
        "en",
        DeterministicTranslationAdapter(
            {("uk", "en", "Оригінальний текст"): "Updated translation"}
        ),
        translated_at=NOW,
    )

    assert first.status == SUCCESS
    assert first.original_text == "Оригінальний текст"
    assert first.translated_text == "Original text"
    assert first.translation_version == 1
    assert first.underlying_origin_id == "publisher.example"
    assert first.origin_kind == "ORIGIN_HOST"
    assert first.creates_independent_origin is False
    assert second.translation_version == 2
    assert service.latest("item-source-a", "en") == second
    assert service.history("item-source-a", target_language="en") == (first, second)

    with sqlite3.connect(runtime.database_path) as connection:
        raw = connection.execute(
            "SELECT title, content FROM raw_items WHERE id = 'item-source-a'"
        ).fetchone()
    assert raw == ("Спільне повідомлення", "Оригінальний текст")


def test_translation_degraded_and_ambiguous_states_are_persisted(tmp_path):
    runtime = _runtime(tmp_path)
    _collect_one(runtime)
    service = TranslationService(runtime)

    ambiguous = service.translate_raw_item(
        "item-source-a",
        "uk",
        "pl",
        DeterministicTranslationAdapter(
            {
                ("uk", "pl", "Оригінальний текст"): TranslationAdapterResult(
                    status=AMBIGUOUS,
                    translated_text="Tekst oryginalny",
                    uncertainty_note="term has two plausible renderings",
                )
            }
        ),
        translated_at=NOW,
    )
    unsupported = service.translate_raw_item(
        "item-source-a",
        "uk",
        "de",
        DeterministicTranslationAdapter(),
        translated_at=NOW,
    )
    unavailable = service.translate_raw_item(
        "item-source-a",
        "uk",
        "fr",
        DeterministicTranslationAdapter(
            {
                ("uk", "fr", "Оригінальний текст"): TranslationAdapterResult(
                    status=UNAVAILABLE,
                    error_message="provider is unavailable",
                )
            }
        ),
        translated_at=NOW,
    )
    failed = service.translate_raw_item(
        "item-source-a",
        "uk",
        "es",
        RaisingTranslationAdapter(),
        translated_at=NOW,
    )

    assert ambiguous.status == AMBIGUOUS
    assert ambiguous.uncertainty_note == "term has two plausible renderings"
    assert unsupported.status == UNSUPPORTED
    assert unsupported.translated_text is None
    assert unavailable.status == UNAVAILABLE
    assert unavailable.error_message == "provider is unavailable"
    assert failed.status == FAILED
    assert failed.error_message == "translator crashed"

    assert len(service.history("item-source-a")) == 4


def test_non_live_raw_item_falls_back_to_source_identity_without_new_origin(tmp_path):
    runtime = _runtime(tmp_path)
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            ("manual-source", "Manual Source", "Official sources", "official"),
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES (?, ?, ?, ?, ?)",
            (
                "manual-item",
                "manual-source",
                "Заголовок",
                "Ручний текст",
                NOW.isoformat(),
            ),
        )

    record = TranslationService(runtime).translate_raw_item(
        "manual-item",
        "uk",
        "en",
        DeterministicTranslationAdapter(
            {("uk", "en", "Ручний текст"): "Manual text"}
        ),
        translated_at=NOW,
    )

    assert record.underlying_origin_id == "manual-source"
    assert record.origin_kind == "SOURCE_ID"
    assert record.creates_independent_origin is False


def test_translation_does_not_change_m8_verification_or_origin_count(tmp_path):
    runtime = _runtime(tmp_path)
    collection = LiveSourceCollector(
        runtime,
        [
            StaticAdapter("source-a", "https://origin-a.example/story"),
            StaticAdapter("source-b", "https://origin-b.example/story"),
        ],
    ).collect("watch-translation", NOW)
    processor = LiveEndToEndProcessor(runtime)
    before = processor.process_collection(collection.collection_id, processed_at=NOW)

    service = TranslationService(runtime)
    translated = service.translate_raw_item(
        "item-source-a",
        "uk",
        "en",
        DeterministicTranslationAdapter(
            {("uk", "en", "Оригінальний текст"): "Original text"}
        ),
        translated_at=NOW,
    )
    after = processor.process_collection(collection.collection_id, processed_at=NOW)

    assert translated.underlying_origin_id == "origin-a.example"
    assert len(before.claims) == 1
    assert after.claims == before.claims
    assert after.claims[0].independent_origins == (
        "origin-a.example",
        "origin-b.example",
    )
    assert len(after.claims[0].independent_origins) == 2


def test_translation_history_survives_runtime_restart(tmp_path):
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Translation test",
        "translation",
        60,
        watch_id="watch-translation",
        created_at=NOW,
    )
    _collect_one(runtime)
    created = TranslationService(runtime).translate_raw_item(
        "item-source-a",
        "uk",
        "en",
        DeterministicTranslationAdapter(
            {("uk", "en", "Оригінальний текст"): "Original text"}
        ),
        translated_at=NOW,
    )

    restarted = OperationalMonitoringRuntime(project_root)
    reloaded = TranslationService(restarted).latest("item-source-a", "en")

    assert reloaded == created
    assert restarted.database_path == runtime.database_path
