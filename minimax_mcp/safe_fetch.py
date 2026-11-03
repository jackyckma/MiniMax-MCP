"""SSRF-safe download for remote HTTP mode.

DNS rebinding is avoided by never looking the name up again at connect time.
The urllib3 pool's TCP destination is the IP we already checked, while TLS SNI,
certificate verification, and the HTTP Host header stay on the original hostname.
"""

from __future__ import annotations

import ipaddress
import socket
import urllib.parse
from dataclasses import dataclass
from functools import partial

import urllib3
from urllib3.connection import HTTPConnection, HTTPSConnection

from minimax_mcp.exceptions import MinimaxRequestError

CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 30
MAX_BYTES = 20 * 1024 * 1024
MAX_REDIRECTS = 3
_READ_CHUNK = 64 * 1024

_ALLOWED_SCHEMES = frozenset({"http", "https"})
_ALLOWED_PORTS = frozenset({80, 443})
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_BLOCKED_SUFFIXES = (".internal", ".local", ".localhost")
_CGNAT = ipaddress.ip_network("100.64.0.0/10")

_REJECTED = (
    "The file URL was rejected. Only public http(s) URLs on ports 80 and 443 can be fetched."
)
_TOO_MANY_REDIRECTS = "The file URL was rejected because it redirected too many times."
_TOO_LARGE = "The file URL was rejected because the download exceeded 20 MB."
_DOWNLOAD_FAILED = "The file URL could not be downloaded."


@dataclass(frozen=True)
class _Target:
    scheme: str
    hostname: str
    port: int
    ip: str
    path: str


class _PinnedHTTPConnection(HTTPConnection):
    def __init__(self, *args, pinned_ip: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._dns_host = pinned_ip


class _PinnedHTTPSConnection(HTTPSConnection):
    def __init__(self, *args, pinned_ip: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._dns_host = pinned_ip


def fetch_public_url(url: str) -> bytes:
    """Download a caller-supplied URL that passed the public-address checks."""
    current = url
    for hop in range(MAX_REDIRECTS + 1):
        target = _resolve_target(current)
        pool = None
        response = None
        try:
            pool, response = _pinned_get(target)
            if response.status in _REDIRECT_STATUSES:
                if hop == MAX_REDIRECTS:
                    raise MinimaxRequestError(_TOO_MANY_REDIRECTS)
                location = response.headers.get("Location")
                if not location or not str(location).strip():
                    raise MinimaxRequestError(_DOWNLOAD_FAILED)
                current = urllib.parse.urljoin(current, str(location).strip())
                continue
            if response.status < 200 or response.status >= 300:
                raise MinimaxRequestError(_DOWNLOAD_FAILED)
            return _read_limited(response)
        except MinimaxRequestError:
            raise
        except Exception:
            raise MinimaxRequestError(_DOWNLOAD_FAILED) from None
        finally:
            if response is not None:
                response.close()
            if pool is not None:
                pool.close()
    raise MinimaxRequestError(_TOO_MANY_REDIRECTS)


def _resolve_target(url: str) -> _Target:
    if not isinstance(url, str) or any(char in url for char in "\r\n\x00"):
        raise MinimaxRequestError(_REJECTED)
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        raise MinimaxRequestError(_REJECTED) from None
    scheme = (parsed.scheme or "").lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise MinimaxRequestError(_REJECTED)
    if parsed.username is not None or parsed.password is not None:
        raise MinimaxRequestError(_REJECTED)
    hostname = parsed.hostname
    if not hostname:
        raise MinimaxRequestError(_REJECTED)
    try:
        port = parsed.port
    except ValueError:
        raise MinimaxRequestError(_REJECTED) from None
    if port is None:
        port = 443 if scheme == "https" else 80
    if port not in _ALLOWED_PORTS:
        raise MinimaxRequestError(_REJECTED)

    hostname = _normalize_hostname(hostname)
    ip = _public_ip_for_host(hostname, port)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return _Target(scheme=scheme, hostname=hostname, port=port, ip=ip, path=path)


def _normalize_hostname(hostname: str) -> str:
    name = hostname.strip().lower().rstrip(".")
    if not name or ".." in name or "/" in name or "\\" in name or "@" in name:
        raise MinimaxRequestError(_REJECTED)
    try:
        ipaddress.ip_address(name)
        return name
    except ValueError:
        pass
    if "." not in name or any(name == suffix.lstrip(".") or name.endswith(suffix) for suffix in _BLOCKED_SUFFIXES):
        raise MinimaxRequestError(_REJECTED)
    try:
        return name.encode("idna").decode("ascii")
    except UnicodeError:
        raise MinimaxRequestError(_REJECTED) from None


def _public_ip_for_host(hostname: str, port: int) -> str:
    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None
    if literal is not None:
        _ensure_public(literal)
        return str(_connect_ip(literal))

    try:
        infos = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        raise MinimaxRequestError(_REJECTED) from None
    if not infos:
        raise MinimaxRequestError(_REJECTED)

    chosen: str | None = None
    for info in infos:
        sockaddr = info[4]
        raw = sockaddr[0]
        if isinstance(raw, str) and "%" in raw:
            raw = raw.split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            raise MinimaxRequestError(_REJECTED) from None
        _ensure_public(ip)
        connect_ip = str(_connect_ip(ip))
        if chosen is None:
            chosen = connect_ip
    if chosen is None:
        raise MinimaxRequestError(_REJECTED)
    return chosen


def _connect_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address):
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return ip.ipv4_mapped
    return ip


def _ensure_public(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    checked = _connect_ip(ip)
    if checked.version == 4 and checked in _CGNAT:
        raise MinimaxRequestError(_REJECTED)
    if (
        checked.is_private
        or checked.is_loopback
        or checked.is_link_local
        or checked.is_multicast
        or checked.is_reserved
        or checked.is_unspecified
        or not checked.is_global
    ):
        raise MinimaxRequestError(_REJECTED)


def _pinned_get(target: _Target):
    timeout = urllib3.Timeout(connect=CONNECT_TIMEOUT_SECONDS, read=READ_TIMEOUT_SECONDS)
    headers = {"Host": _host_header(target), "Accept": "*/*"}
    if target.scheme == "https":
        pool = urllib3.HTTPSConnectionPool(
            target.ip,
            port=target.port,
            timeout=timeout,
            retries=False,
            cert_reqs="CERT_REQUIRED",
            assert_hostname=target.hostname,
            server_hostname=target.hostname,
        )
        pool.ConnectionCls = partial(_PinnedHTTPSConnection, pinned_ip=target.ip)
    else:
        pool = urllib3.HTTPConnectionPool(
            target.ip,
            port=target.port,
            timeout=timeout,
            retries=False,
        )
        pool.ConnectionCls = partial(_PinnedHTTPConnection, pinned_ip=target.ip)
    try:
        response = pool.urlopen(
            "GET",
            target.path,
            headers=headers,
            redirect=False,
            preload_content=False,
            retries=False,
            assert_same_host=False,
        )
    except Exception:
        pool.close()
        raise
    return pool, response


def _host_header(target: _Target) -> str:
    default = 443 if target.scheme == "https" else 80
    if target.port == default:
        return target.hostname
    return f"{target.hostname}:{target.port}"


def _read_limited(response) -> bytes:
    declared = response.headers.get("Content-Length")
    if declared is not None:
        try:
            if int(declared) > MAX_BYTES:
                raise MinimaxRequestError(_TOO_LARGE)
        except ValueError:
            pass
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(_READ_CHUNK, decode_content=False)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_BYTES:
            raise MinimaxRequestError(_TOO_LARGE)
        chunks.append(chunk)
    return b"".join(chunks)
