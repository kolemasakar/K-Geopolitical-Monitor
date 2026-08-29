"""Post-Phase-11 E1 provider-neutral translation foundation.

Translations are derived presentation/analysis aids. They never replace the original
raw item and never create a new independent evidence origin.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import sqlite3
from typing import Mapping, Protocol
from urllib.parse import urlparse

from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time, utc_now
from .region_language_coverage import normalize_language_code


SUCCESS = "SUCCESS"
FAILED = "FAILED"
UNAVAILABLE = "UNAVAILABLE"
UNSUPPORTED = "UNSUPPORTED"
AMBIGUOUS = "AMBIGUOUS"
TRANSLATION_STATUSES = {SUCCESS, FAILED, UNAVAILABLE, UNSUPPORTED, AMBIGUOUS}
TEXT_FIELDS = {"title", "content"}


@dataclass(frozen=True)
class TranslationAdapterResult:
    status: str
    translated_text: str | None = None
    uncertainty_note: str | None = None
    error_message: str | None = None


class TranslationAdapter(Protocol):
    method: str
    provider: str | None
    provider_version: str | None

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> TranslationAdapterResult: ...


@dataclass(frozen=True)
class TranslationRecord:
    translation_id: str
    raw_item_id: str
    text_field: str
    source_language: str
    target_language: str
    original_text: str
    translated_text: str | None
    status: str
    method: str
    provider: str | None
    provider_version: str | None
    translation_version: int
    underlying_origin_id: str
    origin_kind: str
    uncertainty_note: str | None
    error_message: str | None
    created_at: datetime

    @property
    def creates_independent_origin(self) -> bool:
        return False


class DeterministicTranslationAdapter:
    """Deterministic local adapter for tests and controlled local validation.

    Mapping values may be plain translated strings or explicit adapter results. A
    missing mapping is persisted as UNSUPPORTED rather than silently synthesized.
    """

    method = "LOCAL_DETERMINISTIC"
    provider = "LOCAL_DETERMINISTIC"
    provider_version = "1"

    def __init__(
        self,
        mapping: Mapping[
            tuple[str, str, str], str | TranslationAdapterResult
        ] | None = None,
    ):
        self.mapping = dict(mapping or {})

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> TranslationAdapterResult:
        key = (source_language, target_language, text)
        value = self.mapping.get(key)
        if value is None:
            return TranslationAdapterResult(
                status=UNSUPPORTED,
                error_message="deterministic translation mapping is unavailable",
            )
        if isinstance(value, TranslationAdapterResult):
            return value
        return TranslationAdapterResult(status=SUCCESS, translated_text=str(value))


def _stable_translation_id(
    raw_item_id: str,
    text_field: str,
    target_language: str,
    translation_version: int,
) -> str:
    identity = f"{raw_item_id}:{text_field}:{target_language}:{translation_version}"
    digest = sha256(identity.encode("utf-8")).hexdigest()[:24]
    return f"translation-{digest}"


def _origin_host(original_url: str) -> str:
    host = (urlparse(original_url).hostname or "").casefold().strip(".")
    if host.startswith("www."):
        host = host[4:]
    if not host:
        raise ValueError("live provenance original_url must contain a host")
    return host


def _clean_optional(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _validate_adapter_result(result: TranslationAdapterResult) -> TranslationAdapterResult:
    status = str(result.status).strip().upper()
    if status not in TRANSLATION_STATUSES:
        raise ValueError(f"unsupported translation status: {result.status}")

    translated_text = _clean_optional(result.translated_text)
    uncertainty_note = _clean_optional(result.uncertainty_note)
    error_message = _clean_optional(result.error_message)

    if status == SUCCESS:
        if translated_text is None:
            raise ValueError("SUCCESS translation requires translated_text")
        if error_message is not None:
            raise ValueError("SUCCESS translation cannot contain error_message")
    elif status == AMBIGUOUS:
        if translated_text is None:
            raise ValueError("AMBIGUOUS translation requires translated_text")
        if uncertainty_note is None:
            raise ValueError("AMBIGUOUS translation requires uncertainty_note")
        if error_message is not None:
            raise ValueError("AMBIGUOUS translation cannot contain error_message")
    else:
        if translated_text is not None:
            raise ValueError(f"{status} translation cannot contain translated_text")
        if error_message is None:
            raise ValueError(f"{status} translation requires error_message")

    return TranslationAdapterResult(
        status=status,
        translated_text=translated_text,
        uncertainty_note=uncertainty_note,
        error_message=error_message,
    )


class TranslationService:
    """Persist versioned translations without mutating original or evidence state."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path

    def _raw_item(self, raw_item_id: str) -> tuple[str, str, str]:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT source_id, title, content FROM raw_items WHERE id = ?",
                (raw_item_id,),
            ).fetchone()
        if row is None:
            raise ValueError("raw item does not exist")
        return str(row[0]), str(row[1] or ""), str(row[2] or "")

    def _underlying_origin(self, raw_item_id: str, source_id: str) -> tuple[str, str]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT original_url
                FROM live_source_provenance
                WHERE raw_item_id = ?
                ORDER BY original_url
                """,
                (raw_item_id,),
            ).fetchall()

        if not rows:
            normalized_source = source_id.strip()
            if not normalized_source:
                raise ValueError("raw item source_id cannot define an origin")
            return normalized_source, "SOURCE_ID"

        hosts = {_origin_host(str(row[0])) for row in rows}
        if len(hosts) != 1:
            raise ValueError("raw item has conflicting live provenance origins")
        return next(iter(hosts)), "ORIGIN_HOST"

    def _next_version(self, raw_item_id: str, text_field: str, target_language: str) -> int:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT COALESCE(MAX(translation_version), 0)
                FROM raw_item_translations
                WHERE raw_item_id = ? AND text_field = ? AND target_language = ?
                """,
                (raw_item_id, text_field, target_language),
            ).fetchone()
        return int(row[0]) + 1

    def translate_raw_item(
        self,
        raw_item_id: str,
        source_language: str,
        target_language: str,
        adapter: TranslationAdapter,
        *,
        text_field: str = "content",
        translated_at: datetime | None = None,
    ) -> TranslationRecord:
        normalized_field = text_field.strip().lower()
        if normalized_field not in TEXT_FIELDS:
            raise ValueError("text_field must be title or content")

        source_code = normalize_language_code(source_language)
        target_code = normalize_language_code(target_language)
        if source_code == target_code:
            raise ValueError("source and target language must differ")

        method = _clean_optional(getattr(adapter, "method", None))
        if method is None:
            raise ValueError("translation adapter method must not be empty")
        provider = _clean_optional(getattr(adapter, "provider", None))
        provider_version = _clean_optional(getattr(adapter, "provider_version", None))

        source_id, title, content = self._raw_item(raw_item_id)
        original_text = title if normalized_field == "title" else content
        if not original_text.strip():
            raise ValueError("raw item translation field is empty")

        underlying_origin_id, origin_kind = self._underlying_origin(raw_item_id, source_id)
        version = self._next_version(raw_item_id, normalized_field, target_code)
        created_at = _normalize_time(translated_at or utc_now())

        try:
            adapter_result = adapter.translate(
                original_text,
                source_language=source_code,
                target_language=target_code,
            )
            result = _validate_adapter_result(adapter_result)
        except Exception as exc:
            error = str(exc).strip() or exc.__class__.__name__
            result = TranslationAdapterResult(status=FAILED, error_message=error)

        translation_id = _stable_translation_id(
            raw_item_id,
            normalized_field,
            target_code,
            version,
        )
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO raw_item_translations(
                    translation_id, raw_item_id, text_field,
                    source_language, target_language, original_text,
                    translated_text, status, method, provider,
                    provider_version, translation_version,
                    underlying_origin_id, origin_kind, uncertainty_note,
                    error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    translation_id,
                    raw_item_id,
                    normalized_field,
                    source_code,
                    target_code,
                    original_text,
                    result.translated_text,
                    result.status,
                    method,
                    provider,
                    provider_version,
                    version,
                    underlying_origin_id,
                    origin_kind,
                    result.uncertainty_note,
                    result.error_message,
                    created_at.isoformat(),
                ),
            )

        return TranslationRecord(
            translation_id=translation_id,
            raw_item_id=raw_item_id,
            text_field=normalized_field,
            source_language=source_code,
            target_language=target_code,
            original_text=original_text,
            translated_text=result.translated_text,
            status=result.status,
            method=method,
            provider=provider,
            provider_version=provider_version,
            translation_version=version,
            underlying_origin_id=underlying_origin_id,
            origin_kind=origin_kind,
            uncertainty_note=result.uncertainty_note,
            error_message=result.error_message,
            created_at=created_at,
        )

    def history(
        self,
        raw_item_id: str,
        *,
        text_field: str | None = None,
        target_language: str | None = None,
    ) -> tuple[TranslationRecord, ...]:
        clauses = ["raw_item_id = ?"]
        params: list[object] = [raw_item_id]
        if text_field is not None:
            normalized_field = text_field.strip().lower()
            if normalized_field not in TEXT_FIELDS:
                raise ValueError("text_field must be title or content")
            clauses.append("text_field = ?")
            params.append(normalized_field)
        if target_language is not None:
            clauses.append("target_language = ?")
            params.append(normalize_language_code(target_language))

        query = """
            SELECT translation_id, raw_item_id, text_field,
                   source_language, target_language, original_text,
                   translated_text, status, method, provider,
                   provider_version, translation_version,
                   underlying_origin_id, origin_kind, uncertainty_note,
                   error_message, created_at
            FROM raw_item_translations
            WHERE {where_clause}
            ORDER BY target_language, text_field, translation_version
        """.format(where_clause=" AND ".join(clauses))
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        return tuple(self._record_from_row(row) for row in rows)

    def latest(
        self,
        raw_item_id: str,
        target_language: str,
        *,
        text_field: str = "content",
    ) -> TranslationRecord | None:
        normalized_field = text_field.strip().lower()
        if normalized_field not in TEXT_FIELDS:
            raise ValueError("text_field must be title or content")
        target_code = normalize_language_code(target_language)
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT translation_id, raw_item_id, text_field,
                       source_language, target_language, original_text,
                       translated_text, status, method, provider,
                       provider_version, translation_version,
                       underlying_origin_id, origin_kind, uncertainty_note,
                       error_message, created_at
                FROM raw_item_translations
                WHERE raw_item_id = ? AND text_field = ? AND target_language = ?
                ORDER BY translation_version DESC
                LIMIT 1
                """,
                (raw_item_id, normalized_field, target_code),
            ).fetchone()
        return None if row is None else self._record_from_row(row)

    @staticmethod
    def _record_from_row(row: tuple) -> TranslationRecord:
        return TranslationRecord(
            translation_id=row[0],
            raw_item_id=row[1],
            text_field=row[2],
            source_language=row[3],
            target_language=row[4],
            original_text=row[5],
            translated_text=row[6],
            status=row[7],
            method=row[8],
            provider=row[9],
            provider_version=row[10],
            translation_version=int(row[11]),
            underlying_origin_id=row[12],
            origin_kind=row[13],
            uncertainty_note=row[14],
            error_message=row[15],
            created_at=datetime.fromisoformat(row[16]),
        )
