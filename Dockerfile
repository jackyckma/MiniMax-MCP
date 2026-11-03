FROM python:3.12-slim
LABEL "language"="python"
WORKDIR /src
COPY . .
RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin mcp
USER mcp
EXPOSE 8080
ENV MCP_TRANSPORT=http
CMD ["python", "-m", "minimax_mcp.server"]
