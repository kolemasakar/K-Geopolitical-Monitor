"""Isolated ASGI streamed-body and token lifecycle boundary tests."""
import anyio
from kgeopolitical_monitor.private_mcp_gateway_v2 import create_gateway


def run_request(app, headers, chunks):
    async def scenario():
        messages = iter([
            {"type": "http.request", "body": data, "more_body": i < len(chunks) - 1}
            for i, data in enumerate(chunks)
        ])
        output = []

        async def receive():
            return next(messages)

        async def send(message):
            output.append(message)

        scope = {"type": "http", "method": "POST", "path": "/mcp",
                 "headers": headers, "scheme": "http", "server": ("127.0.0.1", 8000)}
        await app(scope, receive, send)
        return output[0]["status"]
    return anyio.run(scenario)


def test_streamed_oversize_rejected_without_length():
    token = "t" * 48
    reads = []

    def reader():
        reads.append(True)
        raise AssertionError("backend must not be accessed")

    app = create_gateway(reader, token)
    status = run_request(app, [(b"authorization", ("Bearer " + token).encode())],
                         [b"a" * 3000, b"b" * 1097])
    assert status == 413
    assert reads == []


def test_token_replacement_invalidates_old_token_in_new_gateway():
    old = "o" * 48
    new = "n" * 48
    app = create_gateway(lambda: None, new)
    assert run_request(app, [(b"authorization", ("Bearer " + old).encode())],
                       [b"{}"]) == 401


def test_duplicate_authorization_asgi_rejected():
    token = "t" * 48
    app = create_gateway(lambda: None, token)
    header = (b"authorization", ("Bearer " + token).encode())
    assert run_request(app, [header, header], [b"{}"]) == 401
