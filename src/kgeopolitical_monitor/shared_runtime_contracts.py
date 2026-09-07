from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable


class RuntimeProfile(str, Enum):
    """Explicit runtime profile selector.

    LOCAL preserves the validated owner-only project-local runtime.
    SHARED is a separate Phase 18 profile and is disabled unless explicitly enabled.
    """

    LOCAL = "local"
    SHARED = "shared"


class SharedRuntimeContractError(ValueError):
    """Base error for fail-closed Phase 18 contract validation."""


class SharedRuntimeDisabledError(SharedRuntimeContractError):
    """Raised when shared profile selection is attempted while disabled."""


class TenantContextError(SharedRuntimeContractError):
    """Raised when a shared operation lacks an unambiguous tenant context."""


def _require_identifier(value: str | None, *, field: str) -> str:
    if value is None:
        raise TenantContextError(f"{field} is required")
    normalized = value.strip()
    if not normalized:
        raise TenantContextError(f"{field} must be non-empty")
    if normalized in {"*", "all", "default"}:
        raise TenantContextError(f"{field} is ambiguous")
    return normalized


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Mandatory security scope for every shared canonical operation."""

    workspace_id: str
    project_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "workspace_id",
            _require_identifier(self.workspace_id, field="workspace_id"),
        )
        object.__setattr__(
            self,
            "project_id",
            _require_identifier(self.project_id, field="project_id"),
        )

    @classmethod
    def from_optional(
        cls,
        *,
        workspace_id: str | None,
        project_id: str | None,
    ) -> "TenantContext":
        return cls(
            workspace_id=_require_identifier(workspace_id, field="workspace_id"),
            project_id=_require_identifier(project_id, field="project_id"),
        )


@dataclass(frozen=True, slots=True)
class SharedRuntimeSettings:
    """Provider-neutral configuration boundary for Phase 18 runtime selection.

    Shared runtime remains disabled by default. P18.0 deliberately carries no
    provider endpoint, credentials, database URL, or local SQLite path.
    """

    profile: RuntimeProfile = RuntimeProfile.LOCAL
    shared_enabled: bool = False

    def resolve_profile(self) -> RuntimeProfile:
        if self.profile is RuntimeProfile.SHARED and not self.shared_enabled:
            raise SharedRuntimeDisabledError(
                "shared runtime profile is disabled; explicit enablement is required"
            )
        return self.profile


@dataclass(frozen=True, slots=True)
class SharedOperationContext:
    """Explicit scope supplied to provider-neutral shared-runtime adapters."""

    tenant: TenantContext
    correlation_id: str | None = None


@runtime_checkable
class SharedRuntimeAdapter(Protocol):
    """Provider-neutral adapter contract for future shared canonical storage.

    Concrete datastore/provider integration is intentionally outside P18.0.
    """

    def healthcheck(self) -> bool: ...

    def read(self, *, context: SharedOperationContext, object_id: str) -> object: ...

    def write(
        self,
        *,
        context: SharedOperationContext,
        object_id: str,
        value: object,
    ) -> None: ...


def require_shared_context(context: SharedOperationContext | None) -> SharedOperationContext:
    """Fail closed when a shared canonical operation lacks tenant scope."""

    if context is None:
        raise TenantContextError("shared operation requires tenant context")
    # Reconstructing validates that adapter callers cannot smuggle mutable or
    # partially initialized tenant-like state through this boundary.
    TenantContext(
        workspace_id=context.tenant.workspace_id,
        project_id=context.tenant.project_id,
    )
    return context
