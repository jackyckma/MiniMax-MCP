![export](https://github.com/MiniMax-AI/MiniMax-01/raw/main/figures/MiniMaxLogo-Light.png)

<div align="center" style="line-height: 1;">
  <a href="https://www.minimax.io" target="_blank" style="margin: 2px; color: var(--fgColor-default);">
    <img alt="Homepage" src="https://img.shields.io/badge/_Homepage-MiniMax-FF4040?style=flat-square&labelColor=2C3E50&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSIwIDAgNDkwLjE2IDQxMS43Ij48ZGVmcz48c3R5bGU+LmNscy0xe2ZpbGw6I2ZmZjt9PC9zdHlsZT48L2RlZnM+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMjMzLjQ1LDQwLjgxYTE3LjU1LDE3LjU1LDAsMSwwLTM1LjEsMFYzMzEuNTZhNDAuODIsNDAuODIsMCwwLDEtODEuNjMsMFYxNDVhMTcuNTUsMTcuNTUsMCwxLDAtMzUuMDksMHY3OS4wNmE0MC44Miw0MC44MiwwLDAsMS04MS42MywwVjE5NS40MmExMS42MywxMS42MywwLDAsMSwyMy4yNiwwdjI4LjY2YTE3LjU1LDE3LjU1LDAsMCwwLDM1LjEsMFYxNDVBNDAuODIsNDAuODIsMCwwLDEsMTQwLDE0NVYzMzEuNTZhMTcuNTUsMTcuNTUsMCwwLDAsMzUuMSwwVjIxNy41aDBWNDAuODFhNDAuODEsNDAuODEsMCwxLDEsODEuNjIsMFYyODEuNTZhMTEuNjMsMTEuNjMsMCwxLDEtMjMuMjYsMFptMjE1LjksNjMuNEE0MC44Niw0MC44NiwwLDAsMCw0MDguNTMsMTQ1VjMwMC44NWExNy41NSwxNy41NSwwLDAsMS0zNS4wOSwwdi0yNjBhNDAuODIsNDAuODIsMCwwLDAtODEuNjMsMFYzNzAuODlhMTcuNTUsMTcuNTUsMCwwLDEtMzUuMSwwVjMzMGExMS42MywxMS42MywwLDEsMC0yMy4yNiwwdjQwLjg2YTQwLjgxLDQwLjgxLDAsMCwwLDgxLjYyLDBWNDAuODFhMTcuNTUsMTcuNTUsMCwwLDEsMzUuMSwwdjI2MGE0MC44Miw0MC44MiwwLDAsMCw4MS42MywwVjE0NWExNy41NSwxNy41NSwwLDEsMSwzNS4xLDBWMjgxLjU2YTExLjYzLDExLjYzLDAsMCwwLDIzLjI2LDBWMTQ1QTQwLjg1LDQwLjg1LDAsMCwwLDQ0OS4zNSwxMDQuMjFaIi8+PC9zdmc+&logoWidth=20" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://arxiv.org/abs/2501.08313" target="_blank" style="margin: 2px;">
    <img alt="Paper" src="https://img.shields.io/badge/📖_Paper-MiniMax--01-FF4040?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
  </a>
   <a href="https://chat.minimax.io/" target="_blank" style="margin: 2px;">
    <img alt="Chat" src="https://img.shields.io/badge/_MiniMax_Chat-FF4040?style=flat-square&labelColor=2C3E50&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSIwIDAgNDkwLjE2IDQxMS43Ij48ZGVmcz48c3R5bGU+LmNscy0xe2ZpbGw6I2ZmZjt9PC9zdHlsZT48L2RlZnM+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMjMzLjQ1LDQwLjgxYTE3LjU1LDE3LjU1LDAsMSwwLTM1LjEsMFYzMzEuNTZhNDAuODIsNDAuODIsMCwwLDEtODEuNjMsMFYxNDVhMTcuNTUsMTcuNTUsMCwxLDAtMzUuMDksMHY3OS4wNmE0MC44Miw0MC44MiwwLDAsMS04MS42MywwVjE5NS40MmExMS42MywxMS42MywwLDAsMSwyMy4yNiwwdjI4LjY2YTE3LjU1LDE3LjU1LDAsMCwwLDM1LjEsMFYxNDVBNDAuODIsNDAuODIsMCwwLDEsMTQwLDE0NVYzMzEuNTZhMTcuNTUsMTcuNTUsMCwwLDAsMzUuMSwwVjIxNy41aDBWNDAuODFhNDAuODEsNDAuODEsMCwxLDEsODEuNjIsMFYyODEuNTZhMTEuNjMsMTEuNjMsMCwxLDEtMjMuMjYsMFptMjE1LjksNjMuNEE0MC44Niw0MC44NiwwLDAsMCw0MDguNTMsMTQ1VjMwMC44NWExNy41NSwxNy41NSwwLDAsMS0zNS4wOSwwdi0yNjBhNDAuODIsNDAuODIsMCwwLDAtODEuNjMsMFYzNzAuODlhMTcuNTUsMTcuNTUsMCwwLDEtMzUuMSwwVjMzMGExMS42MywxMS42MywwLDEsMC0yMy4yNiwwdjQwLjg2YTQwLjgxLDQwLjgxLDAsMCwwLDgxLjYyLDBWNDAuODFhMTcuNTUsMTcuNTUsMCwwLDEsMzUuMSwwdjI2MGE0MC44Miw0MC44MiwwLDAsMCw4MS42MywwVjE0NWExNy41NSwxNy41NSwwLDEsMSwzNS4xLDBWMjgxLjU2YTExLjYzLDExLjYzLDAsMCwwLDIzLjI2LDBWMTQ1QTQwLjg1LDQwLjg1LDAsMCwwLDQ0OS4zNSwxMDQuMjFaIi8+PC9zdmc+&logoWidth=20" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://www.minimax.io/platform" style="margin: 2px;">
    <img alt="API" src="https://img.shields.io/badge/⚡_API-Platform-FF4040?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
  </a>  
</div>
<div align="center" style="line-height: 1;">
  <a href="https://huggingface.co/MiniMaxAI" target="_blank" style="margin: 2px;">
    <img alt="Hugging Face" src="https://img.shields.io/badge/🤗_Hugging_Face-MiniMax-FF4040?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://github.com/MiniMax-AI/MiniMax-AI.github.io/blob/main/images/wechat-qrcode.jpeg" target="_blank" style="margin: 2px;">
    <img alt="WeChat" src="https://img.shields.io/badge/_WeChat-MiniMax-FF4040?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://www.modelscope.cn/organization/MiniMax" target="_blank" style="margin: 2px;">
    <img alt="ModelScope" src="https://img.shields.io/badge/_ModelScope-MiniMax-FF4040?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>
<div align="center" style="line-height: 1;">
   <a href="https://github.com/MiniMax-AI/MiniMax-MCP/blob/main/LICENSE" style="margin: 2px;">
    <img alt="Code License" src="https://img.shields.io/badge/_Code_License-MIT-FF4040?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>

<p align="center">
  Official MiniMax Model Context Protocol (MCP) server that enables interaction with powerful Text to Speech and video/image generation APIs. This server allows MCP clients like <a href="https://www.anthropic.com/claude">Claude Desktop</a>, <a href="https://www.cursor.so">Cursor</a>, <a href="https://codeium.com/windsurf">Windsurf</a>, <a href="https://github.com/openai/openai-agents-python">OpenAI Agents</a> and others to generate speech, clone voices, generate video, generate image and more.
</p>

> 💡 Recommended: **[MiniMax CLI (mmx-cli)](https://github.com/MiniMax-AI/cli)** — our official command-line tool with the latest models and additional features including text, vision, and search. Works as an AI agent skill for Claude Code, Cursor, OpenClaw, etc.

## Documentation
- [中文文档](README-CN.md)
- [MiniMax-MCP-JS](https://github.com/MiniMax-AI/MiniMax-MCP-JS) - Official JavaScript implementation of MiniMax MCP

## Quickstart with MCP Client
1. Get your API key from [MiniMax](https://www.minimax.io/platform/user-center/basic-information/interface-key). 
2. Install `uv` (Python package manager), install with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see the `uv` [repo](https://github.com/astral-sh/uv) for additional install methods.
3. **Important**: The API host and key vary by region and must match; otherwise, you'll encounter an `Invalid API key` error.

|Region| Global  | Mainland  |
|:--|:-----|:-----|
|MINIMAX_API_KEY| go get from [MiniMax Global](https://www.minimax.io/platform/user-center/basic-information/interface-key) | go get from [MiniMax](https://platform.minimaxi.com/user-center/basic-information/interface-key) |
|MINIMAX_API_HOST| https://api.minimax.io | https://api.minimaxi.com |


### Claude Desktop
Go to `Claude > Settings > Developer > Edit Config > claude_desktop_config.json` to include the following:

```
{
  "mcpServers": {
    "MiniMax": {
      "command": "uvx",
      "args": [
        "minimax-mcp",
        "-y"
      ],
      "env": {
        "MINIMAX_API_KEY": "insert-your-api-key-here",
        "MINIMAX_MCP_BASE_PATH": "local-output-dir-path, such as /User/xxx/Desktop",
        "MINIMAX_API_HOST": "api host, https://api.minimax.io | https://api.minimaxi.com",
        "MINIMAX_API_RESOURCE_MODE": "optional, [url|local], url is default, audio/image/video are downloaded locally or provided in URL format"
      }
    }
  }
}

```
⚠️ Warning: The API key needs to match the host. If an error "API Error: invalid api key" occurs, please check your api host:
- Global Host：`https://api.minimax.io`
- Mainland Host：`https://api.minimaxi.com`

If you're using Windows, you will have to enable "Developer Mode" in Claude Desktop to use the MCP server. Click "Help" in the hamburger menu in the top left and select "Enable Developer Mode".


### Cursor
Go to `Cursor -> Preferences -> Cursor Settings -> MCP -> Add new global MCP Server` to add above config.

That's it. Your MCP client can now interact with MiniMax through these tools:

## Transport
`main()` starts **stdio** unless you opt into HTTP. There is no SSE server in this package: the older README described SSE, but the code never selected a transport other than the default `mcp.run()` (stdio).

| | stdio (default) | Streamable HTTP |
|:-----|:-----|:-----|
| How to start | `minimax-mcp` with no extra flags | `MCP_TRANSPORT=http` or `--transport http` |
| Where it runs | Local subprocess (Claude Desktop, Cursor, Windsurf) | Remote container, for example Zeabur |
| Endpoint | stdin / stdout | `http://0.0.0.0:$PORT/mcp` (`PORT` defaults to `8080`) |
| Auth | Process environment | `Authorization: Bearer <MCP_SERVER_TOKEN>` on every request except `GET /health` |
| Files | Local paths or URLs, depending on `MINIMAX_API_RESOURCE_MODE` | http(s) or `data:` URLs only. Local paths and `output_directory` are rejected. Resource mode is forced to `url`. |

## Remote deployment (Zeabur / HTTP)

This mode is for a **remote MCP connector** (Claude custom connector, Cursor, ChatGPT). It speaks [Streamable HTTP](https://modelcontextprotocol.io) at `/mcp`, stateless JSON responses, behind a shared bearer token. The same image does not enable `play_audio` and does not read or write the server filesystem.

### Cost and keys

These tools call MiniMax APIs that **spend money or subscription quota**. Only invoke them when you mean to.

- A **Token Plan / M Plan subscription key is not a pay-as-you-go API key**. They are not interchangeable. Put the subscription key in `MINIMAX_API_KEY` only if you intend to draw down that plan; otherwise use a pay-as-you-go key from the same region as `MINIMAX_API_HOST`.
- Global host: `https://api.minimax.io`. Mainland host: `https://api.minimaxi.com`. A mismatch returns invalid-API-key errors.
- If the API returns status **2061** (`your current token plan not support model` / "model not available on your plan"), the tool result says so and names the `MINIMAX_DEFAULT_*_MODEL` overrides. Docs list models that subscription keys often do **not** include: MiniMax H3, voice design, and rapid voice cloning. Credits / pay-as-you-go cover a wider set.
- **Quota (verified from MiniMax docs on 2026-10-28, not a fixed "N per day" for every non-text model):** text, image, and speech share one Token Plan quota, counted in a **5-hour rolling window and a weekly window**. Video on the current M Plan docs is on the **weekly window only** (no 5-hour window). The public docs do not publish one per-day cap that applies to all non-text models. A search snippet of the Token Plan subscribe page mentioned Hailuo 2.3 video at about **3 clips/day (Max) and 5 clips/day (Ultra)**, with Plus excluding video; that page is client-rendered and those daily counts were **not** in the HTML fetched for this README, so treat them as unverified. The console usage bar is the source of truth.

### Environment variables

Set these on the Zeabur service. Zeabur injects `PORT`. Do not commit values.

| Variable | HTTP mode | Purpose |
|:-----|:-----|:-----|
| `MINIMAX_API_KEY` | Required | MiniMax key. Never logged. Region must match the host. |
| `MINIMAX_API_HOST` | Required | `https://api.minimax.io` (global) or `https://api.minimaxi.com` (mainland). |
| `MCP_SERVER_TOKEN` | Required, non-empty | Bearer secret for `/mcp`. The process refuses to start if this is missing. Generate with `openssl rand -hex 32`. Never logged. |
| `MCP_TRANSPORT` | `http` | The Docker image sets this. Unset or `stdio` keeps the local subprocess behavior. |
| `PORT` | Optional | Listen port. Default `8080`. Zeabur sets it. |
| `MINIMAX_MCP_ALLOWED_TOOLS` | Optional | Comma-separated tool names. Unknown names abort startup. Unset uses the HTTP default below. Ignored in stdio (all tools stay registered). |
| `MINIMAX_DEFAULT_SPEECH_MODEL` | Optional | Default speech model when a call omits `model`. Unset: `speech-2.8-hd`. |
| `MINIMAX_DEFAULT_T2V_MODEL` | Optional | Default text-to-video model. Unset: `MiniMax-Hailuo-2.3`. |
| `MINIMAX_DEFAULT_T2I_MODEL` | Optional | Default text-to-image model. Unset: `image-01`. |
| `MINIMAX_API_RESOURCE_MODE` | Ignored | HTTP mode forces `url` and warns if this is set to anything else. |

`GET /health` returns `200` and `{"status":"ok"}` with no token, for the platform health check.

HTTP default tools (no `play_audio`): `text_to_audio`, `list_voices`, `voice_clone`, `voice_design`, `text_to_image`, `generate_video`, `query_video_generation`.

`voice_clone` `file` and `generate_video` `first_frame_image` accept only `http://`, `https://`, or base64 `data:` URLs. `output_directory` is ignored. `play_audio` is omitted because it reads local files and plays audio on the machine. In remote HTTP mode, `voice_clone` downloads http(s) audio only from globally routable hosts on ports 80 and 443, re-checks up to 3 redirects, stops above 20 MB, and pins the TCP connection to the resolved public IP (TLS SNI and the Host header stay on the original name); this guard does not apply to stdio, does not inspect bytes a public host returns, and does not fetch `generate_video` image URLs itself.

### Models

Checked against [MiniMax model list](https://platform.minimax.io/docs/faq/models) and the [text-to-video API](https://platform.minimax.io/docs/api-reference/video-generation-t2v) on 2026-10-28. This server still calls the existing `/v1/t2a_v2`, `/v1/image_generation`, and `/v1/video_generation` endpoints. It does **not** call the newer H3 video API.

Speech (verified): `speech-2.8-hd` (built-in default), `speech-2.8-turbo`, `speech-2.6-hd`, `speech-2.6-turbo`, `speech-02-hd`, `speech-02-turbo`.

Text-to-video on `/v1/video_generation` (verified enum): `MiniMax-Hailuo-2.3` (built-in default), `MiniMax-Hailuo-02`, `T2V-01-Director`, `T2V-01`.

Also on the model list, not in that text-to-video enum: `MiniMax-Hailuo-2.3-Fast` (described as image-to-video). Whether this server's `/v1/video_generation` call accepts it is **unverified**.

Image (verified): `image-01` (built-in default), `image-01-live` (docs: text plus a reference image; this tool only sends a prompt, so `image-01-live` behavior here is **unverified**).

`MiniMax-H3` and `MiniMax-H3-Max` are on the model list and use a separate video API. Passing them to `generate_video` is **unverified** and Token Plan docs say H3 is not included. Do not point a subscription key at them unless you have confirmed the key.

### Zeabur

1. Push this repo and create a Zeabur service from it. Zeabur uses the `Dockerfile` (`python:3.12-slim`, non-root user, `MCP_TRANSPORT=http`).
2. Set `MINIMAX_API_KEY`, `MINIMAX_API_HOST`, and `MCP_SERVER_TOKEN`. Leave `PORT` to Zeabur.
3. Deploy. The MCP URL is `https://<service>.zeabur.app/mcp`. `https://<service>.zeabur.app/health` should return 200 without a token.

`sounddevice` / `soundfile` (and libportaudio / libsndfile) are an optional `playback` extra. The image does not install them. `play_audio` is not part of the HTTP allowlist; local playback still goes through `ffplay` when you run stdio.

### Claude custom connector

1. In Claude, open **Customize → Connectors → Add custom connector**.
2. Name it and set the remote MCP URL to `https://<service>.zeabur.app/mcp`.
3. Set authentication to **None**. This server does not use OAuth.
4. Under request headers, add `Authorization` with value `Bearer <MCP_SERVER_TOKEN>` (one space after `Bearer`) and mark it required.
5. In a conversation, use **+ → Add connectors** and enable it. Connectors are per conversation.

The request-headers control has been in beta and may be hidden on some accounts.

### Cursor and ChatGPT

Use the same URL and header. In Cursor, add a remote MCP server whose URL is `https://<service>.zeabur.app/mcp` and whose headers include `Authorization: Bearer <MCP_SERVER_TOKEN>`. ChatGPT custom connectors / developer mode should use that Streamable HTTP URL with the same bearer header. This server does not implement OAuth; if a client can only do OAuth, it cannot connect until that client accepts a static bearer header.

## Available Tools
| tool  | description  |
|-|-|
|`text_to_audio`|Convert text to audio with a given voice|
|`list_voices`|List all voices available|
|`voice_clone`|Clone a voice using provided audio files|
|`generate_video`|Generate a video from a prompt|
|`text_to_image`|Generate a image from a prompt|
|`query_video_generation`|Query the result of video generation task|
|`voice_design`|Generate a voice from a prompt using preview text|

## Release Notes

### July 2, 2025

#### 🆕 What's New
- **Voice Design**: New `voice_design` tool - create custom voices from descriptive prompts with preview audio
- **Video Enhancement**: Added `MiniMax-Hailuo-02` model with ultra-clear quality and duration/resolution controls  

#### 📈 Enhanced Tools
- `voice_design` - Generate personalized voices from text descriptions
- `generate_video` - Now supports MiniMax-Hailuo-02 with 6s/10s duration and 768P/1080P resolution options

## FAQ
### 1. invalid api key
Please ensure your API key and API host are regionally aligned
|Region| Global  | Mainland  |
|:--|:-----|:-----|
|MINIMAX_API_KEY| go get from [MiniMax Global](https://www.minimax.io/platform/user-center/basic-information/interface-key) | go get from [MiniMax](https://platform.minimaxi.com/user-center/basic-information/interface-key) |
|MINIMAX_API_HOST| https://api.minimax.io | https://api.minimaxi.com |

### 2. spawn uvx ENOENT
Please confirm its absolute path by running this command in your terminal:
```sh
which uvx
```
Once you obtain the absolute path (e.g., /usr/local/bin/uvx), update your configuration to use that path (e.g., "command": "/usr/local/bin/uvx"). 

### 3. How to use `generate_video` in async-mode
Define completion rules before starting:
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/cursor_rule2.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle;"/>
Alternatively, these rules can be configured in your IDE settings (e.g., Cursor):
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/cursor_video_rule.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle;"/>


## Example usage

⚠️ Warning: Using these tools may incur costs.

### 1. broadcast a segment of the evening news
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/Snipaste_2025-04-09_20-07-53.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle;"/>

### 2. clone a voice
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/Snipaste_2025-04-09_19-45-13.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle;"/>

### 3. generate a video
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/Snipaste_2025-04-09_19-58-52.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle;"/>
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/Snipaste_2025-04-09_19-59-43.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle; "/>

### 4. generate images
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/gen_image.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle;"/>
<img src="https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/gen_image1.png?x-oss-process=image/resize,p_50/format,webp" style="display: inline-block; vertical-align: middle; "/>
