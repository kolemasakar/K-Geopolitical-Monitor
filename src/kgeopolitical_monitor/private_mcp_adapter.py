"""Isolated, owner-authenticated MCP-style status adapter. Not a public transport."""
import json
import secrets
import threading
import time
from collections import deque
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .private_plugin_status import kgm_get_status

MAX_REQUEST_BYTES = 4096
MAX_RESPONSE_BYTES = 16384
WINDOW_SECONDS = 60
MAX_REQUESTS = 30
TOOL = {"name": "kgm_get_status", "description": "Read bounded sanitized KGM status",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}}


def create_private_mcp_adapter(reader_factory: Callable[[], Any], owner_token: str,
                               audit: Callable[[str], None] | None = None,
                               clock: Callable[[], float] = time.monotonic) -> FastAPI:
    """No listener is started; deployment/transport is a separate approval gate."""
    if not isinstance(owner_token, str) or len(owner_token) < 32:
        raise ValueError("dedicated owner token must be at least 32 characters")
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    attempts: deque[float] = deque()
    lock = threading.Lock()

    def emit(event: str) -> None:
        if audit:
            try:
                audit(event)  # Fixed event codes only; never log request or token.
            except Exception:
                pass

    @app.post("/mcp")
    async def mcp(request: Request) -> JSONResponse:
        authorization = request.headers.get("authorization", "")
        expected = "Bearer " + owner_token
        if not secrets.compare_digest(authorization, expected):
            emit("DENIED_AUTH")
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        if request.headers.get("content-length", "").isdigit() and int(request.headers["content-length"]) > MAX_REQUEST_BYTES:
            emit("DENIED_SIZE")
            return JSONResponse({"error": "request too large"}, status_code=413)
        with lock:
            now = clock()
            while attempts and now - attempts[0] >= WINDOW_SECONDS:
                attempts.popleft()
            if len(attempts) >= MAX_REQUESTS:
                emit("DENIED_RATE")
                return JSONResponse({"error": "rate limit"}, status_code=429)
            attempts.append(now)
        body = await request.body()
        if len(body) > MAX_REQUEST_BYTES:
            emit("DENIED_SIZE")
            return JSONResponse({"error": "request too large"}, status_code=413)
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0":
                raise ValueError()
            request_id = payload.get("id")
            if type(request_id) not in (str, int) or isinstance(request_id, str) and len(request_id) > 96:
                raise ValueError()
            method = payload.get("method")
            if method == "tools/list" and payload.get("params", {}) == {}:
                result = {"tools": [TOOL]}
            elif method == "tools/call" and payload.get("params") == {"name": TOOL["name"], "arguments": {}}:
                result = {"content": [{"type": "text", "text": json.dumps(kgm_get_status(reader_factory()), separators=(",", ":"))}]}
            else:
                emit("DENIED_METHOD")
                return JSONResponse({"jsonrpc": "2.0", "id": request_id,
                                     "error": {"code": -32601, "message": "method unavailable"}})
            output = {"jsonrpc": "2.0", "id": request_id, "result": result}
            if len(json.dumps(output).encode()) > MAX_RESPONSE_BYTES:
                raise ValueError("response bound")
            emit("ALLOWED_LIST" if method == "tools/list" else "ALLOWED_STATUS")
            return JSONResponse(output)
        except (ValueError, TypeError, UnicodeError):
            emit("DENIED_PAYLOAD")
            return JSONResponse({"error": "invalid request"}, status_code=400)
        except Exception:
            emit("FAILED_INTERNAL")
            return JSONResponse({"error": "unavailable"}, status_code=503)
    return app
