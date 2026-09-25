#!/usr/bin/env python3
"""Non-public HTTPS CONNECT relay for the dedicated KGM government.ru VPN node.

This process binds ONLY to the designated WireGuard address; its caller must
arrive from the single KGM WireGuard peer. It is not an exit node, web cache,
HTTP downloader, or a general-purpose proxy. Keep the cloud firewall closed.
TLS certificate verification stays with the KGM HTTPS client.
"""
from __future__ import annotations

import selectors
import socket
import socketserver
from threading import BoundedSemaphore

BIND_IP = "10.254.90.1"
ALLOWED_CLIENT = "10.254.90.2"
PORT = 18180
ALLOWED_CONNECT_TARGETS = frozenset({
    ("government.ru", 443),
    ("services.government.ru", 443),
})
MAX_HEADER_BYTES = 4096
MAX_ACTIVE_CLIENTS = 2
MAX_TUNNEL_BYTES_PER_DIRECTION = 2_100_000
IDLE_TIMEOUT_SECONDS = 30
CONNECT_TIMEOUT_SECONDS = 8


def parse_connect_request(head: bytes) -> tuple[str, int]:
    """Allow only exact canonical first-party TLS hostnames at port 443."""
    if len(head) > MAX_HEADER_BYTES or not head.endswith(b"\r\n\r\n"):
        raise ValueError("malformed or oversized CONNECT headers")
    try:
        lines = head[:-4].decode("ascii", errors="strict").split("\r\n")
        tokens = lines[0].split()
        if len(tokens) != 3 or tokens[0] != "CONNECT":
            raise ValueError("CONNECT method required")
        if tokens[2] not in ("HTTP/1.0", "HTTP/1.1"):
            raise ValueError("unsupported HTTP version")
        authority = tokens[1].lower()
        if authority.count(":") != 1:
            raise ValueError("host:port authority required")
        hostname, raw_port = authority.split(":")
        if not raw_port.isascii() or not raw_port.isdecimal():
            raise ValueError("numeric port required")
        target = (hostname, int(raw_port))
        if target not in ALLOWED_CONNECT_TARGETS:
            raise ValueError("target outside official allowlist")
        for line in lines[1:]:
            if not line:
                raise ValueError("unexpected internal empty header")
            key, sep, value = line.partition(":")
            if not sep:
                raise ValueError("invalid header")
            if key.lower() == "proxy-authorization":
                raise ValueError("no proxy credentials accepted")
            if key.lower() == "host" and value.strip().lower() != authority:
                raise ValueError("Host and CONNECT authority disagree")
        return target
    except (UnicodeError, OverflowError) as exc:
        raise ValueError("invalid CONNECT request encoding") from exc


def relay_bounded(client: socket.socket, upstream: socket.socket) -> None:
    """Bidirectional TLS bytes only; byte cap and idle timeout fail closed."""
    amounts = {client: 0, upstream: 0}
    selector = selectors.DefaultSelector()
    try:
        selector.register(client, selectors.EVENT_READ, upstream)
        selector.register(upstream, selectors.EVENT_READ, client)
        while True:
            events = selector.select(timeout=IDLE_TIMEOUT_SECONDS)
            if not events:
                return
            for key, _ in events:
                source, destination = key.fileobj, key.data
                data = source.recv(8192)
                if not data:
                    return
                amounts[source] += len(data)
                if amounts[source] > MAX_TUNNEL_BYTES_PER_DIRECTION:
                    return
                destination.sendall(data)
    finally:
        selector.close()


class OnlyOfficialConnect(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        client = self.request
        if self.client_address[0] != ALLOWED_CLIENT:
            return
        if not self.server.slots.acquire(blocking=False):
            return
        try:
            client.settimeout(5)
            head = bytearray()
            while not head.endswith(b"\r\n\r\n"):
                next_byte = client.recv(1)
                if not next_byte or len(head) >= MAX_HEADER_BYTES:
                    raise ValueError("incomplete or oversized CONNECT request")
                head.extend(next_byte)
            target = parse_connect_request(bytes(head))
            try:
                upstream = socket.create_connection(target, timeout=CONNECT_TIMEOUT_SECONDS)
            except OSError:
                client.sendall(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n")
                return
            with upstream:
                client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                client.settimeout(None)
                upstream.settimeout(None)
                relay_bounded(client, upstream)
        except (ValueError, OSError):
            try:
                client.sendall(b"HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n")
            except OSError:
                pass
        finally:
            self.server.slots.release()


class RestrictedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 3

    def __init__(self) -> None:
        self.slots = BoundedSemaphore(MAX_ACTIVE_CLIENTS)
        super().__init__((BIND_IP, PORT), OnlyOfficialConnect)


def main() -> None:
    with RestrictedServer() as server:
        server.serve_forever(poll_interval=1)


if __name__ == "__main__":
    main()
