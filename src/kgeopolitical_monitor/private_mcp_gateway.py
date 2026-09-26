"""Local-only authenticated ASGI gateway for the official KGM MCP SDK app.

This module never binds a socket. The dedicated token and real read-only
reader must be supplied by a separately approved deployment configuration.
"""
import asyncio
import secrets
import time
from collections import deque
from collections.abc import Callable
from typing import Any

from .private_mcp_server import create_private_mcp_server


def create_protected_mcp_app(
    reader_factory: Callable[[], Any],
    owner_token: str,
    audit: Callable[[str], None] | None = None,
    clock: Callable[[], float] = time.monotonic,
    *,
    max_requests: int = 30,
    window_seconds: int = 60,
    max_request_bytes: int = 4096,
):
    if not isinstance(owner_token, str) or len(owner_token) < 32:
        raise ValueError("dedicated owner token must be at least 32 characters")
    if min(max_requests, window_seconds, max_request_bytes) <= 0:
        raise ValueError("positive limits required")
    sdk_app = create_private_mcp_server(reader_factory).streamable_http_app()
    recent: deque[float] = deque()
    lock = asyncio.Lock()

    def emit(code: str) -> None:
        if audit is not None:
            try:
                audit(code)  # fixed event codes only; never include headers or payload
            except Exception:
                pass

    async def reject(send, code: int, body: bytes, event: str):
        emit(event)
        await send({"type": "http.response.start", "status": code,
                    "headers": [(b"content-type", b"text/plain"),
                                (b"content-length", str(len(body)).encode())]})
        await send({"type": "http.response.body", "body": body})

    async def app(scope, receive, send):
        if scope["type"] == "lifespan":
            return await sdk_app(scope, receive, send)
        if scope["type"] != "http":
            return await sdk_app(scope, receive, send)
        if scope.get("path") != "/mcp" or scope.get("method") != "POST":
            return await reject(send, 404, b"not found", "DENIED_ROUTE")
        auth_values = [v for k, v in scope.get("headers", []) if k.lower() == b"authorization"]
        if len(auth_values) != 1 or not secrets.compare_digest(
            auth_values[0], ("Bearer " + owner_token).encode()
        ):
            return await reject(send, 401, b"unauthorized", "DENIED_AUTH")
        lengths = [v for k, v in scope.get("headers", []) if k.lower() == b"content-length"]
        if len(lengths) > 1 or lengths and (not lengths[0].isdigit() or int(lengths[0]) > max_request_bytes):
            return await reject(send, 413, b"request too large", "DENIED_SIZE")
        # Reject unexpected origins: an absent Origin is normal for server clients.
        origins = [v for k, v in scope.get("headers", []) if k.lower() == b"origin"]
        if origins:
            return await reject(send, 403, b"origin forbidden", "DENIED_ORIGIN")
        async with lock:
            now = clock()
            while recent and now - recent[0] >= window_seconds:
                recent.popleft()
            if len(recent) >= max_requests:
                return await reject(send, 429, b"rate limit", "DENIED_RATE")
            recent.append(now)
        size = 0

        async def bounded_receive():
            nonlocal size
            message = await receive()
            if message["type"] == "http.request":
                size += len(message.get("body", b""))
                if size > max_request_bytes:
                    raise _RequestTooLarge()
            return message

        try:
            await sdk_app(scope, bounded_receive, send)
            emit("MCP_REQUEST_FORWARDED")
        except _RequestTooLarge:
            # A request body that omits Content-Length can overflow after the
            # SDK starts responding. Fail closed at a separate buffering gate
            # before forwarding, rather than trying to emit a second response.
            raise

    return app


class _RequestTooLarge(Exception):
    pass
