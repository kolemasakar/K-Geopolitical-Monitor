"""P23.4 free foreign VPN relay is allowlisted and non-activating."""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "ops/p23_4_govru_free_vpn/official_connect_proxy.py"
spec = importlib.util.spec_from_file_location("govru_connect", FILE)
proxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxy)


def head(authority: str, method: str = "CONNECT", headers: str = "") -> bytes:
    return (
        f"{method} {authority} HTTP/1.1\r\nHost: {authority}\r\n"
        f"{headers}\r\n"
    ).encode("ascii")


def test_only_two_exact_official_https_targets_permitted():
    assert proxy.parse_connect_request(head("government.ru:443")) == ("government.ru", 443)
    assert proxy.parse_connect_request(head("services.government.ru:443")) == (
        "services.government.ru", 443
    )
    assert proxy.ALLOWED_CONNECT_TARGETS == frozenset({
        ("government.ru", 443), ("services.government.ru", 443)
    })


@pytest.mark.parametrize("target", [
    "government.ru:80",
    "government.ru.evil.example:443",
    "1.1.1.1:443",
    "localhost:443",
    "www.government.ru:443",
    "government.ru:444",
    "user@government.ru:443",
    "[::1]:443",
])
def test_unknown_or_downgraded_egress_fails_closed(target):
    with pytest.raises(ValueError):
        proxy.parse_connect_request(head(target))


def test_http_method_and_credentials_rejected():
    with pytest.raises(ValueError):
        proxy.parse_connect_request(head("government.ru:443", method="GET"))
    with pytest.raises(ValueError):
        proxy.parse_connect_request(head("government.ru:443", headers="Proxy-Authorization: token\r\n"))


def test_malformed_or_oversized_requests_rejected():
    for request in (
        b"CONNECT government.ru:443 HTTP/1.1\r\n",
        b"CONNECT government.ru:443 HTTP/1.1\r\nHost: evil.example:443\r\n\r\n",
        head("government.ru:443") + b"x" * 4096,
    ):
        with pytest.raises(ValueError):
            proxy.parse_connect_request(request)


def test_never_binds_publicly_or_redirects_entire_host():
    assert proxy.BIND_IP == "10.254.90.1"
    assert proxy.ALLOWED_CLIENT == "10.254.90.2"
    assert proxy.PORT == 18180
    assert proxy.MAX_ACTIVE_CLIENTS == 2
    assert proxy.MAX_TUNNEL_BYTES_PER_DIRECTION <= 2_100_000


def test_existing_canonical_source_remains_governance_blocked():
    from kgeopolitical_monitor.p22_3_b1_source_pack import (
        B1_REPOSITORY_ACTIVE_SOURCE_IDS, b1_by_id
    )
    assert "russian-government-news-ru" not in B1_REPOSITORY_ACTIVE_SOURCE_IDS
    assert b1_by_id()["russian-government-news-ru"].endpoint == "https://government.ru/news/"
