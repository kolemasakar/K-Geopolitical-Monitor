"""Localhost-free ASGI test of official MCP Streamable HTTP transport.

No production listener, credentials, or external network access is used.
"""
from fastapi.testclient import TestClient

from kgeopolitical_monitor.private_mcp_server import create_private_mcp_server


class Reader:
    def state_summary(self):
        return {"active_monitoring_watches": 2}

    def degraded_sources(self):
        return []


def test_streamable_http_initialize_discover_and_call():
    server = create_private_mcp_server(Reader)
    app = server.streamable_http_app()
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": "2025-06-18",
    }
    with TestClient(app, base_url="http://127.0.0.1") as client:
        initialized = client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "kgm-local-test", "version": "0.1"},
            },
        })
        assert initialized.status_code == 200, initialized.text
        assert initialized.json()["result"]["serverInfo"]["name"] == "KGM Private Owner Status"
        session = initialized.headers.get("mcp-session-id")
        if session:
            headers["Mcp-Session-Id"] = session
        discovered = client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {},
        })
        assert discovered.status_code == 200, discovered.text
        assert [item["name"] for item in discovered.json()["result"]["tools"]] == ["kgm_get_status"]
        called = client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "kgm_get_status", "arguments": {}},
        })
        assert called.status_code == 200, called.text
        assert not called.json()["result"].get("isError", False)
        assert "active_monitoring_watches" in str(called.json()["result"])
