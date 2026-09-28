"""Bounded owner-authenticated ASGI wrapper for local MCP SDK tests."""
import asyncio
import secrets
import time
from collections import deque

from .private_mcp_server import create_private_mcp_server


def create_gateway(reader_factory, owner_token, audit=None, clock=time.monotonic):
    if not isinstance(owner_token, str) or len(owner_token) < 32:
        raise ValueError("invalid token configuration")
    sdk = create_private_mcp_server(reader_factory).streamable_http_app()
    recent = deque()
    lock = asyncio.Lock()

    def log(event):
        if audit:
            try:
                audit(event)
            except Exception:
                pass

    async def app(scope, receive, send):
        if scope["type"] != "http":
            return await sdk(scope, receive, send)

        async def deny(code, event):
            log(event)
            body = b"request denied"
            await send({"type": "http.response.start", "status": code,
                        "headers": [(b"content-type", b"text/plain")]})
            await send({"type": "http.response.body", "body": body})

        if scope.get("method") != "POST" or scope.get("path") != "/mcp":
            return await deny(404, "DENIED_ROUTE")
        headers = scope.get("headers", [])
        auth = [v for k, v in headers if k.lower() == b"authorization"]
        if len(auth) != 1 or not secrets.compare_digest(auth[0], ("Bearer " + owner_token).encode()):
            return await deny(401, "DENIED_AUTH")
        if any(k.lower() == b"origin" for k, _ in headers):
            return await deny(403, "DENIED_ORIGIN")
        lengths = [v for k, v in headers if k.lower() == b"content-length"]
        if len(lengths) > 1 or lengths and (not lengths[0].isdigit() or int(lengths[0]) > 4096):
            return await deny(413, "DENIED_SIZE")
        async with lock:
            now = clock()
            while recent and now - recent[0] >= 60:
                recent.popleft()
            if len(recent) >= 30:
                return await deny(429, "DENIED_RATE")
            recent.append(now)
        chunks = []
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                return await deny(400, "DENIED_PAYLOAD")
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > 4096:
                return await deny(413, "DENIED_SIZE")
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        body = b"".join(chunks)
        delivered = False

        async def buffered_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        await sdk(scope, buffered_receive, send)
        log("MCP_FORWARDED")

    return app
