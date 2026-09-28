"""Official MCP SDK initialize/discover/call contract without network listeners."""
import anyio
from mcp import ClientSession
from mcp.shared.memory import create_client_server_memory_streams
from kgeopolitical_monitor.private_mcp_server import create_private_mcp_server


class Reader:
    def state_summary(self):
        return {"active_monitoring_watches": 2}

    def degraded_sources(self):
        return []


async def _protocol_check():
    server = create_private_mcp_server(Reader)
    async with create_client_server_memory_streams() as (client_streams, server_streams):
        async with anyio.create_task_group() as group:
            async def serve():
                await server._mcp_server.run(
                    *server_streams,
                    server._mcp_server.create_initialization_options(),
                )
            group.start_soon(serve)
            async with ClientSession(*client_streams) as client:
                initialized = await client.initialize()
                assert initialized.serverInfo.name == "KGM Private Owner Status"
                tools = await client.list_tools()
                assert [tool.name for tool in tools.tools] == ["kgm_get_status"]
                result = await client.call_tool("kgm_get_status", {})
                assert not result.isError
                assert "active_monitoring_watches" in str(result)
                denied = await client.call_tool("not_allowlisted", {})
                assert denied.isError
            group.cancel_scope.cancel()


def test_official_mcp_protocol():
    anyio.run(_protocol_check)
