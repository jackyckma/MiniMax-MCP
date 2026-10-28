"""Streamable HTTP transport for remote deployment (Zeabur and similar).

Stdio stays the default. This module is only used when MCP_TRANSPORT=http
or --transport http is selected. The bearer token and the MiniMax API key
are never logged.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import sys

import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse
from starlette.types import Receive, Scope, Send

from minimax_mcp.const import (
    ENV_MCP_ALLOWED_TOOLS,
    ENV_MCP_SERVER_TOKEN,
    ENV_MCP_TRANSPORT,
    ENV_MINIMAX_API_HOST,
    ENV_MINIMAX_API_KEY,
)
from minimax_mcp.server import (
    HTTP_DEFAULT_ALLOWLIST,
    _REGISTERED_TOOLS,
    apply_remote_http_safety,
    fastmcp_log_level,
)


def resolve_transport(argv: list[str] | None = None) -> str:
    """Return 'stdio' or 'http'. CLI --transport wins over MCP_TRANSPORT."""
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=None,
        help="MCP transport. stdio (default) or http (Streamable HTTP).",
    )
    args, _unknown = parser.parse_known_args(argv)
    if args.transport:
        return args.transport
    raw = os.getenv(ENV_MCP_TRANSPORT, "stdio")
    value = raw.strip().lower()
    if value in {"", "stdio"}:
        return "stdio"
    if value in {"http", "streamable-http", "streamable_http"}:
        return "http"
    raise SystemExit(
        f"Unsupported MCP_TRANSPORT={raw!r}. Use 'stdio' (default) or 'http'. "
        "SSE is not implemented."
    )


def require_mcp_server_token() -> str:
    token = os.getenv(ENV_MCP_SERVER_TOKEN)
    if token is None or token.strip() == "":
        raise SystemExit(
            "MCP_SERVER_TOKEN is required when MCP_TRANSPORT=http (or --transport http) "
            "and must be a non-empty secret. Refusing to start so /mcp is not public."
        )
    return token.strip()


def require_minimax_credentials() -> None:
    if not os.getenv(ENV_MINIMAX_API_KEY, "").strip():
        raise SystemExit(
            "MINIMAX_API_KEY environment variable is required. "
            "Use a pay-as-you-go key or a Token Plan subscription key, and do not log it."
        )
    host = os.getenv(ENV_MINIMAX_API_HOST, "").strip()
    if not host:
        raise SystemExit(
            "MINIMAX_API_HOST environment variable is required. "
            "Use https://api.minimax.io for a global key or https://api.minimaxi.com for a "
            "mainland key. The key and host region must match."
        )


def resolve_port() -> int:
    raw = os.environ.get("PORT", "8080")
    try:
        port = int(raw)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"PORT must be an integer, got {raw!r}.") from exc
    if not 1 <= port <= 65535:
        raise SystemExit(f"PORT must be between 1 and 65535, got {port}.")
    return port


def known_tool_names() -> list[str]:
    return [name for name, _description, _fn in _REGISTERED_TOOLS]


def resolve_http_allowlist() -> set[str]:
    """Tools registered in HTTP mode. Unknown names fail startup."""
    known = known_tool_names()
    known_set = set(known)
    missing_defaults = sorted(HTTP_DEFAULT_ALLOWLIST - known_set)
    if missing_defaults:
        raise SystemExit(
            "Internal error: HTTP default allowlist names are not registered tools: "
            + ", ".join(missing_defaults)
        )
    raw = os.getenv(ENV_MCP_ALLOWED_TOOLS)
    if raw is None or raw.strip() == "":
        return set(HTTP_DEFAULT_ALLOWLIST)
    names = [part.strip() for part in raw.split(",") if part.strip()]
    if not names:
        raise SystemExit(
            "MINIMAX_MCP_ALLOWED_TOOLS is empty. Unset it to use the default HTTP "
            "allowlist, or pass a comma-separated list of known tool names."
        )
    unknown = [name for name in names if name not in known_set]
    if unknown:
        raise SystemExit(
            "Unknown tool name(s) in MINIMAX_MCP_ALLOWED_TOOLS: "
            + ", ".join(unknown)
            + ". Known tools: "
            + ", ".join(known)
            + "."
        )
    return set(names)


def tokens_match(provided: str, expected: str) -> bool:
    """Constant-time comparison that does not leak the secret length."""
    provided_digest = hashlib.sha256(provided.encode("utf-8")).digest()
    expected_digest = hashlib.sha256(expected.encode("utf-8")).digest()
    return hmac.compare_digest(provided_digest, expected_digest)


def _authorization_header(scope: Scope) -> str:
    for key, value in scope.get("headers") or []:
        if key.lower() == b"authorization":
            try:
                return value.decode("latin-1")
            except UnicodeError:
                return ""
    return ""


def _bearer_token(header: str) -> str:
    parts = header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return ""
    return parts[1].strip()


class BearerAuthMiddleware:
    """Require Authorization: Bearer <MCP_SERVER_TOKEN> except on /health."""

    def __init__(self, app, token: str):
        self.app = app
        self._token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path") or ""
        if path.rstrip("/") == "/health":
            await self.app(scope, receive, send)
            return
        provided = _bearer_token(_authorization_header(scope))
        if not self._token or not provided or not tokens_match(provided, self._token):
            await _send_unauthorized(send)
            return
        await self.app(scope, receive, send)


async def _send_unauthorized(send: Send) -> None:
    body = b'{"error":"unauthorized"}'
    await send(
        {
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


def build_http_app(token: str, allowed: set[str]):
    http_mcp = MCPServer("Minimax", log_level=fastmcp_log_level)
    for name, description, fn in _REGISTERED_TOOLS:
        if name not in allowed:
            continue
        http_mcp.tool(description=description)(fn)

    @http_mcp.custom_route("/health", methods=["GET"])
    async def health(_request):
        return JSONResponse({"status": "ok"})

    app = http_mcp.streamable_http_app(
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
        host="0.0.0.0",
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        ),
    )
    return BearerAuthMiddleware(app, token)


def prepare_http_runtime():
    """Validate env, force URL resource mode, and build the ASGI app."""
    require_minimax_credentials()
    token = require_mcp_server_token()
    apply_remote_http_safety()
    allowed = resolve_http_allowlist()
    return build_http_app(token, allowed), resolve_port()


def run_http() -> None:
    app, port = prepare_http_runtime()
    # Do not include MCP_SERVER_TOKEN or MINIMAX_API_KEY in this line.
    print(
        f"Starting Minimax MCP server (streamable-http) on 0.0.0.0:{port}/mcp",
        file=sys.stderr,
    )
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
