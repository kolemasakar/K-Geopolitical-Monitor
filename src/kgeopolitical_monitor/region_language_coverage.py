"""M10 project-local region and language coverage baseline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re
import sqlite3

from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time, utc_now


ATTRIBUTION_TYPES = {
    "SOURCE_METADATA",
    "ANALYST",
    "DECLARED",
    "TRANSLATION",
}


def normalize_region_code(value: str) -> str:
    normalized = value.strip().upper().replace(" ", "_")
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{1,31}", normalized):
        raise ValueError("invalid region code")
    return normalized


def normalize_language_code(value: str) -> str:
    normalized = value.strip().replace("_", "-").lower()
    if not re.fullmatch(r"[a-z]{2,8}(?:-[a-z0-9]{1,8})*", normalized):
        raise ValueError("invalid language code")
    return normalized


def _stable_id(prefix: str, value: str) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class RegionDefinition:
    region_code: str
    name: str
    region_group: str | None
    created_at: datetime


@dataclass(frozen=True)
class LanguageDefinition:
    language_code: str
    name: str
    created_at: datetime


@dataclass(frozen=True)
class ScopeRequirement:
    watch_id: str
    region_code: str
    language_code: str
    required: bool
    created_at: datetime


@dataclass(frozen=True)
class ObservationAttribution:
    watch_id: str
    raw_item_id: str
    region_code: str
    language_code: str
    attribution_type: str
    confidence: float
    original_language: bool
    created_at: datetime


@dataclass(frozen=True)
class RegionLanguageCoverageReport:
    report_id: str
    watch_id: str
    required_scopes: tuple[str, ...]
    observed_scopes: tuple[str, ...]
    observed_regions: tuple[str, ...]
    observed_languages: tuple[str, ...]
    missing_scopes: tuple[str, ...]
    coverage_ratio: float
    created_at: datetime


class RegionLanguageCoverageService:
    """Manage explicit watch scope and coverage metadata without changing evidence truth."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path

    def register_region(
        self,
        region_code: str,
        name: str,
        *,
        region_group: str | None = None,
        created_at: datetime | None = None,
    ) -> RegionDefinition:
        code = normalize_region_code(region_code)
        if not name.strip():
            raise ValueError("region name must not be empty")
        group = region_group.strip() if region_group and region_group.strip() else None
        timestamp = _normalize_time(created_at or utc_now())
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO region_catalog(region_code, name, region_group, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(region_code) DO UPDATE SET
                    name = excluded.name,
                    region_group = excluded.region_group
                """,
                (code, name.strip(), group, timestamp.isoformat()),
            )
        region = self.get_region(code)
        if region is None:
            raise RuntimeError("failed to persist region")
        return region

    def get_region(self, region_code: str) -> RegionDefinition | None:
        code = normalize_region_code(region_code)
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT region_code, name, region_group, created_at
                FROM region_catalog
                WHERE region_code = ?
                """,
                (code,),
            ).fetchone()
        if row is None:
            return None
        return RegionDefinition(
            region_code=row[0],
            name=row[1],
            region_group=row[2],
            created_at=datetime.fromisoformat(row[3]),
        )

    def register_language(
        self,
        language_code: str,
        name: str,
        *,
        created_at: datetime | None = None,
    ) -> LanguageDefinition:
        code = normalize_language_code(language_code)
        if not name.strip():
            raise ValueError("language name must not be empty")
        timestamp = _normalize_time(created_at or utc_now())
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO language_catalog(language_code, name, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(language_code) DO UPDATE SET
                    name = excluded.name
                """,
                (code, name.strip(), timestamp.isoformat()),
            )
        language = self.get_language(code)
        if language is None:
            raise RuntimeError("failed to persist language")
        return language

    def get_language(self, language_code: str) -> LanguageDefinition | None:
        code = normalize_language_code(language_code)
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT language_code, name, created_at
                FROM language_catalog
                WHERE language_code = ?
                """,
                (code,),
            ).fetchone()
        if row is None:
            return None
        return LanguageDefinition(
            language_code=row[0],
            name=row[1],
            created_at=datetime.fromisoformat(row[2]),
        )

    def configure_watch_scope(
        self,
        watch_id: str,
        scopes: list[tuple[str, str]],
        *,
        configured_at: datetime | None = None,
    ) -> tuple[ScopeRequirement, ...]:
        if self.runtime.repository.get_watch(watch_id) is None:
            raise ValueError("watch does not exist")
        if not scopes:
            raise ValueError("watch requires at least one region/language scope")

        timestamp = _normalize_time(configured_at or utc_now())
        normalized: list[tuple[str, str]] = []
        for region_code, language_code in scopes:
            region = normalize_region_code(region_code)
            language = normalize_language_code(language_code)
            if self.get_region(region) is None:
                raise ValueError(f"unknown region: {region}")
            if self.get_language(language) is None:
                raise ValueError(f"unknown language: {language}")
            normalized.append((region, language))
        unique = sorted(set(normalized))

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "DELETE FROM watch_region_language_scopes WHERE watch_id = ?",
                (watch_id,),
            )
            for region, language in unique:
                connection.execute(
                    """
                    INSERT INTO watch_region_language_scopes(
                        watch_id, region_code, language_code, required, created_at
                    ) VALUES (?, ?, ?, 1, ?)
                    """,
                    (watch_id, region, language, timestamp.isoformat()),
                )
        return self.watch_scope(watch_id)

    def watch_scope(self, watch_id: str) -> tuple[ScopeRequirement, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT watch_id, region_code, language_code, required, created_at
                FROM watch_region_language_scopes
                WHERE watch_id = ?
                ORDER BY region_code, language_code
                """,
                (watch_id,),
            ).fetchall()
        return tuple(
            ScopeRequirement(
                watch_id=row[0],
                region_code=row[1],
                language_code=row[2],
                required=bool(row[3]),
                created_at=datetime.fromisoformat(row[4]),
            )
            for row in rows
        )

    def _raw_item_exists(self, raw_item_id: str) -> bool:
        with sqlite3.connect(self.database_path) as connection:
            return (
                connection.execute(
                    "SELECT 1 FROM raw_items WHERE id = ?",
                    (raw_item_id,),
                ).fetchone()
                is not None
            )

    def _raw_item_belongs_to_watch(self, watch_id: str, raw_item_id: str) -> bool:
        with sqlite3.connect(self.database_path) as connection:
            live = connection.execute(
                """
                SELECT 1
                FROM live_source_provenance AS provenance
                JOIN source_collection_runs AS collection
                  ON collection.collection_id = provenance.collection_id
                WHERE collection.watch_id = ? AND provenance.raw_item_id = ?
                LIMIT 1
                """,
                (watch_id, raw_item_id),
            ).fetchone()
            if live is not None:
                return True
            rows = connection.execute(
                """
                SELECT evidence_refs
                FROM operational_findings
                WHERE watch_id = ?
                """,
                (watch_id,),
            ).fetchall()
        needle = f"raw_item:{raw_item_id}"
        for row in rows:
            try:
                refs = json.loads(row[0])
            except (TypeError, json.JSONDecodeError):
                continue
            if needle in refs:
                return True
        return False

    def tag_observation(
        self,
        watch_id: str,
        raw_item_id: str,
        region_code: str,
        language_code: str,
        *,
        attribution_type: str = "ANALYST",
        confidence: float = 1.0,
        original_language: bool = True,
        tagged_at: datetime | None = None,
    ) -> ObservationAttribution:
        if self.runtime.repository.get_watch(watch_id) is None:
            raise ValueError("watch does not exist")
        if not self._raw_item_exists(raw_item_id):
            raise ValueError("raw item does not exist")
        if not self._raw_item_belongs_to_watch(watch_id, raw_item_id):
            raise ValueError("raw item is not associated with watch")

        region = normalize_region_code(region_code)
        language = normalize_language_code(language_code)
        if self.get_region(region) is None:
            raise ValueError(f"unknown region: {region}")
        if self.get_language(language) is None:
            raise ValueError(f"unknown language: {language}")
        if attribution_type not in ATTRIBUTION_TYPES:
            raise ValueError("unsupported attribution type")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("attribution confidence must be between 0 and 1")

        timestamp = _normalize_time(tagged_at or utc_now())
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO observation_region_language(
                    watch_id, raw_item_id, region_code, language_code,
                    attribution_type, confidence, original_language, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    watch_id, raw_item_id, region_code, language_code, attribution_type
                ) DO UPDATE SET
                    confidence = excluded.confidence,
                    original_language = excluded.original_language,
                    created_at = excluded.created_at
                """,
                (
                    watch_id,
                    raw_item_id,
                    region,
                    language,
                    attribution_type,
                    confidence,
                    int(bool(original_language)),
                    timestamp.isoformat(),
                ),
            )
        return ObservationAttribution(
            watch_id=watch_id,
            raw_item_id=raw_item_id,
            region_code=region,
            language_code=language,
            attribution_type=attribution_type,
            confidence=confidence,
            original_language=bool(original_language),
            created_at=timestamp,
        )

    def attributions(self, watch_id: str) -> tuple[ObservationAttribution, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT watch_id, raw_item_id, region_code, language_code,
                       attribution_type, confidence, original_language, created_at
                FROM observation_region_language
                WHERE watch_id = ?
                ORDER BY raw_item_id, region_code, language_code, attribution_type
                """,
                (watch_id,),
            ).fetchall()
        return tuple(
            ObservationAttribution(
                watch_id=row[0],
                raw_item_id=row[1],
                region_code=row[2],
                language_code=row[3],
                attribution_type=row[4],
                confidence=float(row[5]),
                original_language=bool(row[6]),
                created_at=datetime.fromisoformat(row[7]),
            )
            for row in rows
        )

    def generate_coverage_report(
        self,
        watch_id: str,
        *,
        created_at: datetime | None = None,
    ) -> RegionLanguageCoverageReport:
        if self.runtime.repository.get_watch(watch_id) is None:
            raise ValueError("watch does not exist")
        requirements = self.watch_scope(watch_id)
        if not requirements:
            raise ValueError("watch has no configured region/language scope")
        timestamp = _normalize_time(created_at or utc_now())

        required_pairs = {
            (item.region_code, item.language_code)
            for item in requirements
            if item.required
        }
        observed_rows = self.attributions(watch_id)
        observed_pairs = {
            (item.region_code, item.language_code)
            for item in observed_rows
        }
        missing_pairs = required_pairs - observed_pairs

        def encode(pair: tuple[str, str]) -> str:
            return f"{pair[0]}:{pair[1]}"

        required = tuple(sorted(encode(pair) for pair in required_pairs))
        observed = tuple(sorted(encode(pair) for pair in observed_pairs))
        missing = tuple(sorted(encode(pair) for pair in missing_pairs))
        regions = tuple(sorted({pair[0] for pair in observed_pairs}))
        languages = tuple(sorted({pair[1] for pair in observed_pairs}))
        ratio = (
            (len(required_pairs) - len(missing_pairs)) / len(required_pairs)
            if required_pairs
            else 1.0
        )

        identity = json.dumps(
            {
                "watch_id": watch_id,
                "required": required,
                "observed": observed,
                "created_at": timestamp.isoformat(),
            },
            sort_keys=True,
        )
        report_id = _stable_id("region-language-coverage", identity)
        report = RegionLanguageCoverageReport(
            report_id=report_id,
            watch_id=watch_id,
            required_scopes=required,
            observed_scopes=observed,
            observed_regions=regions,
            observed_languages=languages,
            missing_scopes=missing,
            coverage_ratio=ratio,
            created_at=timestamp,
        )

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO region_language_coverage_reports(
                    report_id, watch_id, required_scopes, observed_scopes,
                    observed_regions, observed_languages, missing_scopes,
                    coverage_ratio, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(report_id) DO UPDATE SET
                    required_scopes = excluded.required_scopes,
                    observed_scopes = excluded.observed_scopes,
                    observed_regions = excluded.observed_regions,
                    observed_languages = excluded.observed_languages,
                    missing_scopes = excluded.missing_scopes,
                    coverage_ratio = excluded.coverage_ratio
                """,
                (
                    report.report_id,
                    report.watch_id,
                    json.dumps(report.required_scopes),
                    json.dumps(report.observed_scopes),
                    json.dumps(report.observed_regions),
                    json.dumps(report.observed_languages),
                    json.dumps(report.missing_scopes),
                    report.coverage_ratio,
                    report.created_at.isoformat(),
                ),
            )
        return report

    def get_coverage_report(
        self,
        report_id: str,
    ) -> RegionLanguageCoverageReport | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT report_id, watch_id, required_scopes, observed_scopes,
                       observed_regions, observed_languages, missing_scopes,
                       coverage_ratio, created_at
                FROM region_language_coverage_reports
                WHERE report_id = ?
                """,
                (report_id,),
            ).fetchone()
        if row is None:
            return None
        return RegionLanguageCoverageReport(
            report_id=row[0],
            watch_id=row[1],
            required_scopes=tuple(json.loads(row[2])),
            observed_scopes=tuple(json.loads(row[3])),
            observed_regions=tuple(json.loads(row[4])),
            observed_languages=tuple(json.loads(row[5])),
            missing_scopes=tuple(json.loads(row[6])),
            coverage_ratio=float(row[7]),
            created_at=datetime.fromisoformat(row[8]),
        )
