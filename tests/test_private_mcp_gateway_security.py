"""Negative security checks for the isolated MCP gateway."""
from fastapi.testclient import TestClient
from kgeopolitical_monitor.private_mcp_gateway_v2 import create_gateway

TOKEN = "x" * 48


def test_invalid_access_does_not_read_state():
    reads = []
    def reader():
        reads.append(1)
        raise AssertionError("unexpected read")
    with TestClient(create_gateway(reader, TOKEN), base_url="http://127.0.0.1:8000") as client:
        assert client.post("/mcp").status_code == 401
        assert client.post("/mcp", headers={"Authorization": "Bearer wrong"}).status_code == 401
        assert client.post("/mcp", headers={"Authorization": "Bearer " + TOKEN,
                           "Origin": "https://invalid.example"}).status_code == 403
        assert client.post("/mcp", headers={"Authorization": "Bearer " + TOKEN},
                           content=b"a" * 4097).status_code == 413
        assert client.get("/mcp", headers={"Authorization": "Bearer " + TOKEN}).status_code == 404
    assert reads == []


def test_duplicate_authorization_denied():
    with TestClient(create_gateway(lambda: None, TOKEN),
                    base_url="http://127.0.0.1:8000") as client:
        response = client.post("/mcp", headers=[
            ("Authorization", "Bearer " + TOKEN),
            ("Authorization", "Bearer " + TOKEN),
        ])
        assert response.status_code == 401


def test_short_token_rejected():
    import pytest
    with pytest.raises(ValueError):
        create_gateway(lambda: None, "short")
