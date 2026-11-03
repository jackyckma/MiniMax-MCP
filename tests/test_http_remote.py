import os
import socket
import threading

import anyio
import httpx2
import pytest
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from starlette.testclient import TestClient

from minimax_mcp.const import (
    ENV_MCP_REMOTE_HTTP,
    configured_speech_model,
    configured_t2i_model,
    configured_t2v_model,
)
from minimax_mcp.exceptions import MinimaxMcpError
from minimax_mcp.http_transport import (
    prepare_http_runtime,
    resolve_http_allowlist,
    resolve_transport,
    tokens_match,
)
from minimax_mcp.server import HTTP_DEFAULT_ALLOWLIST
from minimax_mcp.utils import build_output_path, play, process_input_file
import minimax_mcp.http_transport as http_transport
import minimax_mcp.server as server


HTTP_TOOL_NAMES = set(HTTP_DEFAULT_ALLOWLIST)


@pytest.fixture(autouse=True)
def restore_remote_state():
    mode = server.resource_mode
    remote = os_remote()
    yield
    server.resource_mode = mode
    if remote is None:
        os.environ.pop(ENV_MCP_REMOTE_HTTP, None)
    else:
        os.environ[ENV_MCP_REMOTE_HTTP] = remote


def os_remote():
    return os.environ.get(ENV_MCP_REMOTE_HTTP)


def _app(monkeypatch, token="test-token", allowlist=None):
    monkeypatch.setenv("MCP_SERVER_TOKEN", token)
    monkeypatch.setenv("MINIMAX_API_KEY", "test-api-key")
    monkeypatch.setenv("MINIMAX_API_HOST", "https://api.example.invalid")
    if allowlist is None:
        monkeypatch.delenv("MINIMAX_MCP_ALLOWED_TOOLS", raising=False)
    else:
        monkeypatch.setenv("MINIMAX_MCP_ALLOWED_TOOLS", allowlist)
    app, _port = prepare_http_runtime()
    return app


def test_health_is_open_and_mcp_requires_bearer(monkeypatch):
    app = _app(monkeypatch, token="test-token")
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        health_with_bad_token = client.get("/health", headers={"Authorization": "Bearer nope"})
        assert health_with_bad_token.status_code == 200

        missing = client.get("/mcp")
        assert missing.status_code == 401
        assert missing.json()["error"] == "unauthorized"

        wrong = client.get("/mcp", headers={"Authorization": "Bearer wrong-token"})
        assert wrong.status_code == 401

        posted = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"})
        assert posted.status_code == 401

        right = client.post(
            "/mcp",
            headers={
                "Authorization": "Bearer test-token",
                "Accept": "application/json, text/event-stream",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0"},
                },
            },
        )
        assert right.status_code == 200
        assert right.json()["result"]["serverInfo"]["name"] == "Minimax"


def test_tokens_match_uses_compare_digest_without_length_leak():
    assert tokens_match("test-token", "test-token") is True
    assert tokens_match("test-token", "test-token-longer") is False
    assert tokens_match("", "test-token") is False


def test_http_startup_refuses_missing_or_empty_token(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.delenv("MCP_SERVER_TOKEN", raising=False)
    monkeypatch.setattr(http_transport.uvicorn, "run", lambda *args, **kwargs: pytest.fail("bound"))
    with pytest.raises(SystemExit, match="MCP_SERVER_TOKEN"):
        server.main([])

    monkeypatch.setenv("MCP_SERVER_TOKEN", "   ")
    with pytest.raises(SystemExit, match="MCP_SERVER_TOKEN"):
        server.main([])


def test_stdio_main_ignores_http_token_requirement(monkeypatch):
    monkeypatch.delenv("MCP_SERVER_TOKEN", raising=False)
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    monkeypatch.setenv("MINIMAX_MCP_REMOTE_HTTP", "1")
    called = {}
    monkeypatch.setattr(server.mcp, "run", lambda: called.setdefault("ran", True))
    server.main([])
    assert called["ran"] is True
    assert os.environ.get(ENV_MCP_REMOTE_HTTP) is None


def test_transport_flag_overrides_env(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    assert resolve_transport([]) == "http"
    assert resolve_transport(["--transport", "stdio"]) == "stdio"
    assert resolve_transport(["--transport", "http"]) == "http"
    with pytest.raises(SystemExit, match="Unsupported MCP_TRANSPORT"):
        monkeypatch.setenv("MCP_TRANSPORT", "sse")
        resolve_transport([])


def test_allowlist_default_custom_and_unknown(monkeypatch):
    monkeypatch.delenv("MINIMAX_MCP_ALLOWED_TOOLS", raising=False)
    assert resolve_http_allowlist() == HTTP_TOOL_NAMES
    assert "play_audio" not in resolve_http_allowlist()

    monkeypatch.setenv("MINIMAX_MCP_ALLOWED_TOOLS", " list_voices, text_to_audio ")
    assert resolve_http_allowlist() == {"list_voices", "text_to_audio"}

    monkeypatch.setenv("MINIMAX_MCP_ALLOWED_TOOLS", "text_to_audio,not_a_real_tool")
    with pytest.raises(SystemExit, match="not_a_real_tool"):
        resolve_http_allowlist()

    monkeypatch.setenv("MINIMAX_MCP_ALLOWED_TOOLS", " , ")
    with pytest.raises(SystemExit, match="empty"):
        resolve_http_allowlist()


def test_http_tools_list_is_the_allowlist(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_TOKEN", "test-token")
    monkeypatch.delenv("MINIMAX_MCP_ALLOWED_TOOLS", raising=False)
    app, _port = prepare_http_runtime()
    names = _tools_over_http(app, "test-token")
    assert names == HTTP_TOOL_NAMES

    monkeypatch.setenv("MINIMAX_MCP_ALLOWED_TOOLS", "list_voices")
    app, _port = prepare_http_runtime()
    assert _tools_over_http(app, "test-token") == {"list_voices"}


def _tools_over_http(app, token: str) -> set[str]:
    port = _free_port()
    config = http_transport.uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    uv_server = _QuietServer(config)
    thread = threading.Thread(target=uv_server.run, daemon=True)
    thread.start()
    try:
        _wait_until_ready(port)
        return anyio.run(_list_tools, port, token)
    finally:
        uv_server.should_exit = True
        thread.join(timeout=5)


class _QuietServer(http_transport.uvicorn.Server):
    def install_signal_handlers(self):
        return None


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_ready(port: int) -> None:
    import time
    import urllib.request

    last_error = None
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=0.2) as response:
                if response.status == 200:
                    return
        except Exception as exc:
            last_error = exc
            time.sleep(0.05)
    raise RuntimeError(f"HTTP server did not become ready: {last_error}")


async def _list_tools(port: int, token: str) -> set[str]:
    http_client = httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"})
    transport = streamable_http_client(
        f"http://127.0.0.1:{port}/mcp",
        http_client=http_client,
        terminate_on_close=False,
    )
    try:
        async with Client(transport, raise_exceptions=True) as client:
            result = await client.list_tools()
            return {tool.name for tool in result.tools}
    finally:
        await http_client.aclose()


def test_remote_mode_overrides_local_resource_mode(monkeypatch, capsys):
    monkeypatch.setenv("MINIMAX_API_RESOURCE_MODE", "local")
    server.resource_mode = "local"
    server.apply_remote_http_safety()
    assert server.resource_mode == "url"
    assert os.environ[ENV_MCP_REMOTE_HTTP] == "1"
    warning = capsys.readouterr().err
    assert "MINIMAX_API_RESOURCE_MODE" in warning
    assert "url" in warning
    assert "test-api-key" not in warning


def test_remote_mode_rejects_local_paths_and_ignores_output_directory(monkeypatch, tmp_path):
    server.apply_remote_http_safety()

    def fail_exists(path):
        raise AssertionError(f"filesystem probed: {path}")

    monkeypatch.setattr(server.os.path, "exists", fail_exists)
    audio = tmp_path / "clip.mp3"
    audio.write_bytes(b"ID3")
    image = tmp_path / "frame.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    voice = server.voice_clone(
        "voice-1",
        str(audio),
        "hello",
        output_directory=str(tmp_path),
        is_url=False,
    )
    assert "not allowed" in voice.text.lower()
    assert "http" in voice.text.lower()

    video = server.generate_video(
        prompt="a cat",
        first_frame_image=str(image),
        output_directory=str(tmp_path / "out"),
        async_mode=True,
    )
    assert "not allowed" in video.text.lower()
    assert set(tmp_path.iterdir()) == {audio, image}


def test_remote_mode_accepts_https_and_data_urls(monkeypatch, tmp_path):
    server.apply_remote_http_safety()
    seen = {}

    def fake_post(path, **kwargs):
        seen.setdefault("calls", []).append(path)
        if path == "/v1/files/upload":
            assert kwargs["files"]["file"][1].read() == b"ID3fake"
            return {"file": {"file_id": "file-1"}}
        if path == "/v1/voice_clone":
            assert kwargs["json"]["model"] == "speech-2.8-hd"
            return {"demo_audio": "https://cdn.example/demo.mp3"}
        if path == "/v1/video_generation":
            seen["image"] = kwargs["json"]["first_frame_image"]
            return {"task_id": "task-1"}
        raise AssertionError(path)

    monkeypatch.setattr(server.api_client, "post", fake_post)

    def fake_fetch(url):
        assert url == "https://example.com/sample.mp3"
        return b"ID3fake"

    monkeypatch.setattr(server, "fetch_public_url", fake_fetch)

    voice = server.voice_clone(
        "voice-1",
        "https://example.com/sample.mp3",
        "hello there",
        output_directory=str(tmp_path / "should-not-be-created"),
    )
    assert "https://cdn.example/demo.mp3" in voice.text
    assert not (tmp_path / "should-not-be-created").exists()

    payload = "data:audio/mpeg;base64," + __import__("base64").b64encode(b"ID3fake").decode()
    data_voice = server.voice_clone("voice-2", payload, "hello there", output_directory="/tmp")
    assert "https://cdn.example/demo.mp3" in data_voice.text

    video = server.generate_video(
        prompt="a cat",
        first_frame_image="https://example.com/frame.jpg",
        output_directory=str(tmp_path),
        async_mode=True,
    )
    assert seen["image"] == "https://example.com/frame.jpg"
    assert "task-1" in video.text

    data_image = "data:image/png;base64," + __import__("base64").b64encode(b"png").decode()
    server.generate_video(
        prompt="a cat",
        first_frame_image=data_image,
        async_mode=True,
    )
    assert seen["image"] == data_image


def test_remote_blocks_utils_that_touch_the_filesystem(monkeypatch, tmp_path):
    monkeypatch.setenv(ENV_MCP_REMOTE_HTTP, "1")
    with pytest.raises(MinimaxMcpError, match="remote HTTP"):
        build_output_path(str(tmp_path / "out"))
    assert not (tmp_path / "out").exists()
    with pytest.raises(MinimaxMcpError, match="remote HTTP"):
        process_input_file(str(tmp_path / "clip.mp3"))
    with pytest.raises(ValueError, match="remote HTTP"):
        play(b"not-audio")


def test_model_defaults_follow_env(monkeypatch):
    monkeypatch.delenv("MINIMAX_DEFAULT_SPEECH_MODEL", raising=False)
    monkeypatch.delenv("MINIMAX_DEFAULT_T2V_MODEL", raising=False)
    monkeypatch.delenv("MINIMAX_DEFAULT_T2I_MODEL", raising=False)
    assert configured_speech_model() == "speech-2.8-hd"
    assert configured_t2v_model() == "MiniMax-Hailuo-2.3"
    assert configured_t2i_model() == "image-01"

    monkeypatch.setenv("MINIMAX_DEFAULT_SPEECH_MODEL", "speech-2.8-turbo")
    monkeypatch.setenv("MINIMAX_DEFAULT_T2V_MODEL", "MiniMax-Hailuo-02")
    monkeypatch.setenv("MINIMAX_DEFAULT_T2I_MODEL", "image-01-live")
    assert configured_speech_model() == "speech-2.8-turbo"
    assert configured_t2v_model() == "MiniMax-Hailuo-02"
    assert configured_t2i_model() == "image-01-live"

    seen = {}

    def fake_post(path, **kwargs):
        seen["model"] = kwargs["json"]["model"]
        return {"data": {"audio": "https://cdn.example/a.mp3"}}

    monkeypatch.setattr(server.api_client, "post", fake_post)
    result = server.text_to_audio("hello")
    assert seen["model"] == "speech-2.8-turbo"
    assert "https://cdn.example/a.mp3" in result.text
