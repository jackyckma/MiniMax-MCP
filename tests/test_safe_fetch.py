import socket

import pytest
import urllib3

from minimax_mcp.exceptions import MinimaxRequestError
from minimax_mcp.safe_fetch import (
    MAX_BYTES,
    _Target,
    _pinned_get,
    fetch_public_url,
)
import minimax_mcp.safe_fetch as safe_fetch
import minimax_mcp.server as server


BLOCKED_ADDRESSES = [
    "127.0.0.1",
    "10.0.0.5",
    "172.16.0.1",
    "192.168.1.1",
    "169.254.169.254",
    "100.64.0.1",
    "::1",
    "fd00::1",
    "::ffff:127.0.0.1",
    "0.0.0.0",
]


class _Pool:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class _Response:
    def __init__(self, status, headers=None, chunks=None):
        self.status = status
        self.headers = headers or {}
        self._chunks = list(chunks or [])
        self.closed = False
        self.reads = 0

    def read(self, amt=None, decode_content=False):
        self.reads += 1
        if not self._chunks:
            return b""
        return self._chunks.pop(0)

    def close(self):
        self.closed = True


def _addrinfo(ip: str):
    parsed = ipaddress_family(ip)
    sockaddr = (ip, 0) if parsed == socket.AF_INET else (ip, 0, 0, 0)
    return [(parsed, socket.SOCK_STREAM, 6, "", sockaddr)]


def ipaddress_family(ip: str) -> int:
    if ":" in ip:
        return socket.AF_INET6
    return socket.AF_INET


def _public_dns(host, port, *args, **kwargs):
    assert host == "cdn.example"
    return _addrinfo("1.1.1.1")


@pytest.fixture
def no_network(monkeypatch):
    def fail_dns(*args, **kwargs):
        raise AssertionError(f"unexpected DNS lookup: {args[:2]}")

    def fail_http(target):
        raise AssertionError(f"unexpected HTTP fetch: {target}")

    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", fail_dns)
    monkeypatch.setattr(safe_fetch, "_pinned_get", fail_http)


@pytest.mark.parametrize("address", BLOCKED_ADDRESSES)
def test_literal_blocked_addresses_are_rejected(address, no_network):
    host = f"[{address}]" if ":" in address else address
    with pytest.raises(MinimaxRequestError, match="rejected"):
        fetch_public_url(f"http://{host}/secret")


@pytest.mark.parametrize("address", BLOCKED_ADDRESSES)
def test_hostname_resolving_to_blocked_address_is_rejected(address, monkeypatch):
    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", lambda *args, **kwargs: _addrinfo(address))
    monkeypatch.setattr(
        safe_fetch,
        "_pinned_get",
        lambda target: (_ for _ in ()).throw(AssertionError("connected")),
    )
    with pytest.raises(MinimaxRequestError, match="rejected"):
        fetch_public_url("https://cdn.example/clip.mp3")


@pytest.mark.parametrize(
    "hostname",
    ["foo.internal", "localhost", "intranet", "foo.local", "bar.localhost", "LOCALHOST"],
)
def test_blocked_hostnames_skip_dns(hostname, no_network):
    with pytest.raises(MinimaxRequestError, match="rejected"):
        fetch_public_url(f"https://{hostname}/clip.mp3")


@pytest.mark.parametrize(
    "url",
    [
        "https://cdn.example:8443/clip.mp3",
        "http://cdn.example:8080/clip.mp3",
        "http://1.1.1.1:8080/clip.mp3",
        "https://cdn.example:22/clip.mp3",
    ],
)
def test_non_standard_ports_are_rejected(url, no_network):
    with pytest.raises(MinimaxRequestError, match="rejected"):
        fetch_public_url(url)


def test_redirect_to_private_ip_is_not_fetched(monkeypatch):
    def dns(host, port, *args, **kwargs):
        assert host == "cdn.example"
        return _addrinfo("1.1.1.1")

    calls = []

    def pinned(target):
        calls.append(target)
        response = _Response(302, {"Location": "http://169.254.169.254/latest/meta-data"})
        return _Pool(), response

    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", dns)
    monkeypatch.setattr(safe_fetch, "_pinned_get", pinned)
    with pytest.raises(MinimaxRequestError, match="rejected"):
        fetch_public_url("https://cdn.example/clip.mp3")
    assert [target.ip for target in calls] == ["1.1.1.1"]
    assert calls[0].hostname == "cdn.example"


def test_more_than_three_redirects_are_rejected(monkeypatch):
    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", _public_dns)
    calls = []

    def pinned(target):
        calls.append(target.path)
        response = _Response(302, {"Location": f"https://cdn.example/hop-{len(calls)}"})
        return _Pool(), response

    monkeypatch.setattr(safe_fetch, "_pinned_get", pinned)
    with pytest.raises(MinimaxRequestError, match="redirected too many times"):
        fetch_public_url("https://cdn.example/start")
    assert len(calls) == 4


def test_three_redirects_then_public_body(monkeypatch):
    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", _public_dns)
    calls = []

    def pinned(target):
        calls.append(target.ip)
        if len(calls) <= 3:
            response = _Response(302, {"Location": "https://cdn.example/next"})
        else:
            response = _Response(200, {}, [b"audio-bytes"])
        return _Pool(), response

    monkeypatch.setattr(safe_fetch, "_pinned_get", pinned)
    assert fetch_public_url("https://cdn.example/start") == b"audio-bytes"
    assert calls == ["1.1.1.1", "1.1.1.1", "1.1.1.1", "1.1.1.1"]


def test_oversize_body_is_aborted_and_closed(monkeypatch):
    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", _public_dns)
    response = _Response(200, {}, [b"a" * (MAX_BYTES + 1)])
    pool = _Pool()
    monkeypatch.setattr(safe_fetch, "_pinned_get", lambda target: (pool, response))
    with pytest.raises(MinimaxRequestError, match="20 MB"):
        fetch_public_url("https://cdn.example/huge.mp3")
    assert response.closed is True
    assert pool.closed is True


def test_declared_content_length_over_cap_is_rejected(monkeypatch):
    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", _public_dns)
    response = _Response(200, {"Content-Length": str(MAX_BYTES + 1)}, [b"small"])
    monkeypatch.setattr(safe_fetch, "_pinned_get", lambda target: (_Pool(), response))
    with pytest.raises(MinimaxRequestError, match="20 MB"):
        fetch_public_url("https://cdn.example/huge.mp3")
    assert response.reads == 0
    assert response.closed is True


def test_mixed_public_and_private_resolution_is_rejected(monkeypatch):
    def dns(host, port, *args, **kwargs):
        return _addrinfo("1.1.1.1") + _addrinfo("10.0.0.5")

    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", dns)
    monkeypatch.setattr(
        safe_fetch,
        "_pinned_get",
        lambda target: (_ for _ in ()).throw(AssertionError("connected")),
    )
    with pytest.raises(MinimaxRequestError, match="rejected"):
        fetch_public_url("https://cdn.example/clip.mp3")


def test_public_https_url_downloads_pinned_body(monkeypatch):
    seen = []

    def dns(host, port, family, socktype, *args, **kwargs):
        assert host == "cdn.example"
        assert port == 443
        assert family == socket.AF_UNSPEC
        assert socktype == socket.SOCK_STREAM
        return _addrinfo("1.1.1.1")

    def pinned(target):
        seen.append(target)
        response = _Response(200, {}, [b"ID3", b"fake"])
        return _Pool(), response

    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", dns)
    monkeypatch.setattr(safe_fetch, "_pinned_get", pinned)
    body = fetch_public_url("https://cdn.example/voice.mp3?x=1")
    assert body == b"ID3fake"
    assert seen[0] == _Target("https", "cdn.example", 443, "1.1.1.1", "/voice.mp3?x=1")


def test_connection_is_pinned_to_resolved_ip(monkeypatch):
    created = {}

    class SpyPool(urllib3.HTTPSConnectionPool):
        def __init__(self, host, port=None, **kwargs):
            created["host"] = host
            created["port"] = port
            created["kwargs"] = kwargs
            super().__init__(host, port, **kwargs)

        def urlopen(self, method, url, **kwargs):
            created["headers"] = kwargs.get("headers")
            created["redirect"] = kwargs.get("redirect")
            created["preload_content"] = kwargs.get("preload_content")
            created["connection_cls"] = self.ConnectionCls
            raise RuntimeError("stop-before-connect")

    monkeypatch.setattr(safe_fetch.urllib3, "HTTPSConnectionPool", SpyPool)
    target = _Target("https", "cdn.example", 443, "1.1.1.1", "/voice.mp3")
    with pytest.raises(RuntimeError, match="stop-before-connect"):
        _pinned_get(target)

    assert created["host"] == "1.1.1.1"
    assert created["port"] == 443
    assert created["kwargs"]["assert_hostname"] == "cdn.example"
    assert created["kwargs"]["server_hostname"] == "cdn.example"
    assert created["kwargs"]["timeout"].connect_timeout == 10
    assert created["kwargs"]["timeout"].read_timeout == 30
    assert created["headers"]["Host"] == "cdn.example"
    assert created["redirect"] is False
    assert created["preload_content"] is False
    connection = created["connection_cls"](
        host="cdn.example",
        port=443,
        timeout=10,
        server_hostname="cdn.example",
    )
    assert connection._dns_host == "1.1.1.1"
    assert connection.server_hostname == "cdn.example"


def test_http_connection_is_pinned_to_resolved_ip(monkeypatch):
    created = {}

    class SpyPool(urllib3.HTTPConnectionPool):
        def __init__(self, host, port=None, **kwargs):
            created["host"] = host
            created["port"] = port
            created["kwargs"] = kwargs
            super().__init__(host, port, **kwargs)

        def urlopen(self, method, url, **kwargs):
            created["headers"] = kwargs.get("headers")
            created["connection_cls"] = self.ConnectionCls
            raise RuntimeError("stop-before-connect")

    monkeypatch.setattr(safe_fetch.urllib3, "HTTPConnectionPool", SpyPool)
    target = _Target("http", "cdn.example", 80, "1.1.1.1", "/voice.mp3")
    with pytest.raises(RuntimeError, match="stop-before-connect"):
        _pinned_get(target)
    assert created["host"] == "1.1.1.1"
    assert created["port"] == 80
    assert created["headers"]["Host"] == "cdn.example"
    connection = created["connection_cls"](host="cdn.example", port=80, timeout=10)
    assert connection._dns_host == "1.1.1.1"


def test_voice_clone_remote_rejects_loopback_without_api_call(monkeypatch):
    previous = server.resource_mode
    monkeypatch.setenv("MINIMAX_MCP_REMOTE_HTTP", "1")
    server.apply_remote_http_safety()
    monkeypatch.setattr(server.api_client, "post", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("api")))
    try:
        result = server.voice_clone("voice-1", "http://127.0.0.1/a.mp3", "hello")
    finally:
        server.resource_mode = previous
    assert "rejected" in result.text.lower()
    assert "127.0.0.1" not in result.text


def test_stdio_url_upload_still_uses_requests_stream(monkeypatch):
    monkeypatch.delenv("MINIMAX_MCP_REMOTE_HTTP", raising=False)
    previous = server.resource_mode
    server.resource_mode = "url"

    def reject_safe_fetch(url):
        raise AssertionError(f"stdio used safe fetch for {url}")

    class Raw:
        def __init__(self):
            self._buffer = b"stdio-bytes"

        def read(self, *args, **kwargs):
            return self._buffer

    class Download:
        raw = Raw()

        def raise_for_status(self):
            return None

    seen = {}

    def fake_get(url, **kwargs):
        seen["url"] = url
        seen["kwargs"] = kwargs
        return Download()

    def fake_post(path, **kwargs):
        if path == "/v1/files/upload":
            assert kwargs["files"]["file"][1] is Download.raw or kwargs["files"]["file"][1].__class__ is Raw
            return {"file": {"file_id": "file-1"}}
        assert path == "/v1/voice_clone"
        return {}

    monkeypatch.setattr(server, "fetch_public_url", reject_safe_fetch)
    monkeypatch.setattr(server.requests, "get", fake_get)
    monkeypatch.setattr(server.api_client, "post", fake_post)
    try:
        result = server.voice_clone("voice-1", "https://example.com/a.mp3", "hello", is_url=True)
    finally:
        server.resource_mode = previous
    assert seen["url"] == "https://example.com/a.mp3"
    assert seen["kwargs"] == {"stream": True}
    assert "Voice cloned successfully" in result.text
