"""Explicitly bounded owner-only source transport for proposed on-demand P4 pilot.

In-process limits are defense in depth, not network namespace enforcement.
No network request is made by constructing this class.
"""
from __future__ import annotations

from dataclasses import dataclass
import socket
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

from .live_sources import HttpResponse

APPROVED_ENDPOINTS = frozenset({
    ("api.gdeltproject.org", "/api/v2/doc/doc"),
    ("www.consilium.europa.eu", "/en/rss/pressreleases.ashx"),
    ("www.gdacs.org", "/xml/rss.xml"),
})


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("source redirect refused")


@dataclass(frozen=True)
class RestrictedSourcePolicy:
    max_requests: int = 2
    timeout_seconds: float = 7.0
    max_bytes_per_response: int = 512_000
    gdacs_max_bytes_per_response: int | None = None
    gdelt_timeout_seconds: float | None = None

    def __post_init__(self):
        if not 1 <= self.max_requests <= 5:
            raise ValueError("request cap out of bounds")
        if not 0 < self.timeout_seconds <= 15:
            raise ValueError("timeout out of bounds")
        if not 1 <= self.max_bytes_per_response <= 2_000_000:
            raise ValueError("response cap out of bounds")
        if self.gdacs_max_bytes_per_response is not None and not (
            self.max_bytes_per_response <= self.gdacs_max_bytes_per_response <= 2_000_000
        ):
            raise ValueError("GDACS dedicated cap out of bounds")
        if self.gdelt_timeout_seconds is not None and not (
            self.timeout_seconds <= self.gdelt_timeout_seconds <= 15
        ):
            raise ValueError("GDELT timeout out of bounds")


def validate_source_url(url: str) -> None:
    try:
        p = urlsplit(url)
        port = p.port
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid source URL") from exc
    if (p.scheme != "https" or p.username is not None or p.password is not None
            or port not in (None, 443)
            or (p.hostname, p.path) not in APPROVED_ENDPOINTS
            or p.fragment):
        raise ValueError("source endpoint not allowlisted")


class RestrictedSourceTransport:
    """One-request-budget transport; no following HTTP redirects or env proxies.

    Requires a separate isolated execution container and explicit owner consent
    before live external use. DNS/rebinding and network policy remain out of scope.
    """
    def __init__(self, policy: RestrictedSourcePolicy):
        self.policy = policy
        self.calls = 0
        # Explicitly disable proxies, including ambient HTTPS_PROXY.
        self._opener = build_opener(ProxyHandler({}), HTTPSHandler(), _NoRedirect())

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> HttpResponse:
        validate_source_url(url)
        if self.calls >= self.policy.max_requests:
            raise RuntimeError("one-shot request budget exhausted")
        if headers and any(k.casefold() in ("authorization", "cookie", "proxy-authorization")
                           for k in headers):
            raise ValueError("credential headers forbidden in public source retrieval")
        self.calls += 1
        request = Request(url, headers=headers or {}, method="GET")
        try:
            timeout = (self.policy.gdelt_timeout_seconds
                   if urlsplit(url).hostname == "api.gdeltproject.org"
                   and self.policy.gdelt_timeout_seconds is not None
                   else self.policy.timeout_seconds)
            with self._opener.open(request, timeout=timeout) as response:
                cap = (self.policy.gdacs_max_bytes_per_response
                       if urlsplit(url).hostname == "www.gdacs.org"
                       and self.policy.gdacs_max_bytes_per_response is not None
                       else self.policy.max_bytes_per_response)
                body = response.read(cap + 1)
                if len(body) > cap:
                    raise RuntimeError("source response exceeds configured bound")
                return HttpResponse(body=body, content_type=response.headers.get("Content-Type", ""))
        except HTTPError as exc:
            raise RuntimeError(f"source_http_status_{exc.code}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise RuntimeError("source_network_timeout") from exc
        except ssl.SSLError as exc:
            raise RuntimeError("source_network_tls_failure") from exc
        except URLError as exc:
            reason = exc.reason
            if isinstance(reason, socket.gaierror):
                code = "source_network_dns_failure"
            elif isinstance(reason, (TimeoutError, socket.timeout)):
                code = "source_network_timeout"
            elif isinstance(reason, ssl.SSLError):
                code = "source_network_tls_failure"
            elif isinstance(reason, (ConnectionError, ConnectionRefusedError)):
                code = "source_network_connect_failure"
            else:
                code = "source_network_failure"
            raise RuntimeError(code) from exc
