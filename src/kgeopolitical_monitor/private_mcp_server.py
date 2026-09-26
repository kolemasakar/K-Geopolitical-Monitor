"""Official MCP SDK-backed, local-only KGM protocol server.

This factory creates no listener and no production reader. The authenticated
network gateway is a separate, unapproved deployment gate.
"""
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP
from .private_plugin_status import kgm_get_status


def create_private_mcp_server(reader_factory: Callable[[], Any]) -> FastMCP:
    server = FastMCP(
        "KGM Private Owner Status",
        host="127.0.0.1",
        stateless_http=True,
        json_response=True,
        streamable_http_path="/mcp",
        max_request_body_size=4096,
    )

    @server.tool(name="kgm_get_status", description="Read sanitized KGM monitoring status")
    def status() -> dict[str, object]:
        return kgm_get_status(reader_factory())

    return server
