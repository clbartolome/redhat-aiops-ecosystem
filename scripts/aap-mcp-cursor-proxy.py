#!/usr/bin/env python3
"""Stdio MCP proxy for Ansible AAP Streamable HTTP MCP.

Cursor silently drops very large tools/list payloads (~200KB from AAP).
This proxy forwards all MCP traffic and replaces tools/list schemas with a
minimal stub so tools register in the IDE; tool calls still hit the real server.
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://ansible-mcp-aap.apps.ocp.zaskan.es/mcp/"
MAX_DESC = 200
DEFAULT_ENV_FILE = os.path.expanduser("~/.config/cursor/aap-mcp.env")


def _load_env_file(path: str) -> None:
    try:
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if key and key not in os.environ:
                    os.environ[key] = value.strip()
    except OSError:
        return


def _ensure_config() -> None:
    env_file = os.environ.get("AAP_MCP_ENV_FILE", DEFAULT_ENV_FILE)
    _load_env_file(env_file)
    legacy = os.path.expanduser("~/.config/environment.d/aap-mcp.conf")
    if legacy != env_file:
        _load_env_file(legacy)
    ca_legacy = os.path.expanduser("~/.config/environment.d/cursor-ocp-ca.conf")
    _load_env_file(ca_legacy)


def _ssl_context() -> ssl.SSLContext:
    ca = os.environ.get("NODE_EXTRA_CA_CERTS") or os.environ.get("AAP_MCP_CA_FILE")
    if ca and os.path.isfile(ca):
        return ssl.create_default_context(cafile=ca)
    if os.environ.get("AAP_MCP_INSECURE", "").lower() in ("1", "true", "yes"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return ssl.create_default_context()


def _parse_sse_body(raw: bytes) -> dict:
    text = raw.decode("utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload:
                return json.loads(payload)
    return json.loads(text)


def _post(url: str, token: str, body: dict, session_id: str | None) -> tuple[dict, str | None]:
    data = json.dumps(body).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=120) as resp:
        sid = resp.headers.get("Mcp-Session-Id") or session_id
        return _parse_sse_body(resp.read()), sid


def _slim_tools_list(response: dict) -> dict:
    tools = response.get("result", {}).get("tools")
    if not isinstance(tools, list):
        return response
    response = json.loads(json.dumps(response))
    response["result"]["tools"] = [
        {
            "name": t.get("name", ""),
            "description": (t.get("description") or "")[:MAX_DESC],
            "inputSchema": {"type": "object"},
        }
        for t in tools
        if t.get("name")
    ]
    return response


def main() -> int:
    _ensure_config()
    url = os.environ.get("AAP_MCP_URL", DEFAULT_URL).rstrip("/") + "/"
    token = os.environ.get("AAP_MCP_TOKEN", "").strip()
    if not token:
        print("AAP_MCP_TOKEN is required", file=sys.stderr)
        return 1

    session_id: str | None = None
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        if msg.get("id") is None:
            try:
                _, session_id = _post(url, token, msg, session_id)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                pass
            continue

        try:
            response, session_id = _post(url, token, msg, session_id)
            if msg.get("method") == "tools/list":
                response = _slim_tools_list(response)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as exc:  # noqa: BLE001 — return JSON-RPC error to Cursor
            err = {
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "error": {"code": -32603, "message": str(exc)},
            }
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    sys.exit(main())
