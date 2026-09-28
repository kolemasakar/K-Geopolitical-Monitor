"""Security tests for isolated owner-only MCP-style adapter."""
import json

from fastapi.testclient import TestClient
from kgeopolitical_monitor.private_mcp_adapter import create_private_mcp_adapter

TOKEN = "a" * 48
STATUS = {"active_monitoring_watches": 1, "last_monitoring_cycle": None,
          "last_unattended_cycle_at": None, "unattended_cycle_instrumentation": "UNKNOWN"}


class Reader:
    def state_summary(self):
        return STATUS

    def degraded_sources(self):
        return []


def call(client, method="tools/call", params=None, token=TOKEN, request_id=1):
    if params is None:
        params = {"name": "kgm_get_status", "arguments": {}}
    return client.post("/mcp", headers={"Authorization": "Bearer " + token},
                       json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})


def test_owner_status_and_allowlist():
    events = []
    client = TestClient(create_private_mcp_adapter(Reader, TOKEN, events.append))
    listed = call(client, "tools/list", {})
    assert listed.status_code == 200
    assert [tool["name"] for tool in listed.json()["result"]["tools"]] == ["kgm_get_status"]
    response = call(client)
    assert response.status_code == 200
    value = json.loads(response.json()["result"]["content"][0]["text"])
    assert value["active_monitoring_watches"] == 1
    assert value["service_health"] == "NOT_MEASURED"
    assert events == ["ALLOWED_LIST", "ALLOWED_STATUS"]


def test_denial_no_reader_execution():
    executed = []
    def forbidden_reader():
        executed.append(1)
        raise AssertionError("reader must not be invoked")
    events = []
    client = TestClient(create_private_mcp_adapter(forbidden_reader, TOKEN, events.append))
    assert call(client, token="wrong").status_code == 401
    assert client.post("/mcp", json={}).status_code == 401
    assert call(client, params={"name": "shell", "arguments": {}}).json()["error"]["code"] == -32601
    assert call(client, params={"name": "kgm_get_status", "arguments": {"sql": "select *"}}).json()["error"]["code"] == -32601
    assert client.get("/openapi.json").status_code == 404
    assert client.get("/docs").status_code == 404
    assert executed == []
    assert events == ["DENIED_AUTH", "DENIED_AUTH", "DENIED_METHOD", "DENIED_METHOD"]


def test_request_and_response_bounds_and_errors():
    client = TestClient(create_private_mcp_adapter(Reader, TOKEN))
    assert client.post("/mcp", headers={"Authorization": "Bearer " + TOKEN},
                       content=b"x" * 5000).status_code == 413
    assert client.post("/mcp", headers={"Authorization": "Bearer " + TOKEN},
                       content=b"invalid").status_code == 400
    def broken():
        raise RuntimeError("secret backend details")
    error = call(TestClient(create_private_mcp_adapter(broken, TOKEN)))
    assert error.status_code == 503
    assert "secret" not in error.text


def test_rate_limit_and_secret_free_audit():
    events = []
    client = TestClient(create_private_mcp_adapter(Reader, TOKEN, events.append, clock=lambda: 10.0))
    for _ in range(30):
        assert call(client, "tools/list", {}).status_code == 200
    assert call(client, "tools/list", {}).status_code == 429
    assert events[-1] == "DENIED_RATE"
    assert TOKEN not in repr(events)


def test_invalid_token_configuration():
    try:
        create_private_mcp_adapter(Reader, "short")
    except ValueError:
        pass
    else:
        raise AssertionError("short token accepted")
