"""Provider-neutral Phase 18 shared-runtime contracts.

P18.0 intentionally defines boundaries only.  It does not provide a shared
canonical datastore, authentication, authorization, ingress, or activation.
The existing project-local SQLite runtime remains the active canonical
profile.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Protocol, runtime_checkable


class RuntimeProfile(str, Enum):
    """Explicit runtime profiles supported by the architecture contract."""

    OWNER_LOCAL = "owner_local"
    SHARED_TEAM = "shared_team"


class StorageScope(str, Enum):
    """Canonical storage classes visible to the runtime-profile boundary."""

    PROJECT_LOCAL_SQLITE = "project_local_sqlite"
    SHARED_CANONICAL = "shared_canonical"


class RuntimeProfileError(RuntimeError):
    """Base error for fail-closed runtime-profile selection."""


class SharedRuntimeDisabledError(RuntimeProfileError):
    """Raised when the shared/team profile is selected before enablement."""


class SharedRuntimeBoundaryError(RuntimeProfileError):
    """Raised when a shared runtime attempts to use a forbidden storage scope."""


class TenantContextError(ValueError):
    """Base error for invalid tenant context."""


class MissingTenantContextError(TenantContextError):
    """Raised when required tenant scope is absent."""


class AmbiguousTenantContextError(TenantContextError):
    """Raised when more than one tenant scope candidate is supplied."""


def _normalize_identifier(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TenantContextError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise MissingTenantContextError(f"{field_name} is required")
    return normalized


def _resolve_single_identifier(values: Iterable[str], *, field_name: str) -> str:
    normalized = {
        _normalize_identifier(value, field_name=field_name)
        for value in values
    }
    if not normalized:
        raise MissingTenantContextError(f"{field_name} is required")
    if len(normalized) != 1:
        raise AmbiguousTenantContextError(
            f"{field_name} is ambiguous: expected exactly one distinct value"
        )
    return next(iter(normalized))


@dataclass(frozen=True)
class TenantContext:
    """Required workspace/project scope for future shared-runtime operations.

    Authentication and authorization are deliberately outside P18.0 and are
    introduced in P18.1/P18.2.  This type only guarantees that a shared call
    cannot proceed without one unambiguous workspace and project scope.
    """

    workspace_id: str
    project_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "workspace_id",
            _normalize_identifier(self.workspace_id, field_name="workspace_id"),
        )
        object.__setattr__(
            self,
            "project_id",
            _normalize_identifier(self.project_id, field_name="project_id"),
        )

    @classmethod
    def resolve(
        cls,
        *,
        workspace_ids: Iterable[str],
        project_ids: Iterable[str],
    ) -> "TenantContext":
        """Resolve candidate scopes and fail closed on absence or ambiguity."""

        return cls(
            workspace_id=_resolve_single_identifier(
                workspace_ids,
                field_name="workspace_id",
            ),
            project_id=_resolve_single_identifier(
                project_ids,
                field_name="project_id",
            ),
        )


@dataclass(frozen=True)
class RuntimeProfileConfig:
    """Provider-neutral runtime-profile configuration boundary.

    The default is intentionally the existing owner/local profile.  Shared
    runtime selection requires an explicit enablement flag and remains a
    contract/test-harness capability only until later Phase 18 gates are
    validated and activated.
    """

    profile: RuntimeProfile = RuntimeProfile.OWNER_LOCAL
    shared_enabled: bool = False

    def __post_init__(self) -> None:
        if self.profile is RuntimeProfile.SHARED_TEAM and not self.shared_enabled:
            raise SharedRuntimeDisabledError(
                "shared/team runtime profile is disabled; owner/local remains active"
            )

    @classmethod
    def owner_local(cls) -> "RuntimeProfileConfig":
        return cls()

    @classmethod
    def shared_team_for_contract_test(cls) -> "RuntimeProfileConfig":
        """Enable only the P18.0 contract harness, not a production runtime."""

        return cls(profile=RuntimeProfile.SHARED_TEAM, shared_enabled=True)


@runtime_checkable
class SharedCanonicalAdapter(Protocol):
    """Provider-neutral boundary for a future shared canonical datastore."""

    @property
    def adapter_id(self) -> str:
        """Stable adapter implementation identifier."""

    @property
    def storage_scope(self) -> StorageScope:
        """Storage class used by this adapter."""


def bind_shared_adapter(
    *,
    config: RuntimeProfileConfig,
    adapter: SharedCanonicalAdapter,
) -> SharedCanonicalAdapter:
    """Validate that a shared profile cannot fall back to local SQLite.

    P18.0 does not connect to or create a datastore.  This function is the
    fail-closed binding guard future shared services must pass before using a
    provider-specific adapter.
    """

    if config.profile is not RuntimeProfile.SHARED_TEAM or not config.shared_enabled:
        raise SharedRuntimeDisabledError(
            "shared adapter binding requires an explicitly enabled shared/team profile"
        )

    if adapter.storage_scope is not StorageScope.SHARED_CANONICAL:
        raise SharedRuntimeBoundaryError(
            "shared/team runtime cannot bind project-local SQLite canonical storage"
        )

    adapter_id = str(adapter.adapter_id).strip()
    if not adapter_id:
        raise SharedRuntimeBoundaryError("shared canonical adapter_id is required")

    return adapter
