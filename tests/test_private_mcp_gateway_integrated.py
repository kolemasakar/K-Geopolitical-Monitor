"""Regression checks for authenticated official MCP HTTP gateway."""
from fastapi.testclient import TestClient
from kgeopolitical_monitor.private_mcp_gateway_v2 import create_gateway

TOKEN = "b" * 48
HEADERS = {"Authorization": "Bearer " + TOKEN,
           "Accept": "application/json, text/event-stream",
           "Content-Type": "application/json",
           "MCP-Protocol-Version": "2025-06-18"}
INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "test", "version": "1"}}}


class Reader:
    def state_summary(self):
        return {"active_monitoring_watches": 3}

    def degraded_sources(self):
        return []


def test_auth_and_protocol():
    with TestClient(create_gateway(Reader, TOKEN), base_url="http://127.0.0.1:8000") as c:
        assert c.post("/mcp", json=INIT).status_code == 401
        assert c.post("/mcp", json=INIT, headers={**HEADERS, "Origin": "https://invalid.example"}).status_code == 403
        assert c.post("/mcp", content=b"x" * 5000, headers=HEADERS).status_code == 413
        assert c.get("/openapi.json", headers=HEADERS).status_code == 404
        assert c.post("/mcp", json=INIT, headers=HEADERS).status_code == 200
        result = c.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, headers=HEADERS)
        assert [x["name"] for x in result.json()["result"]["tools"]] == ["kgm_get_status"]
        result = c.post("/mcp", json={"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                        "params": {"name": "kgm_get_status", "arguments": {}}}, headers=HEADERS)
        assert result.status_code == 200
        assert "active_monitoring_watches" in str(result.json()["result"])


def test_rate_limit():
    with TestClient(create_gateway(Reader, TOKEN, clock=lambda: 1.0), base_url="http://127.0.0.1:8000") as c:
        for _ in range(30):
            assert c.post("/mcp", json={}, headers=HEADERS).status_code != 429
        assert c.post("/mcp", json={}, headers=HEADERS).status_code == 429
