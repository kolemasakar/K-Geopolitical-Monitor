"""Phase 13 P13.1 structured semantic claim model.

P13.1 stores immutable, versioned semantic claim structure and non-evidentiary
links to existing legacy/live/raw objects. It intentionally does not model
underlying origin, evidence stance/independence, contradiction resolution,
verification policy, or factual confidence promotion; those belong to P13.2+.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Mapping

from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


SEMANTIC_CLAIM_MODEL_VERSION = "P13.1-1.0"
POLARITIES = ("AFFIRMATIVE", "NEGATED", "UNKNOWN")
MODALITIES = (
    "ASSERTED",
    "REPORTED",
    "ALLEGED",
    "DENIED",
    "ESTIMATED",
    "QUESTIONED",
    "UNKNOWN",
)
LINK_TARGET_TYPES = ("LEGACY_CLAIM", "LIVE_ANALYSIS_CLAIM", "RAW_ITEM")


def _required(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _optional(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _enum(value: object, field_name: str, allowed: tuple[str, ...]) -> str:
    normalized = _required(value, field_name).upper()
    if normalized not in allowed:
        raise ValueError(f"unsupported {field_name}: {normalized}")
    return normalized


def _language(value: object) -> str:
    normalized = _required(value, "original_language").lower().replace("_", "-")
    if not re.fullmatch(r"[a-z]{2,8}(?:-[a-z0-9]{1,8})*", normalized):
        raise ValueError("original_language must be a normalized language tag")
    return normalized


def _json_object(value: Mapping[str, object] | None, field_name: str) -> dict[str, object]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object mapping")
    # JSON round-trip rejects unserializable values and yields a detached object.
    try:
        encoded = json.dumps(dict(value), sort_keys=True, ensure_ascii=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON-serializable") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return decoded


def _confidence(value: object) -> float:
    normalized = float(value)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError("extraction_confidence must be between 0 and 1")
    return normalized


def _stable_version_id(semantic_claim_id: str, version: int) -> str:
    digest = sha256(f"{semantic_claim_id}:{version}".encode("utf-8")).hexdigest()[:24]
    return f"semantic-claim-version-{digest}"


def _stable_link_id(version_id: str, target_type: str, target_id: str) -> str:
    digest = sha256(f"{version_id}:{target_type}:{target_id}".encode("utf-8")).hexdigest()[:24]
    return f"semantic-claim-link-{digest}"


@dataclass(frozen=True)
class SemanticClaimVersion:
    semantic_claim_version_id: str
    semantic_claim_id: str
    semantic_version: int
    normalized_proposition: str
    claimant_actor: str | None
    subject_text: str | None
    object_theme: str | None
    event_action_type: str | None
    polarity: str
    modality: str
    time_scope: dict[str, object]
    location_scope: dict[str, object]
    quantity: dict[str, object]
    original_language: str
    extraction_method: str
    extraction_version: str
    extraction_confidence: float
    supersedes_version_id: str | None
    created_at: datetime

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def factual_confidence(self) -> None:
        return None


@dataclass(frozen=True)
class SemanticClaimLink:
    link_id: str
    semantic_claim_version_id: str
    target_type: str
    target_id: str
    created_at: datetime

    @property
    def is_evidence_relation(self) -> bool:
        return False


class SemanticClaimService:
    """Append-only P13.1 semantic claim persistence and compatibility linkage."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path

    def record_version(
        self,
        semantic_claim_id: str,
        *,
        normalized_proposition: str,
        claimant_actor: str | None = None,
        subject_text: str | None = None,
        object_theme: str | None = None,
        event_action_type: str | None = None,
        polarity: str = "UNKNOWN",
        modality: str = "UNKNOWN",
        time_scope: Mapping[str, object] | None = None,
        location_scope: Mapping[str, object] | None = None,
        quantity: Mapping[str, object] | None = None,
        original_language: str,
        extraction_method: str,
        extraction_version: str,
        extraction_confidence: float,
        created_at: datetime,
    ) -> SemanticClaimVersion:
        claim_id = _required(semantic_claim_id, "semantic_claim_id")
        proposition = _required(normalized_proposition, "normalized_proposition")
        actor = _optional(claimant_actor)
        subject = _optional(subject_text)
        object_value = _optional(object_theme)
        action = _optional(event_action_type)
        normalized_polarity = _enum(polarity, "polarity", POLARITIES)
        normalized_modality = _enum(modality, "modality", MODALITIES)
        normalized_time = _json_object(time_scope, "time_scope")
        normalized_location = _json_object(location_scope, "location_scope")
        normalized_quantity = _json_object(quantity, "quantity")
        language = _language(original_language)
        method = _required(extraction_method, "extraction_method")
        method_version = _required(extraction_version, "extraction_version")
        extraction_score = _confidence(extraction_confidence)
        timestamp = _normalize_time(created_at)

        previous = self.current(claim_id)
        version = 1 if previous is None else previous.semantic_version + 1
        supersedes = None if previous is None else previous.semantic_claim_version_id
        version_id = _stable_version_id(claim_id, version)

        with runtime_database_connection(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO semantic_claim_versions(
                    semantic_claim_version_id, semantic_claim_id, semantic_version,
                    normalized_proposition, claimant_actor, subject_text, object_theme,
                    event_action_type, polarity, modality, time_scope_json,
                    location_scope_json, quantity_json, original_language,
                    extraction_method, extraction_version, extraction_confidence,
                    supersedes_version_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    claim_id,
                    version,
                    proposition,
                    actor,
                    subject,
                    object_value,
                    action,
                    normalized_polarity,
                    normalized_modality,
                    json.dumps(normalized_time, sort_keys=True, ensure_ascii=False),
                    json.dumps(normalized_location, sort_keys=True, ensure_ascii=False),
                    json.dumps(normalized_quantity, sort_keys=True, ensure_ascii=False),
                    language,
                    method,
                    method_version,
                    extraction_score,
                    supersedes,
                    timestamp.isoformat(),
                ),
            )

        return SemanticClaimVersion(
            semantic_claim_version_id=version_id,
            semantic_claim_id=claim_id,
            semantic_version=version,
            normalized_proposition=proposition,
            claimant_actor=actor,
            subject_text=subject,
            object_theme=object_value,
            event_action_type=action,
            polarity=normalized_polarity,
            modality=normalized_modality,
            time_scope=normalized_time,
            location_scope=normalized_location,
            quantity=normalized_quantity,
            original_language=language,
            extraction_method=method,
            extraction_version=method_version,
            extraction_confidence=extraction_score,
            supersedes_version_id=supersedes,
            created_at=timestamp,
        )

    def current(self, semantic_claim_id: str) -> SemanticClaimVersion | None:
        claim_id = _required(semantic_claim_id, "semantic_claim_id")
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT semantic_claim_version_id, semantic_claim_id, semantic_version,
                       normalized_proposition, claimant_actor, subject_text, object_theme,
                       event_action_type, polarity, modality, time_scope_json,
                       location_scope_json, quantity_json, original_language,
                       extraction_method, extraction_version, extraction_confidence,
                       supersedes_version_id, created_at
                FROM semantic_claim_versions
                WHERE semantic_claim_id = ?
                ORDER BY semantic_version DESC
                LIMIT 1
                """,
                (claim_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def history(self, semantic_claim_id: str) -> tuple[SemanticClaimVersion, ...]:
        claim_id = _required(semantic_claim_id, "semantic_claim_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT semantic_claim_version_id, semantic_claim_id, semantic_version,
                       normalized_proposition, claimant_actor, subject_text, object_theme,
                       event_action_type, polarity, modality, time_scope_json,
                       location_scope_json, quantity_json, original_language,
                       extraction_method, extraction_version, extraction_confidence,
                       supersedes_version_id, created_at
                FROM semantic_claim_versions
                WHERE semantic_claim_id = ?
                ORDER BY semantic_version
                """,
                (claim_id,),
            ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def link(
        self,
        semantic_claim_version_id: str,
        *,
        target_type: str,
        target_id: str,
        created_at: datetime,
    ) -> SemanticClaimLink:
        version_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        normalized_type = _enum(target_type, "target_type", LINK_TARGET_TYPES)
        normalized_target = _required(target_id, "target_id")
        timestamp = _normalize_time(created_at)

        with runtime_database_connection(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id = ?",
                (version_id,),
            ).fetchone() is None:
                raise ValueError("semantic claim version does not exist")

            table, column = {
                "LEGACY_CLAIM": ("claims", "id"),
                "LIVE_ANALYSIS_CLAIM": ("live_analysis_claims", "claim_id"),
                "RAW_ITEM": ("raw_items", "id"),
            }[normalized_type]
            if connection.execute(
                f"SELECT 1 FROM {table} WHERE {column} = ?",
                (normalized_target,),
            ).fetchone() is None:
                raise ValueError(f"{normalized_type} target does not exist")

            link_id = _stable_link_id(version_id, normalized_type, normalized_target)
            existing = connection.execute(
                "SELECT created_at FROM semantic_claim_links WHERE link_id = ?",
                (link_id,),
            ).fetchone()
            if existing is None:
                connection.execute(
                    """
                    INSERT INTO semantic_claim_links(
                        link_id, semantic_claim_version_id, target_type, target_id, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (link_id, version_id, normalized_type, normalized_target, timestamp.isoformat()),
                )
            else:
                timestamp = datetime.fromisoformat(existing[0])

        return SemanticClaimLink(
            link_id=link_id,
            semantic_claim_version_id=version_id,
            target_type=normalized_type,
            target_id=normalized_target,
            created_at=timestamp,
        )

    def links(self, semantic_claim_version_id: str) -> tuple[SemanticClaimLink, ...]:
        version_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT link_id, semantic_claim_version_id, target_type, target_id, created_at
                FROM semantic_claim_links
                WHERE semantic_claim_version_id = ?
                ORDER BY target_type, target_id
                """,
                (version_id,),
            ).fetchall()
        return tuple(
            SemanticClaimLink(
                link_id=row[0],
                semantic_claim_version_id=row[1],
                target_type=row[2],
                target_id=row[3],
                created_at=datetime.fromisoformat(row[4]),
            )
            for row in rows
        )

    @staticmethod
    def _from_row(row) -> SemanticClaimVersion:
        return SemanticClaimVersion(
            semantic_claim_version_id=row[0],
            semantic_claim_id=row[1],
            semantic_version=int(row[2]),
            normalized_proposition=row[3],
            claimant_actor=row[4],
            subject_text=row[5],
            object_theme=row[6],
            event_action_type=row[7],
            polarity=row[8],
            modality=row[9],
            time_scope=json.loads(row[10]),
            location_scope=json.loads(row[11]),
            quantity=json.loads(row[12]),
            original_language=row[13],
            extraction_method=row[14],
            extraction_version=row[15],
            extraction_confidence=float(row[16]),
            supersedes_version_id=row[17],
            created_at=datetime.fromisoformat(row[18]),
        )
