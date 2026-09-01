"""Phase 13 P13.2 provenance and underlying-origin relation model.

This module records provenance identity, claim-level provenance roles and
entity-to-entity derivation chains. It intentionally does not assess evidence
stance, evidentiary independence, contradiction resolution, verification state
or factual/coverage confidence; those belong to P13.3+.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Mapping
from urllib.parse import parse_qsl, urlsplit

from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


SEMANTIC_PROVENANCE_MODEL_VERSION = "P13.2-1.0"
ENTITY_KINDS = (
    "PUBLICATION",
    "PUBLISHER",
    "SOURCE_ENDPOINT",
    "OFFICIAL_STATEMENT",
    "OFFICIAL_DOCUMENT",
    "WIRE_REPORT",
    "DATASET",
    "SOCIAL_POST",
    "USER_PROVIDED",
    "OTHER",
    "UNKNOWN",
    "MIXED",
)
PROVENANCE_ROLES = (
    "PUBLICATION",
    "PUBLISHER",
    "IMMEDIATE_ACQUIRED_SOURCE",
    "CITED_SOURCE",
    "QUOTED_SOURCE",
    "UNDERLYING_ORIGIN",
    "PROVENANCE_CONTEXT",
)
ATTRIBUTION_STATES = ("OBSERVED", "ASSERTED", "UNRESOLVED", "MIXED")
RELATION_TYPES = (
    "PUBLISHED_BY",
    "ACQUIRED_FROM",
    "CITES",
    "QUOTES",
    "SYNDICATED_FROM",
    "REPOSTED_FROM",
    "TRANSLATED_FROM",
    "DERIVED_FROM",
    "DATA_EXTRACTED_FROM",
    "OTHER",
)
_SENSITIVE_QUERY_KEYS = {
    "api_key",
    "apikey",
    "access_token",
    "token",
    "auth",
    "authorization",
    "secret",
    "signature",
    "sig",
}


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


def _language(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = _required(value, "language").lower().replace("_", "-")
    if not re.fullmatch(r"[a-z]{2,8}(?:-[a-z0-9]{1,8})*", normalized):
        raise ValueError("language must be a normalized language tag")
    return normalized


def _json_object(value: Mapping[str, object] | None, field_name: str) -> dict[str, object]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object mapping")
    try:
        encoded = json.dumps(dict(value), sort_keys=True, ensure_ascii=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON-serializable") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return decoded


def _url(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = _required(value, "canonical_url")
    parsed = urlsplit(normalized)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("canonical_url must be HTTP or HTTPS")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("canonical_url must not contain credentials")
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in _SENSITIVE_QUERY_KEYS:
            raise ValueError("canonical_url must not contain sensitive query credentials")
    return normalized


def _stable_version_id(prefix: str, identity: str, version: int) -> str:
    digest = sha256(f"{identity}:{version}".encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class ProvenanceEntityVersion:
    provenance_entity_version_id: str
    provenance_entity_id: str
    provenance_version: int
    entity_kind: str
    canonical_name: str
    source_id: str | None
    raw_item_id: str | None
    canonical_url: str | None
    language: str | None
    metadata: dict[str, object]
    supersedes_version_id: str | None
    created_at: datetime

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def changes_verification_state(self) -> bool:
        return False


@dataclass(frozen=True)
class ClaimProvenanceRoleVersion:
    claim_provenance_role_version_id: str
    claim_provenance_role_id: str
    role_version: int
    semantic_claim_version_id: str
    provenance_entity_version_id: str
    provenance_role: str
    attribution_state: str
    note: str | None
    supersedes_role_version_id: str | None
    created_at: datetime

    @property
    def is_evidence_relation(self) -> bool:
        return False

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def changes_verification_state(self) -> bool:
        return False


@dataclass(frozen=True)
class ProvenanceRelationVersion:
    provenance_relation_version_id: str
    provenance_relation_id: str
    relation_version: int
    subject_entity_version_id: str
    object_entity_version_id: str
    relation_type: str
    note: str | None
    supersedes_relation_version_id: str | None
    created_at: datetime

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def changes_verification_state(self) -> bool:
        return False


class SemanticProvenanceService:
    """Append-only P13.2 provenance persistence without truth promotion."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path

    def record_entity_version(
        self,
        provenance_entity_id: str,
        *,
        entity_kind: str,
        canonical_name: str,
        source_id: str | None = None,
        raw_item_id: str | None = None,
        canonical_url: str | None = None,
        language: str | None = None,
        metadata: Mapping[str, object] | None = None,
        created_at: datetime,
    ) -> ProvenanceEntityVersion:
        entity_id = _required(provenance_entity_id, "provenance_entity_id")
        kind = _enum(entity_kind, "entity_kind", ENTITY_KINDS)
        name = _required(canonical_name, "canonical_name")
        normalized_source = _optional(source_id)
        normalized_raw = _optional(raw_item_id)
        normalized_url = _url(canonical_url)
        normalized_language = _language(language)
        normalized_metadata = _json_object(metadata, "metadata")
        timestamp = _normalize_time(created_at)

        if kind in {"UNKNOWN", "MIXED"} and any(
            value is not None for value in (normalized_source, normalized_raw, normalized_url)
        ):
            raise ValueError(f"{kind} provenance entity cannot claim concrete source/raw/url identity")

        with runtime_database_connection(self.database_path) as connection:
            if normalized_source is not None and connection.execute(
                "SELECT 1 FROM sources WHERE id = ?", (normalized_source,)
            ).fetchone() is None:
                raise ValueError("source_id does not exist")

            raw_source_id = None
            if normalized_raw is not None:
                row = connection.execute(
                    "SELECT source_id FROM raw_items WHERE id = ?", (normalized_raw,)
                ).fetchone()
                if row is None:
                    raise ValueError("raw_item_id does not exist")
                raw_source_id = row[0]
            if (
                normalized_source is not None
                and raw_source_id is not None
                and normalized_source != raw_source_id
            ):
                raise ValueError("source_id does not match raw_item source")

            previous_row = connection.execute(
                """
                SELECT provenance_entity_version_id, provenance_version
                FROM semantic_provenance_entity_versions
                WHERE provenance_entity_id = ?
                ORDER BY provenance_version DESC
                LIMIT 1
                """,
                (entity_id,),
            ).fetchone()
            version = 1 if previous_row is None else int(previous_row[1]) + 1
            supersedes = None if previous_row is None else previous_row[0]
            version_id = _stable_version_id("provenance-entity-version", entity_id, version)

            connection.execute(
                """
                INSERT INTO semantic_provenance_entity_versions(
                    provenance_entity_version_id, provenance_entity_id, provenance_version,
                    entity_kind, canonical_name, source_id, raw_item_id, canonical_url,
                    language, metadata_json, supersedes_version_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    entity_id,
                    version,
                    kind,
                    name,
                    normalized_source,
                    normalized_raw,
                    normalized_url,
                    normalized_language,
                    json.dumps(normalized_metadata, sort_keys=True, ensure_ascii=False),
                    supersedes,
                    timestamp.isoformat(),
                ),
            )

        return ProvenanceEntityVersion(
            provenance_entity_version_id=version_id,
            provenance_entity_id=entity_id,
            provenance_version=version,
            entity_kind=kind,
            canonical_name=name,
            source_id=normalized_source,
            raw_item_id=normalized_raw,
            canonical_url=normalized_url,
            language=normalized_language,
            metadata=normalized_metadata,
            supersedes_version_id=supersedes,
            created_at=timestamp,
        )

    def entity_current(self, provenance_entity_id: str) -> ProvenanceEntityVersion | None:
        entity_id = _required(provenance_entity_id, "provenance_entity_id")
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT provenance_entity_version_id, provenance_entity_id, provenance_version,
                       entity_kind, canonical_name, source_id, raw_item_id, canonical_url,
                       language, metadata_json, supersedes_version_id, created_at
                FROM semantic_provenance_entity_versions
                WHERE provenance_entity_id = ?
                ORDER BY provenance_version DESC
                LIMIT 1
                """,
                (entity_id,),
            ).fetchone()
        return None if row is None else self._entity_from_row(row)

    def entity_history(self, provenance_entity_id: str) -> tuple[ProvenanceEntityVersion, ...]:
        entity_id = _required(provenance_entity_id, "provenance_entity_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT provenance_entity_version_id, provenance_entity_id, provenance_version,
                       entity_kind, canonical_name, source_id, raw_item_id, canonical_url,
                       language, metadata_json, supersedes_version_id, created_at
                FROM semantic_provenance_entity_versions
                WHERE provenance_entity_id = ?
                ORDER BY provenance_version
                """,
                (entity_id,),
            ).fetchall()
        return tuple(self._entity_from_row(row) for row in rows)

    def record_claim_role_version(
        self,
        claim_provenance_role_id: str,
        *,
        semantic_claim_version_id: str,
        provenance_entity_version_id: str,
        provenance_role: str,
        attribution_state: str,
        note: str | None = None,
        created_at: datetime,
    ) -> ClaimProvenanceRoleVersion:
        role_id = _required(claim_provenance_role_id, "claim_provenance_role_id")
        claim_version_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        entity_version_id = _required(provenance_entity_version_id, "provenance_entity_version_id")
        role = _enum(provenance_role, "provenance_role", PROVENANCE_ROLES)
        state = _enum(attribution_state, "attribution_state", ATTRIBUTION_STATES)
        normalized_note = _optional(note)
        timestamp = _normalize_time(created_at)

        with runtime_database_connection(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id = ?",
                (claim_version_id,),
            ).fetchone() is None:
                raise ValueError("semantic claim version does not exist")
            entity_row = connection.execute(
                "SELECT entity_kind FROM semantic_provenance_entity_versions WHERE provenance_entity_version_id = ?",
                (entity_version_id,),
            ).fetchone()
            if entity_row is None:
                raise ValueError("provenance entity version does not exist")
            entity_kind = entity_row[0]

            if state in {"UNRESOLVED", "MIXED"} and role != "UNDERLYING_ORIGIN":
                raise ValueError("UNRESOLVED/MIXED attribution is only valid for UNDERLYING_ORIGIN")
            if role == "UNDERLYING_ORIGIN":
                if state == "UNRESOLVED" and entity_kind != "UNKNOWN":
                    raise ValueError("UNRESOLVED underlying origin requires UNKNOWN entity")
                if state == "MIXED" and entity_kind != "MIXED":
                    raise ValueError("MIXED underlying origin requires MIXED entity")
                if entity_kind == "UNKNOWN" and state != "UNRESOLVED":
                    raise ValueError("UNKNOWN underlying origin must remain UNRESOLVED")
                if entity_kind == "MIXED" and state != "MIXED":
                    raise ValueError("MIXED underlying origin must remain MIXED")
            elif entity_kind in {"UNKNOWN", "MIXED"}:
                raise ValueError("UNKNOWN/MIXED entity may only represent UNDERLYING_ORIGIN")

            previous_row = connection.execute(
                """
                SELECT claim_provenance_role_version_id, role_version
                FROM semantic_claim_provenance_role_versions
                WHERE claim_provenance_role_id = ?
                ORDER BY role_version DESC
                LIMIT 1
                """,
                (role_id,),
            ).fetchone()
            version = 1 if previous_row is None else int(previous_row[1]) + 1
            supersedes = None if previous_row is None else previous_row[0]
            version_id = _stable_version_id("claim-provenance-role-version", role_id, version)

            connection.execute(
                """
                INSERT INTO semantic_claim_provenance_role_versions(
                    claim_provenance_role_version_id, claim_provenance_role_id, role_version,
                    semantic_claim_version_id, provenance_entity_version_id, provenance_role,
                    attribution_state, note, supersedes_role_version_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    role_id,
                    version,
                    claim_version_id,
                    entity_version_id,
                    role,
                    state,
                    normalized_note,
                    supersedes,
                    timestamp.isoformat(),
                ),
            )

        return ClaimProvenanceRoleVersion(
            claim_provenance_role_version_id=version_id,
            claim_provenance_role_id=role_id,
            role_version=version,
            semantic_claim_version_id=claim_version_id,
            provenance_entity_version_id=entity_version_id,
            provenance_role=role,
            attribution_state=state,
            note=normalized_note,
            supersedes_role_version_id=supersedes,
            created_at=timestamp,
        )

    def claim_roles(self, semantic_claim_version_id: str) -> tuple[ClaimProvenanceRoleVersion, ...]:
        claim_version_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT claim_provenance_role_version_id, claim_provenance_role_id,
                       role_version, semantic_claim_version_id, provenance_entity_version_id,
                       provenance_role, attribution_state, note,
                       supersedes_role_version_id, created_at
                FROM semantic_claim_provenance_role_versions
                WHERE semantic_claim_version_id = ?
                ORDER BY provenance_role, claim_provenance_role_id, role_version
                """,
                (claim_version_id,),
            ).fetchall()
        return tuple(self._claim_role_from_row(row) for row in rows)

    def record_relation_version(
        self,
        provenance_relation_id: str,
        *,
        subject_entity_version_id: str,
        object_entity_version_id: str,
        relation_type: str,
        note: str | None = None,
        created_at: datetime,
    ) -> ProvenanceRelationVersion:
        relation_id = _required(provenance_relation_id, "provenance_relation_id")
        subject_id = _required(subject_entity_version_id, "subject_entity_version_id")
        object_id = _required(object_entity_version_id, "object_entity_version_id")
        relation = _enum(relation_type, "relation_type", RELATION_TYPES)
        normalized_note = _optional(note)
        timestamp = _normalize_time(created_at)
        if subject_id == object_id:
            raise ValueError("provenance relation cannot point to itself")

        with runtime_database_connection(self.database_path) as connection:
            entity_rows = connection.execute(
                """
                SELECT provenance_entity_version_id, entity_kind
                FROM semantic_provenance_entity_versions
                WHERE provenance_entity_version_id IN (?, ?)
                """,
                (subject_id, object_id),
            ).fetchall()
            kinds = {row[0]: row[1] for row in entity_rows}
            if subject_id not in kinds or object_id not in kinds:
                raise ValueError("provenance relation entity version does not exist")
            if kinds[subject_id] in {"UNKNOWN", "MIXED"} or kinds[object_id] in {"UNKNOWN", "MIXED"}:
                raise ValueError("UNKNOWN/MIXED origin cannot fabricate a concrete derivation chain")

            previous_row = connection.execute(
                """
                SELECT provenance_relation_version_id, relation_version
                FROM semantic_provenance_relation_versions
                WHERE provenance_relation_id = ?
                ORDER BY relation_version DESC
                LIMIT 1
                """,
                (relation_id,),
            ).fetchone()
            version = 1 if previous_row is None else int(previous_row[1]) + 1
            supersedes = None if previous_row is None else previous_row[0]
            version_id = _stable_version_id("provenance-relation-version", relation_id, version)

            connection.execute(
                """
                INSERT INTO semantic_provenance_relation_versions(
                    provenance_relation_version_id, provenance_relation_id, relation_version,
                    subject_entity_version_id, object_entity_version_id, relation_type,
                    note, supersedes_relation_version_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    relation_id,
                    version,
                    subject_id,
                    object_id,
                    relation,
                    normalized_note,
                    supersedes,
                    timestamp.isoformat(),
                ),
            )

        return ProvenanceRelationVersion(
            provenance_relation_version_id=version_id,
            provenance_relation_id=relation_id,
            relation_version=version,
            subject_entity_version_id=subject_id,
            object_entity_version_id=object_id,
            relation_type=relation,
            note=normalized_note,
            supersedes_relation_version_id=supersedes,
            created_at=timestamp,
        )

    def relation_history(self, provenance_relation_id: str) -> tuple[ProvenanceRelationVersion, ...]:
        relation_id = _required(provenance_relation_id, "provenance_relation_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT provenance_relation_version_id, provenance_relation_id,
                       relation_version, subject_entity_version_id, object_entity_version_id,
                       relation_type, note, supersedes_relation_version_id, created_at
                FROM semantic_provenance_relation_versions
                WHERE provenance_relation_id = ?
                ORDER BY relation_version
                """,
                (relation_id,),
            ).fetchall()
        return tuple(self._relation_from_row(row) for row in rows)

    @staticmethod
    def _entity_from_row(row) -> ProvenanceEntityVersion:
        return ProvenanceEntityVersion(
            provenance_entity_version_id=row[0],
            provenance_entity_id=row[1],
            provenance_version=int(row[2]),
            entity_kind=row[3],
            canonical_name=row[4],
            source_id=row[5],
            raw_item_id=row[6],
            canonical_url=row[7],
            language=row[8],
            metadata=json.loads(row[9]),
            supersedes_version_id=row[10],
            created_at=datetime.fromisoformat(row[11]),
        )

    @staticmethod
    def _claim_role_from_row(row) -> ClaimProvenanceRoleVersion:
        return ClaimProvenanceRoleVersion(
            claim_provenance_role_version_id=row[0],
            claim_provenance_role_id=row[1],
            role_version=int(row[2]),
            semantic_claim_version_id=row[3],
            provenance_entity_version_id=row[4],
            provenance_role=row[5],
            attribution_state=row[6],
            note=row[7],
            supersedes_role_version_id=row[8],
            created_at=datetime.fromisoformat(row[9]),
        )

    @staticmethod
    def _relation_from_row(row) -> ProvenanceRelationVersion:
        return ProvenanceRelationVersion(
            provenance_relation_version_id=row[0],
            provenance_relation_id=row[1],
            relation_version=int(row[2]),
            subject_entity_version_id=row[3],
            object_entity_version_id=row[4],
            relation_type=row[5],
            note=row[6],
            supersedes_relation_version_id=row[7],
            created_at=datetime.fromisoformat(row[8]),
        )