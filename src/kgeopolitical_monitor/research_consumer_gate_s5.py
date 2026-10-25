"""S5.3 research-only consumer contract: no transport, no credential handling."""
from collections.abc import Mapping


class ConsumerNotAuthorized(PermissionError):
    pass


def authorize_offline_view(*, consumer_id: str, scope: str, grants: Mapping[str, tuple[str, ...]], mode: str = "NO_SEND") -> None:
    """Fail closed. Validates a purely local view privilege, not a send permit."""
    if mode != "NO_SEND":
        raise ConsumerNotAuthorized("external delivery is not implemented or approved")
    if not isinstance(consumer_id, str) or not consumer_id or not isinstance(scope, str) or not scope:
        raise ConsumerNotAuthorized("missing consumer or scope")
    if not isinstance(grants, Mapping):
        raise ConsumerNotAuthorized("invalid grants")
    permissions = grants.get(consumer_id)
    if not isinstance(permissions, tuple) or scope not in permissions:
        raise ConsumerNotAuthorized("consumer scope not approved")
